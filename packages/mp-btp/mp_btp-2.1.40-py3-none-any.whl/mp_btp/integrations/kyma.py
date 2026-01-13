#!/usr/bin/env python3
import asyncio
import subprocess
import time
import os
import socket
import logging
import yaml
from typing import Dict, Optional
logger = logging.getLogger(__name__)
TOOL_PATH = os.environ.get("BTP_TOOL_PATH", "/tmp/tool_cache/bin")
KUBECONFIG_CACHE_DIR = os.environ.get("BTP_KUBECONFIG_CACHE", "/tmp/kubeconfig_cache")
_login_cache = {}
LOGIN_CACHE_TTL = 3600
def _env() -> dict:
    env = os.environ.copy()
    if TOOL_PATH not in env.get('PATH', ''):
        env['PATH'] = f"{TOOL_PATH}:{env.get('PATH', '')}"
    return env
def get_cached_kubeconfig(instance_id: str) -> Optional[str]:
    os.makedirs(KUBECONFIG_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(KUBECONFIG_CACHE_DIR, f"{instance_id}.yaml")
    if os.path.exists(cache_path):
        if time.time() - os.path.getmtime(cache_path) < 3600:
            return cache_path
    return None
def download_kubeconfig(instance_id: str, output_path: str = None, use_cache: bool = True) -> Optional[str]:
    if use_cache:
        cached = get_cached_kubeconfig(instance_id)
        if cached:
            if output_path and output_path != cached:
                import shutil
                shutil.copy(cached, output_path)
                return output_path
            return cached
    os.makedirs(KUBECONFIG_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(KUBECONFIG_CACHE_DIR, f"{instance_id}.yaml")
    target = output_path or cache_path
    url = f"https://kyma-env-broker.cp.kyma.cloud.sap/kubeconfig/{instance_id}"
    try:
        r = subprocess.run(['curl', '-s', url, '-o', target], capture_output=True, timeout=30)
        if r.returncode == 0 and os.path.exists(target):
            with open(target) as f:
                yaml.safe_load(f)
            if target != cache_path:
                import shutil
                shutil.copy(target, cache_path)
            return target
        return None
    except:
        return None
def is_logged_in(instance_id: str) -> bool:
    if instance_id in _login_cache:
        if time.time() - _login_cache[instance_id] < LOGIN_CACHE_TTL:
            return True
    return False
def mark_logged_in(instance_id: str):
    _login_cache[instance_id] = time.time()
def _extract_oidc(kubeconfig_path: str) -> Optional[Dict]:
    try:
        with open(kubeconfig_path) as f:
            cfg = yaml.safe_load(f)
        ctx = cfg.get('current-context')
        for u in cfg.get('users', []):
            if u.get('name') == ctx:
                args = u.get('user', {}).get('exec', {}).get('args', [])
                oidc = {}
                for a in args:
                    if a.startswith('--oidc-issuer-url='):
                        oidc['issuer_url'] = a.split('=', 1)[1]
                    elif a.startswith('--oidc-client-id='):
                        oidc['client_id'] = a.split('=', 1)[1]
                return oidc if oidc else None
        return None
    except:
        return None
def _wait_port(port: int, timeout: int = 10) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect(('127.0.0.1', port))
                return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.5)
    return False
async def _automate_login(url: str, email: str, password: str) -> bool:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed")
        return False
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            logger.info(f"Navigating to: {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as e:
                logger.error(f"Failed to connect to {url}: {e}")
                await browser.close()
                return False
            await asyncio.sleep(1)
            current_url = page.url
            logger.info(f"Page loaded: {current_url[:100]}")
            if "accounts.sap.com" in current_url or "sap.com" in current_url:
                logger.info("On SAP login page, starting automation")
                try:
                    await page.fill('#j_username', email)
                    logger.info("Email filled")
                except Exception as e:
                    logger.error(f"Failed to fill email: {e}")
                try:
                    await page.fill('#j_password', password)
                    logger.info("Password filled")
                except Exception as e:
                    logger.error(f"Failed to fill password: {e}")
                try:
                    if await page.query_selector('#logOnFormSubmit'):
                        await page.click('#logOnFormSubmit')
                        logger.info("Continue button clicked")
                        try:
                            await page.wait_for_load_state("networkidle", timeout=15000)
                            logger.info(f"Navigation completed: {page.url[:100]}")
                            page_title = await page.title()
                            if "Terms of Use" in page_title or "terms" in page_title.lower():
                                logger.info("Terms of Use page detected, accepting...")
                                accept_selectors = ['#acceptButton', 'button[type="submit"]', '.accept-button', 'input[value="Accept"]']
                                for selector in accept_selectors:
                                    if await page.query_selector(selector):
                                        await page.click(selector)
                                        logger.info("Terms accepted")
                                        await page.wait_for_load_state("networkidle", timeout=10000)
                                        break
                        except asyncio.TimeoutError:
                            logger.warning("Navigation timeout (may be normal)")
                    else:
                        logger.warning("Continue button not found")
                except Exception as e:
                    logger.error(f"Error during login: {e}")
            elif "localhost" in current_url or "127.0.0.1" in current_url:
                logger.info("Already on kubelogin callback page")
            else:
                logger.warning(f"Unexpected page: {current_url}")
            await asyncio.sleep(3)
            await browser.close()
            logger.info("Login automation completed")
            return True
    except Exception as e:
        logger.error(f"Browser automation failed: {e}")
        return False
def _get_oidc_cache_dir() -> str:
    from pathlib import Path
    return str(Path.home() / '.kube' / 'cache' / 'oidc-login')
def _get_oidc_cache_file() -> Optional[str]:
    oidc_dir = _get_oidc_cache_dir()
    if os.path.exists(oidc_dir):
        files = [f for f in os.listdir(oidc_dir) if not f.startswith('.')]
        if files:
            return os.path.join(oidc_dir, files[0])
    return None
def _load_token_from_db(kyma_id: str) -> Optional[str]:
    try:
        from mp_btp.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SET search_path TO btp_scheduler, public"))
            result = conn.execute(
                text("SELECT oidc_token FROM kyma_runtimes WHERE id = :id"),
                {"id": kyma_id}
            )
            row = result.fetchone()
            if row and row[0]:
                return row[0]
    except ImportError:
        try:
            from models.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SET search_path TO btp_scheduler, public"))
                result = conn.execute(
                    text("SELECT oidc_token FROM kyma_runtimes WHERE id = :id"),
                    {"id": kyma_id}
                )
                row = result.fetchone()
                if row and row[0]:
                    return row[0]
        except Exception as e:
            logger.debug(f"Load token from db failed: {e}")
    except Exception as e:
        logger.debug(f"Load token from db failed: {e}")
    return None
def _save_token_to_db(kyma_id: str, token_json: str):
    try:
        from mp_btp.models.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SET search_path TO btp_scheduler, public"))
            conn.execute(
                text("UPDATE kyma_runtimes SET oidc_token = :token WHERE id = :id"),
                {"token": token_json, "id": kyma_id}
            )
            conn.commit()
            logger.debug(f"Saved oidc token to db ({len(token_json)} chars)")
    except ImportError:
        try:
            from models.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SET search_path TO btp_scheduler, public"))
                conn.execute(
                    text("UPDATE kyma_runtimes SET oidc_token = :token WHERE id = :id"),
                    {"token": token_json, "id": kyma_id}
                )
                conn.commit()
                logger.debug(f"Saved oidc token to db ({len(token_json)} chars)")
        except Exception as e:
            logger.warning(f"Save token to db failed: {e}")
    except Exception as e:
        logger.warning(f"Save token to db failed: {e}")
def _restore_token_from_db(kyma_id: str) -> bool:
    import json
    token_json = _load_token_from_db(kyma_id)
    if not token_json:
        return False
    try:
        json.loads(token_json)
        oidc_dir = _get_oidc_cache_dir()
        os.makedirs(oidc_dir, exist_ok=True)
        cache_file = os.path.join(oidc_dir, "1ba579863b341de39c39680ffeb6c5e6065fb4bbe54ad5a9d819a81c56cbfa76")
        with open(cache_file, 'w') as f:
            f.write(token_json)
        os.chmod(cache_file, 0o600)
        logger.debug(f"Restored token from db to local cache")
        return True
    except Exception as e:
        logger.warning(f"Restore token from db failed: {e}")
        return False
def _backup_token_to_db(kyma_id: str):
    cache_file = _get_oidc_cache_file()
    if cache_file and os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                token_json = f.read()
            _save_token_to_db(kyma_id, token_json)
        except Exception as e:
            logger.warning(f"Backup token to db failed: {e}")
def _get_account_cache_dir(email: str) -> str:
    import hashlib
    email_hash = hashlib.md5(email.encode()).hexdigest()[:12]
    return os.path.join(KUBECONFIG_CACHE_DIR, f"oidc_{email_hash}")
def _switch_oidc_cache(email: str):
    import shutil
    oidc_dir = _get_oidc_cache_dir()
    account_dir = _get_account_cache_dir(email)
    if os.path.exists(account_dir) and os.listdir(account_dir):
        os.makedirs(oidc_dir, exist_ok=True)
        for f in os.listdir(oidc_dir):
            os.remove(os.path.join(oidc_dir, f))
        for f in os.listdir(account_dir):
            shutil.copy2(os.path.join(account_dir, f), oidc_dir)
        logger.info(f"Restored oidc cache for {email[:20]}...")
def _backup_oidc_cache(email: str):
    import shutil
    oidc_dir = _get_oidc_cache_dir()
    account_dir = _get_account_cache_dir(email)
    if os.path.exists(oidc_dir) and os.listdir(oidc_dir):
        os.makedirs(account_dir, exist_ok=True)
        for f in os.listdir(account_dir):
            os.remove(os.path.join(account_dir, f))
        for f in os.listdir(oidc_dir):
            shutil.copy2(os.path.join(oidc_dir, f), account_dir)
        logger.debug(f"Backed up oidc cache for {email[:20]}...")
def kyma_login(kubeconfig_path: str, email: str, password: str, port: int = 8000) -> bool:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    _switch_oidc_cache(email)
    try:
        r = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=10, env=env)
        if r.returncode == 0:
            logger.info(f"Already logged in (cached token valid)")
            return True
    except (subprocess.TimeoutExpired, Exception) as e:
        logger.debug(f"Token check failed: {e}")
    try:
        import shutil
        oidc_dir = _get_oidc_cache_dir()
        if os.path.exists(oidc_dir):
            shutil.rmtree(oidc_dir)
            logger.info("Cleared oidc cache for fresh login")
    except Exception as e:
        logger.warning(f"Could not clear cache: {e}")
    oidc = _extract_oidc(kubeconfig_path)
    if not oidc:
        logger.error("Failed to extract OIDC config")
        return False
    logger.info(f"Starting kubelogin on port {port}")
    cmd = [
        "kubelogin", "get-token", f"--oidc-issuer-url={oidc['issuer_url']}",
        f"--oidc-client-id={oidc['client_id']}", "--oidc-extra-scope=email",
        "--oidc-extra-scope=openid", "--skip-open-browser", f"--listen-address=127.0.0.1:{port}"
    ]
    logger.debug(f"Command: {' '.join(cmd)}")
    logger.debug(f"PATH: {env.get('PATH', '')[:100]}")
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    except FileNotFoundError:
        logger.error("kubelogin not found")
        return False
    try:
        if not _wait_port(port, timeout=10):
            logger.error(f"Port {port} not available")
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                logger.error(f"kubelogin stderr: {stderr[:200]}")
                if '"token"' in stdout:
                    try:
                        r = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=5, env=env)
                        return r.returncode == 0
                    except subprocess.TimeoutExpired:
                        return False
            proc.terminate()
            return False
        logger.info(f"Port {port} ready, starting browser automation")
        time.sleep(1)
        if not asyncio.run(_automate_login(f"http://127.0.0.1:{port}", email, password)):
            logger.error("Browser automation failed")
            return False
        logger.info("Browser automation completed, waiting for token exchange")
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logger.warning("kubelogin still running, terminating")
            proc.terminate()
        time.sleep(1)
        logger.info("Checking kubectl")
        try:
            r = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=30, env=env)
            success = r.returncode == 0
            if success:
                logger.info("Login successful")
                _backup_oidc_cache(email)
            else:
                logger.error(f"kubectl failed: {r.stderr[:200]}")
            return success
        except subprocess.TimeoutExpired:
            logger.error("kubectl timeout")
            return False
    finally:
        try:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
