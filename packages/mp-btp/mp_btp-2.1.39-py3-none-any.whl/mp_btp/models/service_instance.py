from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime, timezone
import uuid
from .database import Base
from .base import GUID


class ServiceInstance(Base):
    __tablename__ = "service_instances"
    
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    endpoint = Column(String(255), nullable=False)  # http://host:port
    last_heartbeat = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    has_browser = Column(Boolean, default=False)  # 是否有 Chromium
    is_active = Column(Boolean, default=True)
