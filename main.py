from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests, math, json, os, asyncio, logging, time
from datetime import datetime
from dotenv import load_dotenv
from startup import update_realtime_availability_task, load_HDB_carpark_data, load_URA_carpark_data, parse_ura_feature
from ura_availability import update_URA_availability
from token_manager import OneMapTokenManager
from carpark_service import CarparkService
from contextlib import asynccontextmanager
from typing import Optional


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

onemap_manager = OneMapTokenManager(
    os.getenv("ONEMAP_USERNAME"),
    os.getenv("ONEMAP_PASSWORD"),
)
carpark_service = CarparkService(onemap_manager)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await carpark_service.startup()
    yield
    # Shutdown (if needed)
    
app = FastAPI(
    title="Singapore Carpark Finder API",
    description="API to find the nearest available public carpark by postcode in Singapore.",
    version="1.0.0",
    lifespan=lifespan
)

origins = [
    "*",
    "https://sg-carpark-finder-fe.vercel.app",
    "https://sg-carpark-finder-fe-faizs-projects-f7b13609.vercel.app",
    "https://sg-carpark-finder-fe-git-main-faizs-projects-f7b13609.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/find-carpark")
async def find_carpark(search_query: str, limit: int = Query(10, gt=0, le=50), start_time: Optional[datetime] = None, 
        end_time: Optional[datetime] = None):
    logger.info(f"search_query:  {search_query}")
    logger.info(f"Start time: {start_time}, End time: {end_time}")
    res = await carpark_service.find_carpark(search_query, limit, start_time, end_time)
    # logger.info(res)
    return res


@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    