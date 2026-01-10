from httpx import AsyncClient, Timeout, Limits, HTTPStatusError
from typing import Optional, Dict, List
from uuid import UUID
import datetime
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

  async def request(
    self,
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None
  ):
    """Make HTTP request."""
    url = f"{self.base_url}/{endpoint.lstrip("/")}"

    for attempt in range(self.max_retries):
      try:
        response = await self.__client.request(
          method=method,
          url=url,
          data=data,
          params=params
        )
        response.raise_for_status()
        return response.json() if response.text else None 
      except HTTPStatusError as e:
        logger.error(f"HTTP error: {e}")
        if attempt == self.max_retries-1:
          raise
        await asyncio.sleep(2 ** attempt)
      
      except Exception as e:
        logger.error(f"Request failed: {e}")
        raise

    return None

  async def send_detection(
    self,
    endpoint: str,
    detections: List[Dict]
  ):
    """Send detection over HTTP request."""
    
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    
    payload = {
      "timestamp": timestamp
    }

    try:
      result = await self.request("POST", endpoint, data=payload)
      if result:
        logger.info(f"Successfully sent {len(detections)} detection(s)")
        return True
      return False
    except Exception as e:
      logger.error(f"Failed to send detection: {e}")
      return False
    
  async def close(self):
    """Close the HTTP client."""
    await self.__client.aclose()

  async def __aenter__(self):
    return self
  
  async def __aexit__(self):
    await self.close()

  