import logging
from datetime import date, datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from mp_btp.config import get_config
from mp_btp.models.database import SessionLocal
from mp_btp.models import Account, CFOrg, KymaRuntime, Deployment, DeploymentReplica
from mp_btp.scheduler.cf_pattern import should_be_active_today, update_history, parse_pattern
from mp_btp.scheduler.core import select_account_for_deployment
from mp_btp.tasks.cleanup import cleanup_replica
from mp_btp.utils.audit import log_operation, OP_KYMA_CREATE, OP_KYMA_DELETE, OP_KYMA_EXPIRE, OP_DEPLOY_MIGRATE
logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()
def schedule_cooling_end(runtime_id: str, cooling_until: datetime):
    job_id = f"cooling_end_{runtime_id}"
    try:
        scheduler.remove_job(job_id)
    except:
        pass
    scheduler.add_job(
        _handle_cooling_end,
        'date',
        run_date=cooling_until,
        args=[runtime_id],
        id=job_id,
        replace_existing=True
    )
    logger.info(f"Scheduled cooling end for {runtime_id[:8]} at {cooling_until}")
def _handle_cooling_end(runtime_id: str):
    db = SessionLocal()
    try:
        runtime = db.query(KymaRuntime).filter(KymaRuntime.id == runtime_id).first()
        if runtime and runtime.status == "COOLING":
            runtime.status = "EXPIRED"
            runtime.cooling_until = None
            db.commit()
            logger.info(f"Kyma {runtime_id[:8]} cooling ended, status -> EXPIRED")
    except Exception as e:
        logger.error(f"Handle cooling end failed: {e}")
    finally:
        db.close()
def migrate_deployments_from_runtime(db, runtime: KymaRuntime):
    from tasks.deployment import execute_replica_kyma, execute_replica_mock
    replicas = db.query(DeploymentReplica).filter(
        DeploymentReplica.runtime_id == runtime.id,
        DeploymentReplica.runtime_type == "kyma",
        DeploymentReplica.status == "RUNNING"
    ).all()
    if not replicas:
        return
    logger.info(f"Migrating {len(replicas)} replicas from expiring Kyma {runtime.cluster_name}")
    for replica in replicas:
        deployment = db.query(Deployment).filter(Deployment.id == replica.deployment_id).first()
        if not deployment:
            continue
        new_account, new_runtime = select_account_for_deployment(
            db, "kyma", deployment.memory_mb, wait_for_creating=True
        )
        if not new_account or new_runtime.id == runtime.id:
            logger.warning(f"No alternative account for replica {replica.id}")
            continue
        old_account_id = replica.account_id
        replica.account_id = new_account.id
        replica.runtime_id = new_runtime.id
        replica.status = "PENDING"
        replica.access_url = None
        db.commit()
        log_operation(OP_DEPLOY_MIGRATE, "SUCCESS",
            account_id=str(new_account.id), deployment_id=str(deployment.id),
            replica_id=str(replica.id), details=f"from={str(old_account_id)[:8]}")
        logger.info(f"Replica {replica.id} migrated from account {old_account_id} to {new_account.id}")
        try:
            mock_mode = get_config().get("deployment", {}).get("mock", True)
            if mock_mode:
                execute_replica_mock(db, deployment, replica)
            else:
                execute_replica_kyma(db, deployment, replica)
            logger.info(f"Replica {replica.id} re-deployed successfully")
        except Exception as e:
            logger.error(f"Re-deploy replica {replica.id} failed: {e}")
            replica.status = "FAILED"
            db.commit()
