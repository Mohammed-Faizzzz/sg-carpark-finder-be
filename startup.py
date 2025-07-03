# Runs during application startup
# Import HDB carpark data and URA carpark data and store both in a dictionary
# Call realtime carpark availability API to get the latest carpark availability data

import csv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import math
import logging
import json
import os
from bs4 import BeautifulSoup
from pyproj import Transformer
import asyncio

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# A single dictionary to hold both HDB and URA carpark data
data = {}

svy21_to_wgs84_transformer = Transformer.from_crs("EPSG:3414", "EPSG:4326", always_xy=True)

def load_HDB_carpark_data(file_path, data):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                carpark_number = row['car_park_no']
                address = row['address']
                x_coord = float(row['x_coord'])
                y_coord = float(row['y_coord'])
                lng, lat = svy21_to_wgs84_transformer.transform(x_coord, y_coord)
                data[carpark_number] = {
                    'carpark_number': carpark_number,
                    'address': address,
                    'coordinates': (lat, lng),
                    'type': 'HDB',
                    'total_lots': 0,
                    'available_lots': 'N/A',
                }
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return data

async def update_realtime_availability_task(dictionary):
    # This dictionary is different from data, dictionary is used to update real-time availability
    # change variable names to indicate this is HDB carpark data
    while True:
        # print("Updating real-time carpark availability...")
        try:
            carpark_api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
            carpark_response = requests.get(carpark_api_url)
            carpark_response.raise_for_status()
            real_time_carpark_data = carpark_response.json()
            
            if real_time_carpark_data and real_time_carpark_data.get('items') and real_time_carpark_data['items'][0].get('carpark_data'):
                for cp in real_time_carpark_data['items'][0]['carpark_data']:
                    carpark_number = cp.get('carpark_number')
                    carpark_info = cp.get('carpark_info')[0]
                    # print(f"Processing carpark {carpark_number} with info: {carpark_info}")
                    total_lots, available_lots = carpark_info.get('total_lots'), carpark_info.get('lots_available')
                    # print(f"Processing carpark {carpark_number}: Total Lots = {total_lots}, Available Lots = {available_lots}")
                    if carpark_number in dictionary:
                        dictionary[carpark_number]['total_lots'] = int(total_lots) if total_lots else 0
                        dictionary[carpark_number]['available_lots'] = int(available_lots) if available_lots else 'N/A'
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch real-time carpark availability: {e}")
        except Exception as e:
            print(f"Error processing real-time availability data: {e}")
        await asyncio.sleep(60)

def parse_ura_feature(feature, data):
    """
    Parses a single URA GeoJSON feature to extract carpark details.
    Returns a dictionary of extracted properties and coordinates.
    """

    # 1. Parse carpark number
    # print(feature)
    carpark_number = feature.get('ppCode')
    # print(f"Processing URA carpark: {carpark_number}")
    if not carpark_number:
        # print(f"URA feature missing PP_CODE in description, skipping: {props.get('Name')}")
        return None
    vehicleCat = feature.get('vehCat')
    if vehicleCat == "Heavy Vehicle" or vehicleCat == "Motorcycle":
        return None # Skip heavy vehicle carparks and motorcycles for now

    # 2. Extract Coordinates (from Polygon geometry)
    # GeoJSON coordinates are [longitude, latitude, altitude] for a Point or first point of a Polygon
    lat, lng = None, None
    geometries = feature.get('geometries')
    if geometries and len(geometries) > 0 and geometries[0].get('coordinates'):
        coords_str = geometries[0]['coordinates']
        try:
            x_coord, y_coord = map(float, coords_str.split(','))
            lng, lat = svy21_to_wgs84_transformer.transform(x_coord, y_coord)
        except ValueError:
            logger.warning(f"URA rate item {pp_code}: Malformed coordinates '{coords_str}', skipping coord conversion.")       
    
    # 3. Construct the carpark data dictionary
    if carpark_number in data:
        # print(f"Updating existing URA carpark {carpark_number} with new rate data.")
        new_rate = {
            'veh_cat': feature.get('vehCat'),
            'start_time': feature.get('startTime'),
            'end_time': feature.get('endTime'),

            'weekday': {
                'min_duration': feature.get('weekdayMin'),
                'rate': feature.get('weekdayRate'),
            },
            'saturday': {
                'min_duration': feature.get('satdayMin'),
                'rate': feature.get('satdayRate'),
            },
            'sunday_ph': {
                'min_duration': feature.get('sunPHMin'),
                'rate': feature.get('sunPHRate'),
            }
        }
        # If carpark already exists, append the new rate to its rates list
        if 'rates' in data[carpark_number]:
            data[carpark_number]['rates'].append(new_rate) 
        if 'total_lots' not in data[carpark_number]:
            data[carpark_number]['total_lots'] = feature.get('parkCapacity', 0)    
    else:
        data[carpark_number] = {
            'carpark_number': carpark_number,
            'address': feature.get('ppName', 'N/A'),
            'coordinates': (lat, lng),
            'type': 'URA',
            'total_lots': feature.get('parkCapacity', 0),
            'available_lots': 'N/A',
            'rates': [{ # Nested dictionary to hold all rate-related details
                'veh_cat': feature.get('vehCat'),
                'start_time': feature.get('startTime'), # Daily start time for this rate block (e.g., "07.00 AM")
                'end_time': feature.get('endTime'),   # Daily end time for this rate block (e.g., "08.30 AM")

                'weekday': {
                    'min_duration': feature.get('weekdayMin'), # e.g., "0 mins"
                    'rate': feature.get('weekdayRate'),       # e.g., "$1.20 per min_duration"
                },
                'saturday': {
                    'min_duration': feature.get('satdayMin'),
                    'rate': feature.get('satdayRate'),
                },
                'sunday_ph': {
                    'min_duration': feature.get('sunPHMin'),
                    'rate': feature.get('sunPHRate'),
                }
            }]
        }

def load_URA_carpark_data(file_path, data):
    # ura_carparks = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            ura_data = json.load(file)
            # print(ura_data.get('Status', 'No Status Found'))
            
            if ura_data.get('Status') == 'Success' and ura_data.get('Result'):
                # print(ura_data['Result'][0])
                for item in ura_data['Result']:
                    parse_ura_feature(item, data)
            else:
                print(f"Provided file {file_path} is not a valid GeoJSON FeatureCollection.")
    except FileNotFoundError:
        print(f"Error: The URA GeoJSON file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred while reading the URA GeoJSON file: {e}")
    return data

# Load all the data, then save it as a json file
prep_data_file = './HDBCarparkInformation.csv'
data = load_HDB_carpark_data(prep_data_file, data)

prep_data_file_ura = './carpark_rates.json'
data = load_URA_carpark_data(prep_data_file_ura, data)

# Check for None values in coordinates
for carpark_number, carpark_info in data.items():
    if carpark_info['coordinates'][0] is None or carpark_info['coordinates'][0] is None:
        # del data[carpark_number]
        print(f"Carpark {carpark_number} has invalid coordinates: {carpark_info['coordinates']}")
# Save the combined data to a JSON file
output_file = './combined_carpark_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
