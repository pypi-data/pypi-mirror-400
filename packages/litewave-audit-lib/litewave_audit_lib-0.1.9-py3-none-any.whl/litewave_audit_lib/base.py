from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any

class BaseAuditLogger(ABC):
    @abstractmethod
    def log(self, *, who, resource, action, timestamp=None,
              location=None, request_context=None,
              context=None, client=None, tenant_id=None, resource_type=None):
        """Audit an action with full context"""
        pass

