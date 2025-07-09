import requests
import time
import os
from dotenv import load_dotenv
import json
import asyncio
from fastapi import HTTPException

load_dotenv()
URA_ACCESS_KEY = os.getenv('URA_ACCESS_KEY')
URA_TOKEN = None
URA_TOKEN_EXPIRY = 0

async def get_access_token():
    global URA_TOKEN, URA_TOKEN_EXPIRY
    if not URA_ACCESS_KEY:
        raise ValueError("URA_ACCESS_KEY is not set in environment variables.")

    if time.time() < URA_TOKEN_EXPIRY:
        return URA_TOKEN

    print("Requesting new URA access token...")
    try:
        token_url = "https://eservice.ura.gov.sg/uraDataService/insertNewToken/v1"
            
        headers = {
            "AccessKey": URA_ACCESS_KEY,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # Mimic a common browser
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://eservice.ura.gov.sg/maps/",
            "Origin": "https://eservice.ura.gov.sg"
            }

        response = requests.get(token_url, headers=headers, timeout=10)
        print(f"URA Token API Response Status: {response.status_code}")
        print(f"URA Token API Raw Response Text: '{response.text}'") # Keep for debugging
        response.raise_for_status()

        token_data = response.json() # This should now parse successfully
            
        # Parse token and expiry from the response (as per your curl output)
        if token_data and token_data.get('Status') == 'Success' and token_data.get('Result'):
            ura_access_token = token_data['Result'] # The token itself
            # The URA token endpoint does NOT return an expiry_timestamp for this token directly in the response.
            # So, set a default expiry (e.g., 1 hour or 30 minutes for safety)
            ura_token_expiry = time.time() + (3600 * 24)
                
            print(f"Successfully obtained URA access token.")
            URA_TOKEN = ura_access_token
            return URA_TOKEN
        else:
            raise ValueError(f"URA access token response indicates failure: {token_data}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to get URA access token: {e}")
        raise HTTPException(status_code=500, detail="Failed to authenticate with URA API.")
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e: # Add JSONDecodeError to catch specific parsing issues
        print(f"Error parsing URA token response: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse URA token response.")


async def update_URA_availability(dictionary):
    
    while True:
        print("Requesting Real-Time URA carpark availability data...")
        try:
            global URA_ACCESS_KEY, URA_TOKEN
            URA_TOKEN = await get_access_token()
            url = "https://eservice.ura.gov.sg/uraDataService/invokeUraDS/v1?service=Car_Park_Availability"
                
            headers = {
                "AccessKey": URA_ACCESS_KEY,
                "Token": URA_TOKEN,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", # Mimic a common browser
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://eservice.ura.gov.sg/maps/",
                "Origin": "https://eservice.ura.gov.sg"
                }

            response = requests.get(url, headers=headers, timeout=10)
            print(f"URA Token API Response Status: {response.status_code}")
            # print(f"URA Token API Raw Response Text: '{response.text}'") # Keep for debugging
            response.raise_for_status()

            token_data = response.json()
                
            if token_data and token_data.get('Status') == 'Success' and token_data.get('Result'):
                print("Successfully obtained URA carpark availability data.")
                result = token_data['Result']
                for carpark in result:
                    carpark_number = carpark.get('carpark_number')
                    if carpark_number and carpark_number in dictionary:
                        dictionary[carpark_number]['available_lots'] = carpark.get('lotsAvailable', 'N/A')
            else:
                raise ValueError(f"URA access token response indicates failure: {token_data}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to get URA access token: {e}")
            raise HTTPException(status_code=500, detail="Failed to authenticate with URA API.")
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e: # Add JSONDecodeError to catch specific parsing issues
            print(f"Error parsing URA token response: {e}")
            raise HTTPException(status_code=500, detail="Failed to parse URA token response.")
        await asyncio.sleep(300)

if __name__ == "__main__":
    data = asyncio.run(update_URA_availability())
    print(f"Loaded {len(data)} carparks from URA API")
    print(list(data[:10]))
