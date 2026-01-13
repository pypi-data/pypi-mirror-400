import time
import random
import logging
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from mp_btp.models.database import SessionLocal
from mp_btp.models import Deployment, DeploymentReplica, Account, KymaRuntime, CFOrg
from mp_btp.integrations.kyma import download_kubeconfig, kyma_deploy, kyma_deploy_raw_yaml, kyma_login, check_deployment_ready, get_service_url, kyma_login_cached, mark_logged_in
from mp_btp.integrations.cf import cf_login, cf_target, cf_push
from mp_btp.integrations.btp_cli import BTPClient
from mp_btp.integrations.tool_manager import ensure_tools
from mp_btp.utils.audit import log_operation, OP_DEPLOY_CREATE, OP_REPLICA_START, OP_REPLICA_STOP
from mp_btp.config import get_config
logger = logging.getLogger(__name__)
config = get_config()
def build_deploy_info(deployment: Deployment, replica: DeploymentReplica, account: Account, runtime) -> dict:
    email_prefix = account.email.split('@')[0] if account.email else ''
    runtime_type = 'kym' if replica.runtime_type == 'kyma' else 'cf'
    deploy_name = deployment.name or str(deployment.id)[:8]
    res_id = f"{runtime_type}:{email_prefix}:{deploy_name}"
    info = {
        "deployment_id": str(deployment.id),
        "deployment_name": deploy_name,
        "image": deployment.image,
        "account_email": account.email,
        "account_subdomain": account.subdomain,
        "runtime_type": replica.runtime_type,
        "replica_index": replica.replica_index,
        "deploy_time": datetime.now(timezone.utc).isoformat(),
        "memory_mb": deployment.memory_mb,
        "project": deployment.project,
        "res_id": res_id,
    }
    if hasattr(runtime, 'cluster_name'):
        info["cluster_name"] = runtime.cluster_name
    if hasattr(runtime, 'org_name'):
        info["org_name"] = runtime.org_name
    if deployment.expires_at:
        info["expires_at"] = deployment.expires_at.isoformat()
    return info
def inject_deploy_env(env_vars: dict, deploy_info: dict, ext_info: str = None) -> dict:
    env = dict(env_vars) if env_vars else {}
    env['RES_ID'] = deploy_info['res_id']
    sys_ext = f"img={deploy_info['image']},mem={deploy_info['memory_mb']}M"
    if ext_info:
        env['EXT_INFO'] = f"{sys_ext},{ext_info}"
    else:
        env['EXT_INFO'] = sys_ext
    env['BTP_DEPLOY_INFO'] = json.dumps(deploy_info)
    return env
_tools_ready = False
def _ensure_tools_once():
    global _tools_ready
    if not _tools_ready:
        results = ensure_tools(["btp", "kubectl", "kubelogin", "cf"])
        logger.info(f"Tools check: {results}")
        _tools_ready = True
def get_multi_node_client():
    mn_config = config.get("multi_node", {})
    if not mn_config.get("enabled"):
        return None
    url = os.environ.get("MULTI_NODE_API_URL") or mn_config.get("url")
    token = os.environ.get("MULTI_NODE_API_TOKEN") or mn_config.get("token")
    if not url:
        return None
    from integrations.multi_node import MultiNodeClient
    return MultiNodeClient(url, token=token, timeout=mn_config.get("timeout", 300))
def get_proxy_for_account(account):
    from integrations.proxy_pool import get_proxy_pool
    pool = get_proxy_pool()
    if not pool:
        return None
    return pool.get_proxy_for_account(account)
def wait_for_kyma_ready(account: Account, runtime: KymaRuntime, db: Session, timeout: int = 1800) -> bool:
    start = time.time()
    client = BTPClient(account.email, account.email, account.password)
    while time.time() - start < timeout:
        if not client.login():
            time.sleep(30)
            continue
        subaccount_id = account.subaccount_id or client.get_subaccount_id()
        if not subaccount_id:
            time.sleep(30)
            continue
        kyma = client.get_kyma_instance(subaccount_id)
        if kyma:
            state = kyma.get("state")
            if state == "OK":
                runtime.instance_id = kyma.get("id")
                runtime.cluster_name = kyma.get("name")
                runtime.status = "OK"
                runtime.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
                db.commit()
                logger.info(f"Kyma {runtime.cluster_name} is ready")
                return True
            elif state == "FAILED":
                runtime.status = "FAILED"
                runtime.failed_count = (runtime.failed_count or 0) + 1
                db.commit()
                logger.error(f"Kyma creation failed for {account.email}")
                return False
        logger.info(f"Kyma still creating, waiting... ({int(time.time() - start)}s)")
        time.sleep(30)
    logger.error(f"Kyma creation timeout after {timeout}s")
    return False