def start_scheduler():
    from models import engine
    from instance_lock import update_heartbeat
    config = get_config()
    jobs_config = config.get("scheduled_jobs", {})
    scheduler.add_job(
        lambda: update_heartbeat(engine),
        'interval',
        seconds=10,
        id="heartbeat",
        replace_existing=True
    )
    logger.info("Heartbeat task scheduled every 10 seconds")
    cf_config = jobs_config.get("cf_daily_check", {})
    cf_time = cf_config.get("time", "08:30")
    cf_tz = cf_config.get("timezone", "Asia/Shanghai")
    hour, minute = map(int, cf_time.split(":"))
    scheduler.add_job(
        cf_daily_check,
        CronTrigger(hour=hour, minute=minute, timezone=pytz.timezone(cf_tz)),
        id="cf_daily_check",
        replace_existing=True
    )
    logger.info(f"CF daily check scheduled at {cf_time} {cf_tz}")
    cleanup_config = jobs_config.get("cleanup", {})
    cleanup_time = cleanup_config.get("time", "01:00")
    cleanup_tz = cleanup_config.get("timezone", "Asia/Shanghai")
    hour, minute = map(int, cleanup_time.split(":"))
    scheduler.add_job(
        cleanup_and_rebuild,
        CronTrigger(hour=hour, minute=minute, timezone=pytz.timezone(cleanup_tz)),
        id="cleanup_expired",
        replace_existing=True
    )
    logger.info(f"Cleanup scheduled at {cleanup_time} {cleanup_tz}")
    scheduler.add_job(
        check_creating_kyma,
        'interval',
        minutes=5,
        id="check_creating_kyma",
        replace_existing=True
    )
    logger.info("Kyma creation check scheduled every 5 minutes")
    scheduler.add_job(
        reschedule_pending_deployments,
        'interval',
        minutes=2,
        id="reschedule_pending",
        replace_existing=True
    )
    logger.info("Pending reschedule check scheduled every 2 minutes")
    schedule_account_daily_checks()
    logger.info("Pending reschedule check scheduled every 2 minutes")
    _restore_cooling_jobs()
    scheduler.start()
    logger.info("Scheduler started")
def _restore_cooling_jobs():
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        cooling_runtimes = db.query(KymaRuntime).filter(
            KymaRuntime.status == "COOLING",
            KymaRuntime.cooling_until != None
        ).all()
        for runtime in cooling_runtimes:
            cooling_until = runtime.cooling_until
            if cooling_until.tzinfo is None:
                cooling_until = cooling_until.replace(tzinfo=timezone.utc)
            if cooling_until <= now:
                runtime.status = "EXPIRED"
                runtime.cooling_until = None
                logger.info(f"Kyma {runtime.id} cooling already ended, status -> EXPIRED")
            else:
                schedule_cooling_end(str(runtime.id), cooling_until)
        db.commit()
        logger.info(f"Restored {len(cooling_runtimes)} cooling jobs")
    except Exception as e:
        logger.error(f"Restore cooling jobs failed: {e}")
    finally:
        db.close()
def stop_scheduler():
    scheduler.shutdown()
def cf_daily_check():
    logger.info("Starting CF daily check")
    db = SessionLocal()
    try:
        today = date.today()
        cf_orgs = db.query(CFOrg).filter(CFOrg.status == "OK").all()
        for cf in cf_orgs:
            account = db.query(Account).filter(Account.id == cf.account_id).first()
            if not account or account.status != "ACTIVE":
                continue
            pattern = cf.active_pattern or "7-5"
            history = cf.active_days_history or {}
            running = db.query(DeploymentReplica).filter(
                DeploymentReplica.runtime_id == cf.id,
                DeploymentReplica.runtime_type == "cf",
                DeploymentReplica.status == "RUNNING"
            ).count()
            was_active = running > 0
            window_days = parse_pattern(pattern)[0]
            cf.active_days_history = update_history(history, today, was_active, window_days)
            logger.info(f"CF {cf.org_name}: {'active' if was_active else 'idle'} (pattern: {pattern})")
        db.commit()
        logger.info(f"CF daily check completed: {len(cf_orgs)} orgs")
    except Exception as e:
        logger.error(f"CF daily check failed: {e}")
        db.rollback()
    finally:
        db.close()
