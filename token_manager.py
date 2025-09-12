import requests, math, json, os, asyncio, logging, time
from datetime import datetime
from startup import update_realtime_availability_task, load_HDB_carpark_data, load_URA_carpark_data, parse_ura_feature
from ura_availability import update_URA_availability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os
from dotenv import load_dotenv
load_dotenv()

ONEMAP_USERNAME = os.getenv('ONEMAP_USERNAME')
ONEMAP_PASSWORD = os.getenv('ONEMAP_PASSWORD')
onemap_access_token = None
onemap_token_expiry = 0


class OneMapTokenManager:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._access_token = None
        self._expiry = 0

    async def get_token(self) -> str:
        if self._access_token and self._expiry > time.time() + 300:
            logger.info("Using cached OneMap token.")
            return self._access_token

        logger.info("Requesting new OneMap token...")
        url = "https://www.onemap.gov.sg/api/auth/post/getToken"
        try:
            resp = requests.post(url, json={"email": self.username, "password": self.password})
            resp.raise_for_status()
            data = resp.json()
            token = data.get("access_token")
            expiry = data.get("expiry_timestamp")

            if not token or not expiry:
                raise ValueError("Missing token or expiry in OneMap response")

            self._access_token = token
            self._expiry = int(expiry) / 1000.0
            logger.info(f"OneMap token obtained, expires at {time.ctime(self._expiry)}")
            return token
        except Exception as e:
            logger.error(f"Failed to get OneMap token: {e}")
            raise HTTPException(status_code=500, detail="OneMap authentication failed")