def execute_deployment(deployment_id: str):
    _ensure_tools_once()
    db = SessionLocal()
    try:
        deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
        if not deployment:
            logger.error(f"Deployment {deployment_id} not found")
            return
        delay_config = config.get("deployment", {}).get("delay", {})
        delay = random.randint(delay_config.get("single_min", 5), delay_config.get("single_max", 30))
        logger.info(f"Deployment {deployment_id}: waiting {delay}s")
        time.sleep(delay)
        mock_mode = config.get("deployment", {}).get("mock", True)
        use_multi_node = config.get("deployment", {}).get("use_multi_node", False)
        success_count = 0
        for replica in deployment.replicas_list:
            try:
                if mock_mode:
                    execute_replica_mock(db, deployment, replica)
                elif use_multi_node:
                    execute_replica_multi_node(db, deployment, replica)
                elif replica.runtime_type == "kyma":
                    execute_replica_kyma(db, deployment, replica)
                else:
                    execute_replica_cf(db, deployment, replica)
                success_count += 1
                log_operation(OP_REPLICA_START, "SUCCESS", 
                    account_id=str(replica.account_id), deployment_id=str(deployment.id),
                    replica_id=str(replica.id), details=f"image={deployment.image}")
            except Exception as e:
                logger.error(f"Replica {replica.replica_index} failed: {e}")
                replica.status = "FAILED"
                db.commit()
                log_operation(OP_REPLICA_START, "FAILED",
                    account_id=str(replica.account_id), deployment_id=str(deployment.id),
                    replica_id=str(replica.id), error_message=str(e))
        deployment.status = "RUNNING" if success_count > 0 else "FAILED"
        db.commit()
        log_operation(OP_DEPLOY_CREATE, deployment.status,
            deployment_id=str(deployment.id), details=f"replicas={success_count}/{len(deployment.replicas_list)}")
        logger.info(f"Deployment {deployment_id}: {success_count}/{len(deployment.replicas_list)} replicas")
    finally:
        db.close()
def execute_replica_mock(db: Session, deployment: Deployment, replica: DeploymentReplica):
    account = db.query(Account).filter(Account.id == replica.account_id).first()
    if not account:
        raise Exception("Account not found")
    if replica.runtime_type == "kyma":
        runtime = db.query(KymaRuntime).filter(KymaRuntime.id == replica.runtime_id).first()
        url = f"https://{replica.container_name}.{runtime.cluster_name or 'kyma'}.ondemand.com"
    else:
        runtime = db.query(CFOrg).filter(CFOrg.id == replica.runtime_id).first()
        region = "unknown"
        if runtime and runtime.api_endpoint:
            parts = runtime.api_endpoint.split('.')
            if len(parts) >= 3:
                region = parts[2]
        url = f"https://{replica.container_name}.cfapps.{region}.hana.ondemand.com"
    replica.status = "RUNNING"
    replica.access_url = url
    replica.started_at = datetime.now(timezone.utc)
    if runtime:
        runtime.memory_used_mb = (runtime.memory_used_mb or 0) + deployment.memory_mb
    db.commit()
