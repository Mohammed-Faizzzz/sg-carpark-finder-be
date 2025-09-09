# Singapore Carpark Finder – Backend

FastAPI backend that finds the **nearest public carparks in Singapore** (HDB + URA) to a user-provided **address/building/postcode**, and enriches them with **real-time availability**. It also includes helpers for **parking cost calculation** (HDB special rates), though no pricing endpoint is exposed yet.

---

## Table of Contents

* [Features](#features)
* [Architecture & Data Flow](#architecture--data-flow)
* [API Reference](#api-reference)
* [Quick Start](#quick-start)
* [Configuration](#configuration)
* [Data Inputs](#data-inputs)
* [Background Jobs](#background-jobs)
* [Calculating Rates (internal helpers)](#calculating-rates-internal-helpers)
* [CORS](#cors)
* [Logging](#logging)
* [Troubleshooting](#troubleshooting)
* [Project Structure](#project-structure)
* [License](#license)

---

## Features

* 🔎 Geocodes a user’s **search query** (postcode/building/address) via **OneMap** and returns **nearest carparks**.
* 🚗 Merges **static HDB carparks** (CSV) and **URA carparks** (JSON) into one dataset.
* 📡 Updates **real-time availability** for:

  * HDB via `api.data.gov.sg` (every 60s)
  * URA via URA Data Service (every 300s)
* 📏 Computes distance using the **Haversine** formula to sort by proximity.
* 🧮 Includes utilities to **estimate HDB parking cost** with special rate tables (internal).

---

## Architecture & Data Flow

1. **Startup (`startup.py`)**

   * Loads HDB static carparks from `HDBCarparkInformation.csv`.
   * Loads URA carparks + rate metadata from `carpark_rates.json` and merges into a single dict.
   * Writes merged result to `combined_carpark_data.json`.

2. **App Boot (`main.py`)**

   * Reads `combined_carpark_data.json` into memory (`carpark_data`).
   * Starts two background tasks:

     * `update_realtime_availability_task` → HDB availability (every 60s).
     * `update_URA_availability` → URA availability (every 300s).

3. **Request Handling**

   * `GET /find-carpark`:

     * Uses **OneMap** to geocode `search_query` → `(lat, lng)`.
     * Computes distance to each known carpark.
     * Attaches the latest **available/total lots** (from live caches).
     * Returns the **nearest** carparks (default top 10).

---

## API Reference

### `GET /find-carpark`

Find the nearest carparks to a search string (postcode/building/address).

**Query params**

* `search_query` *(string, required)*: e.g. `"Raffles Place"`, `"018989"`.
* `limit` *(int, optional, default=10, 1–50)*: max number of results to return.

  > Note: implementation currently slices top 10 after sorting; keep `limit<=10` for consistency.

**Response** → `200 OK`
Array of carpark objects (sorted by distance ascending):

```json
[
  {
    "carpark_number": "HLM",
    "address": "BLK 531A HONG LIM COMPLEX",
    "coordinates": [1.285691, 103.845402],
    "type": "HDB",
    "total_lots": 500,
    "available_lots": 123,
    "distance": 145.23,
    "rates": [
      {
        "veh_cat": "Car",
        "start_time": "07:00 AM",
        "end_time": "09:30 AM",
        "weekday": { "min_duration": "0 mins", "rate": "$1.20" },
        "saturday": { "min_duration": "0 mins", "rate": "$1.20" },
        "sunday_ph": { "min_duration": "0 mins", "rate": "$0.60" }
      }
    ]
  }
]
```

**Errors**

* `404` — Location not found by OneMap, or no suitable carparks nearby.
* `500` — Issues with OneMap/URA/HDB APIs, token parsing, or missing data.

**Example**

```bash
curl -G 'http://localhost:8000/find-carpark' \
  --data-urlencode 'search_query=018989' \
  --data-urlencode 'limit=10'
```

---

### `GET /health`

Simple liveness probe.

**Response**

```json
{ "status": "ok", "timestamp": "2025-09-09T12:34:56.789012" }
```

---

## Quick Start

### Prerequisites

* Python 3.10+ (recommended)
* `uvicorn` for local dev
* API keys (see **Configuration**)
* Data files (see **Data Inputs**)

### Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, include at least:

```
fastapi
uvicorn[standard]
python-dotenv
requests
beautifulsoup4
pyproj
```

### Configure environment

Create a `.env` in the project root:

```
# OneMap (https://www.onemap.gov.sg/)
ONEMAP_USERNAME=your-email@example.com
ONEMAP_PASSWORD=your-onemap-password

# URA (https://www.ura.gov.sg/)
URA_ACCESS_KEY=your-ura-access-key
```

### Prepare data

Place the following files in the project root (or update paths in `startup.py`):

* `HDBCarparkInformation.csv`
* `carpark_rates.json`

On first run, these are merged into `combined_carpark_data.json`.

### Run

```bash
uvicorn main:app --reload --port 8000
```

Open the interactive docs:

* Swagger UI: `http://localhost:8000/docs`
* ReDoc: `http://localhost:8000/redoc`

---

## Configuration

Environment variables are loaded via `python-dotenv` in both `main.py` and `ura_availability.py`.

* **OneMap**

  * `ONEMAP_USERNAME`, `ONEMAP_PASSWORD`
  * A bearer token is fetched at runtime and **cached in memory** until \~5 minutes before expiry.

* **URA**

  * `URA_ACCESS_KEY`
  * Token fetched via `insertNewToken/v1`, cached in memory. Availability fetched via `Car_Park_Availability`.

> Tokens are stored in-process only; if you run multiple replicas, each will manage its own token cache.

---

## Data Inputs

* **HDB static carparks**: `HDBCarparkInformation.csv`
  Columns used: `car_park_no`, `address`, `x_coord`, `y_coord` (SVY21).
  Converted to WGS84 lat/lng using `pyproj` (EPSG:3414 → EPSG:4326).

* **URA carparks & rates**: `carpark_rates.json`
  Parsed into carpark entries, including a `rates` list per carpark with weekday/saturday/sunday\_ph blocks when available.
  Coordinates are also converted from SVY21 → WGS84.

* **Merged output**: `combined_carpark_data.json` (generated at startup).

---

## Background Jobs

* **HDB Availability** (`update_realtime_availability_task`)

  * Source: `https://api.data.gov.sg/v1/transport/carpark-availability`
  * Interval: **60 seconds**
  * Updates `total_lots` and `available_lots` for carparks present in the merged dictionary.

* **URA Availability** (`update_URA_availability`)

  * Auth: `insertNewToken/v1` → `invokeUraDS/v1?service=Car_Park_Availability`
  * Interval: **300 seconds**
  * Updates `available_lots` for matching URA carparks.

> Both tasks run with `asyncio.create_task(...)` on FastAPI startup and maintain **in-memory** views (`real_time_data_hdb`, `real_time_data_ura`).

---

## Calculating Rates (internal helpers)

File: `calc_rates.py`

* **HDB**

  * `calc_hdb_cost(carpark_code, start_time, end_time, overnight=False)`

    * Default rate: \$0.60 / 30 mins unless a **special rate** exists for that carpark code (see `special_rates_HDB`).
    * Handles grace period (≤ 15 mins → \$0).
    * Splits across rate windows on the same day. For cross-day stays, call per day.

* **URA**

  * Stubs/helpers exist (`parse_*`, etc.) to read rate blocks per `weekday/saturday/sunday_ph`. A full `calc_ura_cost(...)` is not yet implemented in the repo.

> No public pricing endpoint is currently exposed; these are utilities to be used by a future API method.

---

## CORS

Configured in `main.py`:

```python
origins = [
  "*",
  "https://sg-carpark-finder-fe.vercel.app",
  "https://sg-carpark-finder-fe-faizs-projects-f7b13609.vercel.app",
  "https://sg-carpark-finder-fe-git-main-faizs-projects-f7b13609.vercel.app"
]
```

* For production, **restrict** this to your frontend domains only.

---

## Logging

* Uses Python `logging` at `INFO` level by default.
* Logs token retrieval, geocoding hits/misses, data loading, and periodic availability updates.
* API errors propagate as `HTTPException` with appropriate status codes.

---

## Troubleshooting

* **`500: Carpark data not loaded or is empty`**

  * Ensure `HDBCarparkInformation.csv` and `carpark_rates.json` exist and are readable.
  * Confirm `startup.py` generated `combined_carpark_data.json` without JSON errors.

* **`404: Location not found or invalid`**

  * Verify `search_query` is a valid SG address/postcode.
  * Check OneMap credentials in `.env`.

* **OneMap token errors**

  * Double check `ONEMAP_USERNAME` / `ONEMAP_PASSWORD`.
  * OneMap endpoints occasionally change auth semantics; review response logs in console.

* **URA token/availability errors**

  * Confirm `URA_ACCESS_KEY`.
  * URA rate limits may apply; ensure intervals aren’t reduced below defaults.

* **Coordinates show as `null`**

  * Some URA features may have malformed or missing coordinates; these are skipped/logged during parsing.

---

## Project Structure

```
.
├── main.py                     # FastAPI app, endpoints, CORS, token mgmt, distance calc
├── startup.py                  # Load & merge HDB/URA static data; write combined JSON
├── ura_availability.py         # URA token + availability polling
├── calc_rates.py               # HDB pricing helpers + specials table
├── HDBCarparkInformation.csv   # (input) HDB static dataset
├── carpark_rates.json          # (input) URA carpark rates & metadata
├── combined_carpark_data.json  # (generated) merged static dataset
├── .env                        # secrets (OneMap, URA)
└── requirements.txt
```

---

### Notes & Next Steps

* Add a `/pricing` endpoint to expose `calc_hdb_cost` (and future `calc_ura_cost`).
* Cache geocoding responses per `search_query` to reduce OneMap calls.
* Add pagination/`limit` handling parity (currently fixed to top 10 slice).
* Add unit tests for data parsing and rate calculation.
