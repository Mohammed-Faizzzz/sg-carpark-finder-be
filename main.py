from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging
import json
import os
import asyncio
from startup import load_HDB_carpark_data, update_realtime_availability_task, parse_ura_feature, load_URA_carpark_data

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

ONEMAP_USERNAME = os.getenv('ONEMAP_USERNAME')
ONEMAP_PASSWORD = os.getenv('ONEMAP_PASSWORD')
onemap_access_token = None
onemap_token_expiry = 0

# import method from prep_data.py to get carpark data
# from prep_data import load_carpark_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

carpark_data = {}
real_time_data = {}

app = FastAPI(
    title="Singapore Carpark Finder API",
    description="API to find the nearest available public carpark by postcode in Singapore.",
    version="1.0.0",
)

# Configure CORS
# For development, allow all origins. In production, restrict this to frontend's domain.
origins = [
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

async def get_onemap_token():
    global onemap_access_token, onemap_token_expiry
    import time

    # Check if token is still valid
    if onemap_access_token and onemap_token_expiry > time.time() + 300: # Refresh if less than 5 min to expiry
        logger.info("Using existing OneMap access token.")
        return onemap_access_token

    logger.info("Requesting new OneMap access token...")
    try:
        token_url = "https://www.onemap.gov.sg/api/auth/post/getToken" # Confirm this URL with OneMap docs
        response = requests.post(token_url, json={
            "email": ONEMAP_USERNAME,
            "password": ONEMAP_PASSWORD
        })
        response.raise_for_status()
        token_data = response.json()
        print("\nToken Response Data:", token_data)
        
        onemap_access_token = token_data.get('access_token')
        onemap_token_expiry = token_data.get('expiry_timestamp')
        
        if onemap_access_token and onemap_token_expiry:
            # Convert milliseconds to seconds for Python's time.time()
            onemap_token_expiry = int(onemap_token_expiry) / 1000.0
            logger.info(f"Successfully obtained OneMap access token. Expires at: {time.ctime(onemap_token_expiry)}")
            return onemap_access_token
        else:
            raise ValueError("Access token or expiry missing from OneMap response.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get OneMap access token: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with OneMap API.")
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Error parsing OneMap token response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse OneMap token response.")

def get_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the distance between two geographical points (latitude, longitude)
    using the Haversine formula.

    Args:
        lat1 (float): Latitude of the first point.
        lon1 (float): Longitude of the first point.
        lat2 (float): Latitude of the second point.
        lon2 (float): Longitude of the second point.

    Returns:
        float: The distance between the two points in meters.
    """
    R = 6371e3  # Earth's radius in meters
    
    # Convert latitudes and longitudes from degrees to radians
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)  # Difference in latitudes
    Δλ = math.radians(lon2 - lon1)  # Difference in longitudes

    # Haversine formula calculation
    a = math.sin(Δφ / 2) * math.sin(Δφ / 2) + \
        math.cos(φ1) * math.cos(φ2) * \
        math.sin(Δλ / 2) * math.sin(Δλ / 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    d = R * c  # Distance in meters
    return d
    
@app.on_event("startup")
async def startup_event():
    """
    Loads static carpark data (HDB & URA) and starts the real-time availability background task.
    This runs once when the FastAPI application starts.
    """
    global carpark_data
    global real_time_data
    
    # Load URA carpark data from GeoJSON file
    prep_data_file_ura = './URAParkingLotGEOJSON.geojson'
    carpark_data = load_URA_carpark_data(prep_data_file_ura, carpark_data)

    # Load HDB static data using the imported function
    hdb_csv_path = './HDBCarparkInformation.csv'
    carpark_data = load_HDB_carpark_data(hdb_csv_path, carpark_data)
    real_time_data = carpark_data.copy()

    # Start the background task to update real-time availability
    asyncio.create_task(update_realtime_availability_task(real_time_data))


@app.get("/find-carpark")
async def find_carpark(postcode: str = Query(..., min_length=6, max_length=6, regex="^[0-9]{6}$")):
# async def find_carpark():
    # postcode = "341119"
    logger.info(f"Received request for postcode: {postcode}")

    user_lat, user_lng = None, None

    # Get OneMap access token
    token = await get_onemap_token()
    headers = {"Authorization": f"Bearer {token}"} # Use the obtained token in the header

    # 1. Get Postcode Coordinates from OneMap API
    try:
        onemap_url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postcode}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        onemap_response = requests.get(onemap_url, headers=headers)
        onemap_response.raise_for_status()
        onemap_data = onemap_response.json()

        if onemap_data and onemap_data.get('results'):
            first_result = onemap_data['results'][0]
            user_lat = float(first_result.get('LATITUDE'))
            user_lng = float(first_result.get('LONGITUDE'))
            if user_lat is None or user_lng is None:
                 raise ValueError("Latitude or Longitude missing from OneMap response.")
            logger.info(f"OneMap: Postcode {postcode} geocoded to {user_lat}, {user_lng}")
        else:
            logger.warning(f"OneMap: No results found for postcode {postcode}")
            raise HTTPException(status_code=404, detail="Postcode not found or invalid.")
    except requests.exceptions.RequestException as e:
        logger.error(f"OneMap API request failed: {e}")
        raise HTTPException(status_code=500, detail="Error connecting to OneMap API.")
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Error processing OneMap data for {postcode}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred processing postcode data.")

    # 2. Calculate Nearest Available Carparks
    searchable_carparks = []
    
    if not carpark_data:
        logger.warning("Global carpark_data is empty. Check startup loading.")
        raise HTTPException(status_code=500, detail="Carpark data not loaded or is empty.")

    for cp_number, cp_info in carpark_data.items():
        carpark = cp_info.copy() # Make a copy to avoid modifying the global dict during iteration
        
        # Determine if carpark should be included and its status
        if carpark['type'] == 'HDB':
            carpark['total_lots'] = real_time_data.get(cp_number, {}).get('total_lots', 0)
            carpark['available_lots'] = real_time_data.get(cp_number, {}).get('available_lots', 'N/A')

        carpark_lat, carpark_lng = carpark['coordinates']

        # Calculate distance
        distance = get_distance(user_lat, user_lng, carpark_lat, carpark_lng)
        carpark['distance'] = distance
        searchable_carparks.append(carpark)

    if not searchable_carparks:
        # print(f"No suitable carparks found near postcode {postcode} (either no available HDB or no nearby URA).")
        raise HTTPException(status_code=404, detail="No suitable carparks found near this postcode.")

    # 3. Return Nearest Carpark Details
    searchable_carparks.sort(key=lambda cp: cp['distance'])
    
    top_n_carparks = searchable_carparks[:10]
    
    # print(f"Returning top {len(top_n_carparks)} nearest suitable carparks for {postcode}.")
    print(top_n_carparks)
    return top_n_carparks
    