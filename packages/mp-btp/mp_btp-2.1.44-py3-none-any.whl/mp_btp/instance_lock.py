#!/usr/bin/env python3
"""
单实例锁机制（基于数据库）- 热备模式
主实例运行调度，备实例等待接管
"""
import os
import socket
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

logger = logging.getLogger(__name__)

LOCK_NAME = "btp_scheduler_master"
LOCK_TIMEOUT = 30  # 锁超时时间（秒）

def get_instance_id():
    """获取实例标识"""
    hostname = socket.gethostname()
    pid = os.getpid()
    return f"{hostname}:{pid}"

def get_lock_status(engine):
    """获取当前锁状态"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT instance_id, acquired_at, heartbeat_at 
                FROM scheduler_locks 
                WHERE lock_name = :lock_name
            """), {"lock_name": LOCK_NAME})
            row = result.fetchone()
            if row:
                return {
                    "master": row[0],
                    "acquired_at": str(row[1]),
                    "heartbeat_at": str(row[2]),
                    "is_self": row[0] == get_instance_id()
                }
        return None
    except:
        return None

def acquire_lock(engine):
    """获取单实例锁（数据库级别）"""
    instance_id = get_instance_id()
    
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scheduler_locks (
                    lock_name VARCHAR(100) PRIMARY KEY,
                    instance_id VARCHAR(200),
                    acquired_at TIMESTAMP,
                    heartbeat_at TIMESTAMP
                )
            """))
            
        with engine.begin() as conn:
            now = datetime.now(timezone.utc)
            timeout_threshold = now - timedelta(seconds=LOCK_TIMEOUT)
            
            # 清理过期锁
            conn.execute(text("""
                DELETE FROM scheduler_locks 
                WHERE lock_name = :lock_name 
                AND heartbeat_at < :threshold
            """), {"lock_name": LOCK_NAME, "threshold": timeout_threshold})
            
            # 尝试插入锁
            try:
                conn.execute(text("""
                    INSERT INTO scheduler_locks (lock_name, instance_id, acquired_at, heartbeat_at)
                    VALUES (:lock_name, :instance_id, :now, :now)
                """), {"lock_name": LOCK_NAME, "instance_id": instance_id, "now": now})
                logger.info(f"✓ 获取调度器锁成功: {instance_id}")
                return True
            except:
                pass
        
        # 锁被占用，返回 False（热备模式不退出）
        status = get_lock_status(engine)
        if status:
            logger.info(f"⏳ 热备模式: 等待主实例 {status['master']}")
        return False
                
    except Exception as e:
        logger.error(f"获取锁失败: {e}")
        return False

def update_heartbeat(engine):
    """更新心跳时间"""
    instance_id = get_instance_id()
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE scheduler_locks 
                SET heartbeat_at = :now 
                WHERE lock_name = :lock_name AND instance_id = :instance_id
            """), {"now": datetime.now(timezone.utc), "lock_name": LOCK_NAME, "instance_id": instance_id})
    except:
        pass

def release_lock(engine):
    """释放锁"""
    instance_id = get_instance_id()
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                DELETE FROM scheduler_locks 
                WHERE lock_name = :lock_name AND instance_id = :instance_id
            """), {"lock_name": LOCK_NAME, "instance_id": instance_id})
            logger.info(f"✓ 释放调度器锁: {instance_id}")
    except:
        pass
