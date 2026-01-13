import asyncio
import json
import logging
import uuid
from datetime import datetime
from threading import Thread
from typing import Optional
import os

import nats
from litewave_audit_lib.base import BaseAuditLogger

logger = logging.getLogger(__name__)


class NATSAuditLogger(BaseAuditLogger):
    def __init__(
        self,
        subject: str,
        nats_connection_url: str = "nats://localhost:4222",
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.subject = subject
        self.nc = None
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self.loop.run_forever, daemon=True)
        self.thread.start()

        if username and password and "@" not in nats_connection_url:
            scheme, addr = nats_connection_url.split("://", 1)
            self.nats_url = f"{scheme}://{username}:{password}@{addr}"
        else:
            self.nats_url = nats_connection_url
        
        # Block and connect on initialization to fail fast
        try:
            future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
            self.nc = future.result(timeout=10)
            logger.info("[NATS] Connection established.")
        except Exception as e:
            self.shutdown()
            raise ConnectionError(f"Failed to connect to NATS at {self.nats_url}") from e

    def _connect(self):
        return nats.connect(servers=[self.nats_url])

    def log(
        self,
        who: Optional[str],
        resource: str,
        action: str,
        timestamp: Optional[datetime] = None,
        location: Optional[str] = "cloud",
        request_context: Optional[dict] = None,
        context: Optional[dict] = None,
        client: Optional[dict] = None,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        deployment_id: Optional[str] = None
    ):
        entry = {
            "id": str(uuid.uuid4()),
            "who": who,
            "resource": resource,
            "action": action,
            "location": location,
            "request_context": request_context or {},
            "context": context or {},
            "client": client or {},
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "deployment_id": deployment_id,
        }
        
        future = asyncio.run_coroutine_threadsafe(self._publish(entry), self.loop)
        try:
            future.result(timeout=5)
            logger.info(f"[NATS] Published: {entry['id']}")
        except Exception as e:
            raise IOError(f"Failed to publish audit log to NATS: {e}") from e

    async def _publish(self, message: dict):
        if self.nc is None or not self.nc.is_connected:
             raise ConnectionError("NATS client is not connected.")
        await self.nc.publish(self.subject, json.dumps(message).encode())
        await self.nc.flush()

    def shutdown(self):
        if self.loop.is_running():
            if self.nc:
                asyncio.run_coroutine_threadsafe(self.nc.close(), self.loop)
            self.loop.call_soon_threadsafe(self.loop.stop)

    def __del__(self):
        self.shutdown()