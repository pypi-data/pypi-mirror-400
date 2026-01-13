"""Operation logging utility."""
from datetime import datetime, timezone
from mp_btp.models.database import SessionLocal
from mp_btp.models.operation_log import OperationLog
import logging

logger = logging.getLogger(__name__)

def log_operation(
    operation_type: str,
    status: str = "SUCCESS",
    account_id: str = None,
    deployment_id: str = None,
    replica_id: str = None,
    error_message: str = None,
    execution_time_ms: int = None,
    details: str = None
):
    """Record operation to database."""
    try:
        db = SessionLocal()
        log = OperationLog(
            operation_type=operation_type,
            status=status,
            account_id=account_id,
            deployment_id=deployment_id,
            replica_id=replica_id,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
            details=details
        )
        db.add(log)
        db.commit()
        db.close()
        logger.debug(f"Logged: {operation_type} | {status}")
    except Exception as e:
        logger.error(f"Failed to log operation: {e}")


# Operation types
OP_ACCOUNT_ADD = "ACCOUNT_ADD"
OP_ACCOUNT_DELETE = "ACCOUNT_DELETE"
OP_ACCOUNT_VERIFY = "ACCOUNT_VERIFY"
OP_KYMA_CREATE = "KYMA_CREATE"
OP_KYMA_DELETE = "KYMA_DELETE"
OP_KYMA_EXPIRE = "KYMA_EXPIRE"
OP_CF_CREATE = "CF_CREATE"
OP_DEPLOY_CREATE = "DEPLOY_CREATE"
OP_DEPLOY_DELETE = "DEPLOY_DELETE"
OP_DEPLOY_MIGRATE = "DEPLOY_MIGRATE"
OP_REPLICA_START = "REPLICA_START"
OP_REPLICA_STOP = "REPLICA_STOP"