def cleanup_and_rebuild():
    logger.info("Starting cleanup and rebuild")
    db = SessionLocal()
    config = get_config()
    try:
        now = datetime.now(timezone.utc)
        cooling_hours = config.get("cooling", {}).get("duration_hours", 24)
        expired_deployments = db.query(Deployment).filter(
            Deployment.status == "RUNNING",
            Deployment.expires_at != None,
            Deployment.expires_at <= now
        ).all()
        for deployment in expired_deployments:
            logger.info(f"Cleaning up expired deployment: {deployment.id}")
            for replica in deployment.replicas_list:
                if replica.status == "RUNNING":
                    cleanup_replica(db, replica)
                replica.status = "STOPPED"
                replica.stopped_at = now
            deployment.status = "STOPPED"
        expiring_threshold = now + timedelta(days=2)
        expiring_kyma = db.query(KymaRuntime).filter(
            KymaRuntime.status == "OK",
            KymaRuntime.expires_at <= expiring_threshold,
            KymaRuntime.expires_at > now
        ).all()
        for runtime in expiring_kyma:
            runtime.status = "EXPIRING"
            log_operation(OP_KYMA_EXPIRE, "EXPIRING", account_id=str(runtime.account_id),
                details=f"cluster={runtime.cluster_name}")
            logger.info(f"Kyma {runtime.cluster_name} marked as EXPIRING")
            migrate_deployments_from_runtime(db, runtime)
        expired_kyma = db.query(KymaRuntime).filter(
            KymaRuntime.status.in_(["OK", "EXPIRING"]),
            KymaRuntime.expires_at <= now
        ).all()
        for runtime in expired_kyma:
            account = db.query(Account).filter(Account.id == runtime.account_id).first()
            if account:
                delete_kyma_from_btp(account, runtime)
            runtime.status = "COOLING"
            runtime.cooling_until = now + timedelta(hours=cooling_hours)
            runtime.memory_used_mb = 0
            log_operation(OP_KYMA_DELETE, "SUCCESS", account_id=str(runtime.account_id),
                details=f"cluster={runtime.cluster_name}")
            logger.info(f"Kyma {runtime.cluster_name} deleted and set to COOLING")
        cooling_done = db.query(KymaRuntime).filter(
            KymaRuntime.status == "COOLING",
            KymaRuntime.cooling_until <= now
        ).all()
        for runtime in cooling_done:
            runtime.status = "EXPIRED"
            runtime.cooling_until = None
            logger.info(f"Kyma cooling done for account {runtime.account_id}, ready to rebuild on demand")
        db.commit()
        logger.info(f"Cleanup done: {len(expired_deployments)} deployments, {len(expired_kyma)} kyma deleted, {len(cooling_done)} kyma ready")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        db.rollback()
    finally:
        db.close()
def delete_kyma_from_btp(account: Account, runtime: KymaRuntime) -> bool:
    from integrations.btp_cli import BTPClient
    try:
        client = BTPClient(account.subdomain, account.email, account.password)
        if not client.login():
            logger.error(f"BTP login failed for {account.email}")
            return False
        subaccount_id = client.get_subaccount_id()
        if not subaccount_id:
            return False
        result = client._run([
            "delete", "accounts/environment-instance", runtime.instance_id,
            "-sa", subaccount_id, "--confirm"
        ], timeout=120)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Delete Kyma failed: {e}")
        return False
def rebuild_kyma(account: Account, runtime: KymaRuntime) -> bool:
    from integrations.btp_cli import BTPClient
    try:
        client = BTPClient(account.email, account.email, account.password)
        if not client.login():
            logger.error(f"BTP login failed for {account.email}")
            return False
        subaccount_id = account.subaccount_id or client.get_subaccount_id()
        if not subaccount_id:
            return False
        existing = client.get_kyma_instance(subaccount_id)
        if existing and existing.get("state") == "OK":
            runtime.instance_id = existing.get("id")
            runtime.cluster_name = existing.get("name")
            runtime.status = "OK"
            runtime.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
            logger.info(f"Kyma already exists for {account.email}")
            return True
        name = runtime.cluster_name or "kyma"
        result = client.create_kyma_runtime(subaccount_id, name)
        if result.get("success"):
            runtime.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
            return True
        return False
    except Exception as e:
        logger.error(f"Rebuild Kyma failed: {e}")
        return False