def kyma_login_cached(instance_id: str, email: str, password: str, port: int = 8000, kyma_id: str = None) -> Optional[str]:
    kubeconfig = download_kubeconfig(instance_id)
    if not kubeconfig:
        logger.error(f"Failed to get kubeconfig for {instance_id}")
        return None
    env = _env()
    env['KUBECONFIG'] = kubeconfig
    if kyma_id:
        _restore_token_from_db(kyma_id)
    try:
        r = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=10, env=env)
        if r.returncode == 0:
            logger.info(f"Token valid for {instance_id[:8]}")
            if kyma_id:
                _backup_token_to_db(kyma_id)
            mark_logged_in(instance_id)
            return kubeconfig
    except Exception as e:
        logger.debug(f"Token check failed: {e}")
    logger.info(f"Token invalid, need browser login for {instance_id[:8]}")
    if kyma_login(kubeconfig, email, password, port):
        mark_logged_in(instance_id)
        if kyma_id:
            _backup_token_to_db(kyma_id)
        return kubeconfig
    if kyma_id:
        logger.info("Local login failed, trying remote refresh...")
        if _request_remote_token_refresh(kyma_id):
            if _restore_token_from_db(kyma_id):
                try:
                    r = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=10, env=env)
                    if r.returncode == 0:
                        logger.info("Remote refresh successful")
                        mark_logged_in(instance_id)
                        return kubeconfig
                except:
                    pass
    return None
