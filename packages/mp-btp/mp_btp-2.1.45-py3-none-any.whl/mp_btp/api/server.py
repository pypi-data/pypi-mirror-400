import sys
import os
import time
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import atexit

from mp_btp.config import get_settings, get_config
from mp_btp.models import Base, engine
from mp_btp.models.service_instance import ServiceInstance
from mp_btp.models.database import SessionLocal
from mp_btp.api.routes import health, accounts, deployments, kyma, maintenance
from mp_btp.tasks.scheduled import start_scheduler, stop_scheduler
from instance_lock import acquire_lock, release_lock, update_heartbeat, get_lock_status

# Setup logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize schema and create tables
from mp_btp.models.database import init_schema
init_schema()
Base.metadata.create_all(bind=engine)

# 热备模式：等待获取锁
_is_master = False
_scheduler_started = False

def _try_become_master():
    """尝试成为主实例"""
    global _is_master, _scheduler_started
    if acquire_lock(engine):
        _is_master = True
        if not _scheduler_started:
            start_scheduler()
            _scheduler_started = True
            logger.info("✓ 成为主实例，调度器已启动")
        return True
    return False

def _standby_loop():
    """热备循环：等待主实例失效后接管"""
    global _is_master
    while True:
        time.sleep(10)
        if not _is_master:
            if _try_become_master():
                continue
            status = get_lock_status(engine)
            if status:
                logger.debug(f"⏳ 热备中，主实例: {status['master']}")

# 首次尝试获取锁
if _try_become_master():
    logger.info("✓ 调度器锁已获取（主实例）")
else:
    status = get_lock_status(engine)
    logger.info(f"⏳ 热备模式启动，等待主实例 {status['master'] if status else 'unknown'}")
    # 启动热备线程
    threading.Thread(target=_standby_loop, daemon=True).start()

# 注册退出时释放锁
atexit.register(lambda: release_lock(engine) if _is_master else None)

# 服务实例 ID（用于注册/注销）
_service_instance_id = None

def _check_browser_available() -> bool:
    """检查是否有 Chromium"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except:
        return False

def _register_service_instance(endpoint: str):
    """注册服务实例到数据库"""
    global _service_instance_id
    try:
        has_browser = _check_browser_available()
        with SessionLocal() as db:
            instance = ServiceInstance(endpoint=endpoint, has_browser=has_browser)
            db.add(instance)
            db.commit()
            _service_instance_id = instance.id
            logger.info(f"✓ 服务实例已注册: {endpoint} (browser={has_browser})")
    except Exception as e:
        logger.warning(f"注册服务实例失败: {e}")

def _unregister_service_instance():
    """注销服务实例"""
    global _service_instance_id
    if _service_instance_id:
        try:
            with SessionLocal() as db:
                db.query(ServiceInstance).filter(ServiceInstance.id == _service_instance_id).delete()
                db.commit()
            logger.info("✓ 服务实例已注销")
        except Exception as e:
            logger.warning(f"注销服务实例失败: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # 优先使用环境变量指定的外网端点
    endpoint = os.environ.get("BTP_SERVICE_ENDPOINT")
    if not endpoint:
        config = get_config()
        host = config['api']['host']
        port = config['api']['port']
        # 如果是 0.0.0.0，尝试获取 hostname
        if host == '0.0.0.0':
            import socket
            try:
                host = socket.gethostname()
            except:
                host = 'localhost'
        endpoint = f"http://{host}:{port}"
    _register_service_instance(endpoint)
    yield
    # Shutdown
    _unregister_service_instance()
    if _scheduler_started:
        stop_scheduler()

# Create app
app = FastAPI(title="BTP Scheduler", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(deployments.router, prefix="/api/v1")
app.include_router(kyma.router, prefix="/api/v1")
app.include_router(maintenance.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "BTP Scheduler API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    config = get_config()
    uvicorn.run(
        "server:app",
        host=config["api"]["host"],
        port=config["api"]["port"],
        reload=True
    )