def check_creating_kyma():
    logger.info("Checking CREATING Kyma status")
    db = SessionLocal()
    try:
        creating = db.query(KymaRuntime).filter(KymaRuntime.status == "CREATING").all()
        for runtime in creating:
            account = db.query(Account).filter(Account.id == runtime.account_id).first()
            if not account:
                continue
            from integrations.btp_cli import BTPClient
            client = BTPClient(account.email, account.email, account.password)
            if not client.login():
                continue
            subaccount_id = account.subaccount_id or client.get_subaccount_id()
            if not subaccount_id:
                continue
            kyma = client.get_kyma_instance(subaccount_id)
            if kyma:
                if kyma.get("state") == "OK":
                    runtime.instance_id = kyma.get("id")
                    runtime.cluster_name = kyma.get("name")
                    runtime.status = "OK"
                    runtime.expires_at = datetime.now(timezone.utc) + timedelta(days=14)
                    logger.info(f"Kyma {runtime.cluster_name} is now ready")
                elif kyma.get("state") == "FAILED":
                    runtime.status = "FAILED"
                    runtime.failed_count = (runtime.failed_count or 0) + 1
                    logger.error(f"Kyma creation failed for {account.email}")
        db.commit()
    except Exception as e:
        logger.error(f"Check creating Kyma failed: {e}")
        db.rollback()
    finally:
        db.close()
def trigger_cleanup():
    cleanup_and_rebuild()
def trigger_cf_check():
    cf_daily_check()
def reschedule_pending_deployments():
    from tasks.deployment import execute_deployment
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=1)
        pending = db.query(Deployment).filter(
            Deployment.status == "PENDING",
            Deployment.created_at < cutoff
        ).all()
        for dep in pending:
            replica = dep.replicas_list[0] if dep.replicas_list else None
            if not replica or replica.status != "PENDING":
                continue
            old_account = db.query(Account).filter(Account.id == replica.account_id).first()
            new_account, new_runtime = select_account_for_deployment(
                db, dep.env_type, dep.memory_mb, wait_for_creating=False
            )
            if new_account and new_account.id != replica.account_id:
                replica.account_id = new_account.id
                replica.runtime_id = new_runtime.id if new_runtime else None
                db.commit()
                logger.info(f"Rescheduled {str(dep.id)[:8]} from {old_account.email} to {new_account.email}")
                try:
                    execute_deployment(str(dep.id))
                except Exception as e:
                    logger.error(f"Reschedule execution failed: {e}")
            else:
                logger.debug(f"No better account for {str(dep.id)[:8]}")
    except Exception as e:
        logger.error(f"Reschedule pending failed: {e}")
        db.rollback()
    finally:
        db.close()
def schedule_account_daily_checks():
    import random
    db = SessionLocal()
    try:
        accounts = db.query(Account).filter(Account.status == "ACTIVE").all()
        for account in accounts:
            hour = random.randint(1, 22)
            minute = random.randint(0, 59)
            scheduler.add_job(
                check_account_kyma,
                CronTrigger(hour=hour, minute=minute),
                args=[str(account.id)],
                id=f"check_account_{account.id}",
                replace_existing=True
            )
            logger.info(f"Scheduled {account.email} daily check at {hour:02d}:{minute:02d}")
    finally:
        db.close()