def execute_replica_kyma(db: Session, deployment: Deployment, replica: DeploymentReplica):
    account = db.query(Account).filter(Account.id == replica.account_id).first()
    runtime = db.query(KymaRuntime).filter(KymaRuntime.id == replica.runtime_id).first()
    if not account or not runtime:
        raise Exception("Account or runtime not found")
    proxy = get_proxy_for_account(account)
    if proxy:
        logger.info(f"Using proxy {proxy.host}:{proxy.port} for {account.email}")
    if runtime.status == "CREATING":
        logger.info(f"Waiting for Kyma {runtime.cluster_name} to be ready...")
        if not wait_for_kyma_ready(account, runtime, db, timeout=1800):
            raise Exception("Kyma creation timeout or failed")
        db.refresh(runtime)
    if not runtime.instance_id:
        raise Exception("Kyma instance_id not available")
    kubeconfig_path = kyma_login_cached(runtime.instance_id, account.email, account.password, port=8000, kyma_id=str(runtime.id))
    if not kubeconfig_path:
        raise Exception("Kyma login failed")
    try:
        deploy_info = build_deploy_info(deployment, replica, account, runtime)
        ext_info = (deployment.env_vars or {}).get('EXT_INFO')
        injected_env = inject_deploy_env(deployment.env_vars, deploy_info, ext_info)
        if deployment.raw_yaml:
            result = kyma_deploy_raw_yaml(kubeconfig_path, deployment.raw_yaml, namespace="demo")
            if not result['success']:
                raise Exception(f"Deploy failed: {result.get('error')}")
            url = f"https://{deployment.project}.{runtime.cluster_name or 'kyma'}.ondemand.com"
        else:
            result = kyma_deploy(kubeconfig_path, replica.container_name, deployment.image,
                                port=deployment.port, memory_mb=deployment.memory_mb,
                                env_vars=injected_env)
            if not result['success']:
                raise Exception(f"Deploy failed: {result.get('error')}")
            check_deployment_ready(kubeconfig_path, replica.container_name, timeout=180)
            url = get_service_url(kubeconfig_path, replica.container_name) or result.get('url')
        replica.status = "RUNNING"
        replica.access_url = url
        replica.started_at = datetime.now(timezone.utc)
        runtime.memory_used_mb = (runtime.memory_used_mb or 0) + deployment.memory_mb
        db.commit()
    except Exception as e:
        raise
def execute_replica_cf(db: Session, deployment: Deployment, replica: DeploymentReplica):
    account = db.query(Account).filter(Account.id == replica.account_id).first()
    runtime = db.query(CFOrg).filter(CFOrg.id == replica.runtime_id).first()
    if not account or not runtime:
        raise Exception("Account or runtime not found")
    proxy = get_proxy_for_account(account)
    if proxy:
        logger.info(f"Using proxy {proxy.host}:{proxy.port} for {account.email}")
    api = runtime.api_endpoint
    if not api:
        raise Exception("CF api_endpoint not configured, run account verify first")
    if not cf_login(api, account.email, account.password, org=runtime.org_name):
        raise Exception("CF login failed")
    cf_target(runtime.org_name, "dev")
    deploy_info = build_deploy_info(deployment, replica, account, runtime)
    ext_info = (deployment.env_vars or {}).get('EXT_INFO')
    injected_env = inject_deploy_env(deployment.env_vars, deploy_info, ext_info)
    result = cf_push(replica.container_name, deployment.image,
                    memory_mb=deployment.memory_mb,
                    disk_mb=deployment.disk_mb or deployment.memory_mb * 2,
                    env_vars=injected_env)
    if not result['success']:
        raise Exception(f"CF push failed: {result.get('error')}")
    replica.status = "RUNNING"
    replica.access_url = result.get('url')
    replica.started_at = datetime.now(timezone.utc)
    runtime.memory_used_mb = (runtime.memory_used_mb or 0) + deployment.memory_mb
    db.commit()
def execute_replica_multi_node(db: Session, deployment: Deployment, replica: DeploymentReplica):
    client = get_multi_node_client()
    if not client:
        raise Exception("Multi-node API not configured")
    account = db.query(Account).filter(Account.id == replica.account_id).first()
    if not account:
        raise Exception("Account not found")
    node_id = account.preferred_node
    if node_id:
        node = client.get_node(node_id)
        if not node or node.get("status") != "online":
            node_id = None
    if not node_id:
        nodes = client.list_nodes()
        online_nodes = [n for n in nodes if n.get("status") == "online"]
        if not online_nodes:
            raise Exception("No online nodes")
        node_id = random.choice(online_nodes).get("id")
        account.preferred_node = node_id
        db.commit()
        logger.info(f"Account {account.email} bound to node {node_id}")
    replica.assigned_node = node_id
    if replica.runtime_type == "kyma":
        execute_kyma_on_node(client, node_id, db, deployment, replica, account)
    else:
        execute_cf_on_node(client, node_id, db, deployment, replica, account)