def _get_active_server_endpoint() -> Optional[str]:
    try:
        from mp_btp.models.database import engine
        from sqlalchemy import text
        from datetime import datetime, timezone, timedelta
        with engine.connect() as conn:
            conn.execute(text("SET search_path TO btp_scheduler, public"))
            row = result.fetchone()
            if row:
                return row[0]
    except ImportError:
        try:
            from models.database import engine
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SET search_path TO btp_scheduler, public"))
                row = result.fetchone()
                if row:
                    return row[0]
        except Exception as e:
            logger.debug(f"Get server endpoint failed: {e}")
    except Exception as e:
        logger.debug(f"Get server endpoint failed: {e}")
    return None
def _request_remote_token_refresh(kyma_id: str) -> bool:
    import requests
    endpoint = _get_active_server_endpoint()
    if not endpoint:
        logger.debug("No active server with browser found")
        return False
    try:
        url = f"{endpoint}/api/v1/kyma/{kyma_id}/refresh-token"
        logger.info(f"Requesting token refresh from {endpoint}")
        resp = requests.post(url, timeout=120)
        if resp.status_code == 200:
            logger.info("Remote token refresh successful")
            return True
        else:
            logger.warning(f"Remote refresh failed: {resp.status_code} {resp.text[:100]}")
    except Exception as e:
        logger.warning(f"Remote refresh request failed: {e}")
    return False
