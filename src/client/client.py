from httpx import AsyncClient, Timeout, Limits
from typing import Optional, Dict
from uuid import UUID
import asyncio

from core.logger import logger

class APIClient:
  def __init__(
    self,
    base_url: str,
    device_id: UUID,
    timeout: float = 30.0,
    max_retries: int = 3,
    headers: Optional[Dict] = None
  ):
    self.base_url = base_url
    self.device_id = device_id
    self.timeout = timeout
    self.max_retries = max_retries
    self.headers = headers

    if not headers:
      self.headers = {
        "Content-Type": "application/json",
        "X-Device-ID": device_id
      }

    self.__client = AsyncClient(
      timeout=Timeout(timeout),
      limits=Limits(max_connections=10, max_keepalive_connections=5)
    ) 

    logger.info(f"Initialized API client for device {device_id}")