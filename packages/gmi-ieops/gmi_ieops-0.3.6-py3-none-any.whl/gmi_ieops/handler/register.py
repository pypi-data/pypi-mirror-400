"""
Register Module - Service registration to IEOPS proxy

Handles service registration, heartbeat, and graceful unregistration.
"""

import os
import asyncio
from typing import Optional, List

from ..utils.util import randstr, APP_ID, get_socket_path
from ..utils.log import uvicorn_logger
from ..config import env
from .client import (
    Payload,
    async_post,
    _CONNECTORS,
    _SYNC_SESSION,
)


class Register:
    """Service registration manager for IEOPS proxy"""
    
    def __init__(self):
        self._appinfo = self._app_info()
        
    def _app_info(self):
        # Get socket path using get_socket_path utility
        socket_path = get_socket_path()
        self._tokens = [randstr(8) for _ in range(env.model.concurrency)]
        return {
            "id": APP_ID,
            "server_socket": socket_path,
            "max_concurrent_reqs": env.model.concurrency,
            "endpoint": env.app.name,
            "weight": 1,
        }

    async def _unregister_old(self):
        """Unregister old registrations on startup, clean up possible zombie registrations
        Clean by socket directory to avoid affecting services with same endpoint but different pods
        """
        socket_path = get_socket_path()
        socket_dir = os.path.dirname(socket_path) or os.getcwd()
        uvicorn_logger.info("Unregistering old models in socket_dir {} from IEOPS proxy (if exists)...".format(socket_dir))
        # Cancel old registrations in the same directory (same pod restart has same directory but different socket ID)
        await async_post(Payload(path="api/model/unregister", payload={"socket_dir": socket_dir}), max_retries=0)

    async def _unregister(self):
        """Unregister current registration on stop"""
        uvicorn_logger.info("Unregistering {} from IEOPS proxy...".format(env.app.name))
        await async_post(Payload(path="api/model/unregister", payload={"id": APP_ID}), max_retries=1)

    async def register(self):
        if not env.register.enabled:
            uvicorn_logger.info("Register is disabled, skipping...")
            return
        uvicorn_logger.info("Registering {} to IEOPS proxy...".format(env.app.name))
        try:
            # Clean old registrations on startup
            await self._unregister_old()
            while True:
                await async_post(Payload(path="api/model/register", payload=self._appinfo))
                await asyncio.sleep(env.register.interval)
        except asyncio.CancelledError:
            uvicorn_logger.info("Register stopped")
            raise
        finally:
            # Unregister on stop
            try:
                await self._unregister()
            except Exception as e:
                uvicorn_logger.warning(f"Failed to unregister: {e}")
            # Close all connectors
            await cleanup_connectors()


async def cleanup_connectors():
    """Clean up all HTTP connectors"""
    for connector in _CONNECTORS.values():
        if connector is not None:
            await connector.close()
    if _SYNC_SESSION is not None:
        _SYNC_SESSION.close()