def execute_kyma_on_node(client, node_id: str, db: Session, deployment: Deployment, 
                         replica: DeploymentReplica, account: Account):
    runtime = db.query(KymaRuntime).filter(KymaRuntime.id == replica.runtime_id).first()
    if not runtime or not runtime.instance_id:
        raise Exception("Kyma runtime not found")
    result = client.btp_login(node_id, account.email, account.email, account.password)
    if not result.get("success"):
        raise Exception(f"BTP login failed: {result}")
    kubeconfig_url = f"https://kyma-env-broker.cp.kyma.cloud.sap/kubeconfig/{runtime.instance_id}"
    manifest = build_k8s_manifest(replica.container_name, deployment.image, 
                                  deployment.port, deployment.memory_mb, deployment.env_vars)
    result = client.exec_on_node(node_id, cmd, timeout_ms=300000)
    if not result.get("success"):
        raise Exception(f"Kyma deploy failed: {result}")
    output = result.get("output", "")
    url = None
    for line in output.strip().split('\n'):
        if ':' in line and not line.startswith('deployment') and not line.startswith('service'):
            url = f"http://{line.strip()}"
            break
    replica.status = "RUNNING"
    replica.access_url = url
    replica.started_at = datetime.now(timezone.utc)
    runtime.memory_used_mb = (runtime.memory_used_mb or 0) + deployment.memory_mb
    db.commit()
    logger.info(f"Deployed {deployment.image} to Kyma via node {node_id}")
def execute_cf_on_node(client, node_id: str, db: Session, deployment: Deployment,
                       replica: DeploymentReplica, account: Account):
    runtime = db.query(CFOrg).filter(CFOrg.id == replica.runtime_id).first()
    if not runtime:
        raise Exception("CF org not found")
    api = runtime.api_endpoint
    if not api:
        raise Exception("CF api_endpoint not configured")
    result = client.cf_login(node_id, api, account.email, account.password, org=runtime.org_name)
    if not result.get("success"):
        raise Exception(f"CF login failed: {result}")
    result = client.exec_on_node(node_id, cmd, timeout_ms=300000)
    if not result.get("success"):
        raise Exception(f"CF push failed: {result}")
    output = result.get("output", "")
    url = None
    for line in output.strip().split('\n'):
        if '.hana.ondemand.com' in line or '.cfapps.' in line:
            url = f"https://{line.strip()}"
            break
    replica.status = "RUNNING"
    replica.access_url = url
    replica.started_at = datetime.now(timezone.utc)
    runtime.memory_used_mb = (runtime.memory_used_mb or 0) + deployment.memory_mb
    db.commit()
    logger.info(f"Deployed {deployment.image} to CF via node {node_id}")
def build_k8s_manifest(name: str, image: str, port: int, memory_mb: int, env_vars: dict) -> str:
    import yaml
    dep = {
        'apiVersion': 'apps/v1', 'kind': 'Deployment',
        'metadata': {'name': name, 'namespace': 'default'},
        'spec': {
            'replicas': 1, 'selector': {'matchLabels': {'app': name}},
            'template': {
                'metadata': {'labels': {'app': name}},
                'spec': {'containers': [{
                    'name': 'app', 'image': image,
                    'resources': {'requests': {'memory': f'{memory_mb}Mi'}, 'limits': {'memory': f'{memory_mb}Mi'}}
                }]}
            }
        }
    }
    if port:
        dep['spec']['template']['spec']['containers'][0]['ports'] = [{'containerPort': port}]
    if env_vars:
        dep['spec']['template']['spec']['containers'][0]['env'] = [{'name': k, 'value': str(v)} for k, v in env_vars.items()]
    manifests = [dep]
    if port:
        manifests.append({
            'apiVersion': 'v1', 'kind': 'Service',
            'metadata': {'name': name, 'namespace': 'default'},
            'spec': {'selector': {'app': name}, 'ports': [{'port': port, 'targetPort': port}], 'type': 'ClusterIP'}
        })
    return '---\n'.join(yaml.dump(m) for m in manifests)