import requests, math, json, os, asyncio, logging, time
from datetime import datetime
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from startup import load_HDB_carpark_data, update_realtime_availability_task, parse_ura_feature, load_URA_carpark_data
from ura_availability import get_access_token, update_URA_availability
from token_manager import OneMapTokenManager
from calc_rates import calc_cost
import copy
from typing import Optional

class CarparkService:
    def __init__(self, token_manager: OneMapTokenManager, data_file: str = "./data/combined_carpark_data.json"):
        self.token_manager = token_manager
        self.data_file = data_file
        self.carpark_data = {}
        self.hdb_data = {}
        self.ura_data = {}

    async def startup(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.carpark_data = json.load(f)
            logger.info(f"Loaded {len(self.carpark_data)} carparks")
        else:
            logger.warning(f"Data file {self.data_file} not found")

        # Use deepcopy to isolate availability states
        self.hdb_data = copy.deepcopy(self.carpark_data)
        self.ura_data = copy.deepcopy(self.carpark_data)

        asyncio.create_task(update_realtime_availability_task(self.hdb_data))
        asyncio.create_task(update_URA_availability(self.ura_data))

    async def find_coord(self, query: str) -> tuple:
        token = await self.token_manager.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={query}&returnGeom=Y&getAddrDetails=Y&pageNum=1"

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("results"):
                raise HTTPException(status_code=404, detail="Location not found")
            coords = data["results"][0]
            return float(coords["LATITUDE"]), float(coords["LONGITUDE"])
        except Exception as e:
            logger.error(f"OneMap error: {e}")
            raise HTTPException(status_code=500, detail="Failed to geocode location")

    async def find_nearest_carpark(self, user_lat: float, user_lng: float, limit: int) -> list:
        results = []
        for cp_number, cp_info in self.carpark_data.items():
            carpark = cp_info.copy()

            if carpark["type"] == "HDB":
                carpark["total_lots"] = self.hdb_data.get(cp_number, {}).get("total_lots", 0)
                carpark["available_lots"] = self.hdb_data.get(cp_number, {}).get("available_lots", "N/A")
            elif carpark["type"] == "URA":
                carpark["total_lots"] = self.ura_data.get(cp_number, {}).get("total_lots", 0)
                carpark["available_lots"] = self.ura_data.get(cp_number, {}).get("available_lots", "N/A")

            lat, lng = carpark["coordinates"]
            if lat is None or lng is None:
                continue

            carpark["distance"] = self._haversine(user_lat, user_lng, lat, lng)
            results.append(carpark)

        if not results:
            raise HTTPException(status_code=404, detail="No suitable carparks found")

        return sorted(results, key=lambda c: c["distance"])[:limit] 

    async def find_carpark(
        self, 
        query: str, 
        limit: int = 10, 
        start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None
    ) -> list:
        # Step 1: Find User's coordinates
        user_lat, user_lng = await self.find_coord(query)

        # Step 2: Find nearest carparks
        if not self.carpark_data:
            raise HTTPException(status_code=500, detail="Carpark data not loaded")
        
        list_of_carparks = await self.find_nearest_carpark(user_lat, user_lng, limit)
        # modify carparks in place to include rates
        if start_time and end_time:
            for cp in list_of_carparks:
                try:
                    cp["cost"] = calc_cost(cp, start_time, end_time)
                except Exception as e:
                    cp["cost_note"] = f"Error calculating cost: {e}"
        else:
            for cp in list_of_carparks:
                cp["cost_note"] = "Provide start & end time to estimate cost"
        
        return list_of_carparks

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371e3
        φ1, φ2 = math.radians(lat1), math.radians(lat2)
        dφ = math.radians(lat2 - lat1)
        dλ = math.radians(lon2 - lon1)

        a = math.sin(dφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(dλ / 2) ** 2
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