def kyma_deploy(kubeconfig_path: str, name: str, image: str, port: Optional[int] = None,
                memory_mb: int = 256, env_vars: Optional[Dict] = None, namespace: str = "default") -> Dict:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    dep = {
        'apiVersion': 'apps/v1', 'kind': 'Deployment',
        'metadata': {'name': name, 'namespace': namespace},
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
            'metadata': {'name': name, 'namespace': namespace},
            'spec': {'selector': {'app': name}, 'ports': [{'port': port, 'targetPort': port}], 'type': 'ClusterIP'}
        })
    manifest_yaml = '---\n'.join(yaml.dump(m) for m in manifests)
    r = subprocess.run(['kubectl', 'apply', '-f', '-'], input=manifest_yaml, capture_output=True, text=True, timeout=60, env=env)
    if r.returncode != 0:
        return {'success': False, 'error': r.stderr}
    url = None
    if port:
        r2 = subprocess.run(['kubectl', 'get', 'svc', name, '-n', namespace, '-o', 'jsonpath={.spec.clusterIP}:{.spec.ports[0].port}'],
                           capture_output=True, text=True, timeout=30, env=env)
        if r2.returncode == 0 and r2.stdout:
            url = f"http://{r2.stdout}"
    return {'success': True, 'url': url}
