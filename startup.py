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

data = {}

def load_HDB_carpark_data(file_path, carpark_data):
    # carpark_data = {}
    svy21_to_wgs84_transformer = Transformer.from_crs("EPSG:3414", "EPSG:4326", always_xy=True)
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                carpark_number = row['car_park_no']
                address = row['address']
                x_coord = float(row['x_coord'])
                y_coord = float(row['y_coord'])
                lng, lat = svy21_to_wgs84_transformer.transform(x_coord, y_coord)
                carpark_data[carpark_number] = {
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
    return carpark_data

async def update_realtime_availability_task(dictionary):
    while True:
        # print("Updating real-time carpark availability...")
        try:
            carpark_api_url = "https://api.data.gov.sg/v1/transport/carpark-availability"
            carpark_response = requests.get(carpark_api_url)
            carpark_response.raise_for_status()
            carpark_data = carpark_response.json()
            
            if carpark_data and carpark_data.get('items') and carpark_data['items'][0].get('carpark_data'):
                for cp in carpark_data['items'][0]['carpark_data']:
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

# prep_data_file = './HDBCarparkInformation.csv'
# data = load_HDB_carpark_data(prep_data_file, data)
# # update_realtime_availability_task(data)
# print(f"Loaded {len(data)} carparks from {prep_data_file}")
# print(list(data.keys())[:10])
# print(list(data.values())[:10])

def parse_ura_feature(feature, carpark_data):
    """
    Parses a single URA GeoJSON feature to extract carpark details.
    Returns a dictionary of extracted properties and coordinates.
    """
    props = feature.get('properties', {})
    geometry = feature.get('geometry', {})

    carpark_info = {}

    # 1. Parse HTML Description using BeautifulSoup
    description_html = props.get('Description', '')
    if description_html:
        soup = BeautifulSoup(description_html, 'html.parser')
        for row in soup.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                value = cols[1].get_text(strip=True)
                carpark_info[key] = value
    
    carpark_number = carpark_info.get('PP_CODE')
    if not carpark_number:
        # print(f"URA feature missing PP_CODE in description, skipping: {props.get('Name')}")
        return None

    # 2. Extract Coordinates (from Polygon geometry)
    # GeoJSON coordinates are [longitude, latitude, altitude] for a Point or first point of a Polygon
    lat, lng = None, None
    if geometry and geometry.get('type') == 'Polygon':
        coords = geometry.get('coordinates')
        if coords and len(coords) > 0 and len(coords[0]) > 0:
            # Use the first point of the outer ring as the carpark's representative point
            lng = coords[0][0][0]
            lat = coords[0][0][1]
        else:
            print(f"URA carpark {carpark_number} has empty or malformed coordinates, skipping.")
            return None
    elif geometry and geometry.get('type') == 'Point': # In case some URA data is Point
        coords = geometry.get('coordinates')
        if coords and len(coords) >= 2:
            lng = coords[0]
            lat = coords[1]
    
    if lat is None or lng is None:
        # print(f"URA carpark {carpark_number} has no valid latitude/longitude, skipping.")
        return None
    
    if carpark_number in carpark_data:
        carpark_data[carpark_number]['total_lots'] += 1
    else:
        carpark_data[carpark_number] = {
            'carpark_number': carpark_number,
            'address': carpark_info.get('PARKING_PL', 'N/A'),
            'coordinates': (lat, lng),
            'type': 'URA',
            'total_lots': 1,
            'available_lots': 'N/A',
        }

def load_URA_carpark_data(file_path, ura_carparks):
    # ura_carparks = {}
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            geojson_data = json.load(file)
            
            if geojson_data.get('type') == 'FeatureCollection':
                for feature in geojson_data.get('features', []):
                    parse_ura_feature(feature, ura_carparks)
            else:
                print(f"Provided file {file_path} is not a valid GeoJSON FeatureCollection.")
    except FileNotFoundError:
        print(f"Error: The URA GeoJSON file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred while reading the URA GeoJSON file: {e}")
    return ura_carparks

# prep_data_file_ura = './URAParkingLotGEOJSON.geojson'
# data = load_URA_carpark_data(prep_data_file_ura, data)
# print(f"Loaded {len(data)} URA carparks from {prep_data_file_ura}")
# print(list(data.keys())[:10])
# print(list(data.values())[:10])