def check_account_kyma(account_id: str):
    from integrations.kyma import get_cached_kubeconfig
    import subprocess
    import os
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account or account.status != "ACTIVE":
            return
        runtime = db.query(KymaRuntime).filter(
            KymaRuntime.account_id == account.id,
            KymaRuntime.status.in_(["OK", "EXPIRING"])
        ).first()
        if not runtime or not runtime.instance_id:
            return
        kubeconfig = get_cached_kubeconfig(runtime.instance_id)
        if not kubeconfig:
            from integrations.kyma import download_kubeconfig
            kubeconfig = download_kubeconfig(runtime.instance_id, use_cache=False)
        if not kubeconfig:
            logger.warning(f"Cannot get kubeconfig for {account.email}, Kyma may be deleted")
            now = datetime.now(timezone.utc)
            expires_at = runtime.expires_at
            if expires_at:
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                if expires_at <= now:
                    logger.info(f"Kyma expired and deleted: {account.email}")
                    handle_kyma_expired(db, account, runtime)
                    db.commit()
                    return
            handle_unexpected_kyma_failure(db, account, runtime)
            db.commit()
            return
        env = os.environ.copy()
        env['KUBECONFIG'] = kubeconfig
        try:
            r = subprocess.run(['kubectl', 'cluster-info'], 
                             capture_output=True, timeout=15, env=env)
            if r.returncode == 0:
                logger.info(f"Kyma check OK: {account.email}")
                return
        except subprocess.TimeoutExpired:
            pass
        now = datetime.now(timezone.utc)
        expires_at = runtime.expires_at
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= now:
                logger.info(f"Kyma expired normally: {account.email}")
                handle_kyma_expired(db, account, runtime)
                db.commit()
                return
        logger.warning(f"Kyma unexpected failure: {account.email}")
        handle_unexpected_kyma_failure(db, account, runtime)
        db.commit()
    except Exception as e:
        logger.error(f"Check account kyma failed: {e}")
        db.rollback()
    finally:
        db.close()
def handle_kyma_expired(db, account: Account, runtime: KymaRuntime):
    config = get_config()
    cooling_hours = config.get("cooling", {}).get("duration_hours", 168)
    replicas = db.query(DeploymentReplica).filter(
        DeploymentReplica.runtime_id == runtime.id,
        DeploymentReplica.status == "RUNNING"
    ).all()
    for r in replicas:
        r.status = "STOPPED"
        r.stopped_at = datetime.now(timezone.utc)
    if runtime.instance_id:
        logger.info(f"Deleting expired Kyma from BTP: {account.email}")
        delete_kyma_from_btp(account, runtime)
    runtime.status = "COOLING"
    runtime.instance_id = None
    runtime.memory_used_mb = 0
    runtime.cooling_until = datetime.now(timezone.utc) + timedelta(hours=cooling_hours)
    schedule_cooling_end(str(runtime.id), runtime.cooling_until)
    log_operation(OP_KYMA_EXPIRE, "SUCCESS", account_id=str(account.id),
        details=f"expired, cooling until {runtime.cooling_until}")
    logger.info(f"Kyma {runtime.cluster_name} expired, cooling for {cooling_hours}h")
def handle_unexpected_kyma_failure(db, account: Account, runtime: KymaRuntime):
    config = get_config()
    cooling_hours = config.get("cooling", {}).get("duration_hours", 168)
    migrate_deployments_from_runtime(db, runtime)
    replicas = db.query(DeploymentReplica).filter(
        DeploymentReplica.runtime_id == runtime.id,
        DeploymentReplica.status == "RUNNING"
    ).all()
    for r in replicas:
        r.status = "STOPPED"
        r.stopped_at = datetime.now(timezone.utc)
    if runtime.instance_id:
        logger.info(f"Deleting failed Kyma from BTP: {account.email}")
        delete_kyma_from_btp(account, runtime)
    runtime.status = "COOLING"
    runtime.instance_id = None
    runtime.failed_count = (runtime.failed_count or 0) + 1
    runtime.memory_used_mb = 0
    runtime.cooling_until = datetime.now(timezone.utc) + timedelta(hours=cooling_hours * 2)
    schedule_cooling_end(str(runtime.id), runtime.cooling_until)
    log_operation(OP_KYMA_EXPIRE, "FAILED", account_id=str(account.id),
        details=f"unexpected failure, failed_count={runtime.failed_count}, cooling until {runtime.cooling_until}")
    logger.warning(f"Kyma {runtime.cluster_name} failed unexpectedly, cooling for {cooling_hours * 2}h")