def kyma_deploy_raw_yaml(kubeconfig_path: str, yaml_content: str, namespace: str = "demo") -> Dict:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    subprocess.run(['kubectl', 'create', 'namespace', namespace, '--dry-run=client', '-o', 'yaml'], 
                  capture_output=True, env=env)
    subprocess.run(['kubectl', 'apply', '-f', '-'], 
                  input=f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {namespace}\n",
                  capture_output=True, text=True, env=env)
    r = subprocess.run(['kubectl', 'apply', '-f', '-', '-n', namespace], 
                      input=yaml_content, capture_output=True, text=True, timeout=120, env=env)
    if r.returncode != 0:
        return {'success': False, 'error': r.stderr}
    return {'success': True, 'output': r.stdout}
def kyma_delete(kubeconfig_path: str, name: str, namespace: str = "default") -> bool:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    r1 = subprocess.run(['kubectl', 'delete', 'deployment', name, '-n', namespace, '--ignore-not-found'],
                        capture_output=True, text=True, timeout=60, env=env)
    r2 = subprocess.run(['kubectl', 'delete', 'svc', name, '-n', namespace, '--ignore-not-found'],
                        capture_output=True, text=True, timeout=60, env=env)
    return r1.returncode == 0 and r2.returncode == 0
def check_deployment_ready(kubeconfig_path: str, name: str, namespace: str = "default", timeout: int = 120) -> bool:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    try:
        r = subprocess.run(['kubectl', 'rollout', 'status', f'deployment/{name}', '-n', namespace, f'--timeout={timeout}s'],
                          capture_output=True, text=True, timeout=timeout + 10, env=env)
        return r.returncode == 0
    except:
        return False
def get_service_url(kubeconfig_path: str, name: str, namespace: str = "default") -> Optional[str]:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    try:
        r = subprocess.run(['kubectl', 'get', 'svc', name, '-n', namespace, '-o', 'jsonpath={.spec.clusterIP}:{.spec.ports[0].port}'],
                          capture_output=True, text=True, timeout=30, env=env)
        return f"http://{r.stdout}" if r.returncode == 0 and r.stdout else None
    except:
        return None
def kyma_logs(kubeconfig_path: str, name: str, namespace: str = "default", tail: int = 100) -> str:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    try:
        r = subprocess.run(
            ['kubectl', 'get', 'pods', '-n', namespace, '-l', f'app={name}', '-o', 'jsonpath={.items[0].metadata.name}'],
            capture_output=True, text=True, timeout=30, env=env
        )
        if r.returncode != 0 or not r.stdout:
            return f"No pods found for deployment: {name}"
        pod_name = r.stdout.strip()
        r = subprocess.run(
            ['kubectl', 'logs', pod_name, '-n', namespace, f'--tail={tail}'],
            capture_output=True, text=True, timeout=30, env=env
        )
        return r.stdout if r.returncode == 0 else f"Failed to get logs: {r.stderr}"
    except Exception as e:
        return f"Error: {e}"
def kyma_restart(kubeconfig_path: str, name: str, namespace: str = "default") -> bool:
    env = _env()
    env['KUBECONFIG'] = kubeconfig_path
    try:
        r = subprocess.run(
            ['kubectl', 'rollout', 'restart', f'deployment/{name}', '-n', namespace],
            capture_output=True, text=True, timeout=60, env=env
        )
        return r.returncode == 0
    except:
        return False
if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 4:
        print(f"Login: {kyma_login(sys.argv[1], sys.argv[2], sys.argv[3])}")
    else:
        print("Usage: python kyma.py <kubeconfig> <email> <password>")