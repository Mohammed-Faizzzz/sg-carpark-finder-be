import datetime
from datetime import datetime, date, time, timedelta
import math
import unittest # Import unittest for testing

# --- YOUR special_rates_HDB DICTIONARY (as provided by you) ---
special_rates_HDB = {
    "ACB": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "09:59:59", "rate_per_half_hour": 1.20},
            {"start": "10:00:00", "end": "16:59:59", "rate_per_half_hour": 1.40},
            {"start": "17:00:00", "end": "17:59:59", "rate_per_half_hour": 0.80},
            {"start": "18:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "07:59:59", "rate_per_half_hour": 1.20},
            {"start": "08:00:00", "end": "16:59:59", "rate_per_half_hour": 1.40},
            {"start": "17:00:00", "end": "18:59:59", "rate_per_half_hour": 0.80},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
            {"start": "08:00:00", "end": "18:59:59", "rate_per_half_hour": 0.80},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "BBB": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "BRB1": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "CY": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "09:59:59", "rate_per_half_hour": 1.20},
            {"start": "10:00:00", "end": "16:59:59", "rate_per_half_hour": 1.40},
            {"start": "17:00:00", "end": "17:59:59", "rate_per_half_hour": 0.80},
            {"start": "18:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "07:59:59", "rate_per_half_hour": 1.20},
            {"start": "08:00:00", "end": "16:59:59", "rate_per_half_hour": 1.40},
            {"start": "17:00:00", "end": "18:59:59", "rate_per_half_hour": 0.80},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
            {"start": "08:00:00", "end": "18:59:59", "rate_per_half_hour": 0.80},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "DUXM": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "HLM": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "KAB": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "KAM": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "KAS": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "PRM": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SLS": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SR1": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SR2": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "TPM": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "UCS": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "WCB": {
        "weekdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "06:59:59", "rate_per_half_hour": 0.60},
            {"start": "07:00:00", "end": "16:59:59", "rate_per_half_hour": 1.20},
            {"start": "19:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SE21": {
        "weekdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SE22": {
        "weekdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [{"start": "00:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "SE24": {
        "weekdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "09:59:59", "rate_per_half_hour": 0.60},
            {"start": "10:00:00", "end": "21:59:59", "rate_per_half_hour": 0.80},
            {"start": "22:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "MP14": {
            "weekdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "saturdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "sundays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}]
    },
    "MP15": {
            "weekdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "saturdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "sundays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}]
    },
    "MP16": {
            "weekdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "saturdays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
            "sundays": [
                {"start": "00:00:00", "end": "07:59:59", "rate_per_half_hour": 0.60},
                {"start": "08:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
                {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}]
    },
    "HG9": {
        "weekdays": [
            {"start": "00:00:00", "end": "10:59:59", "rate_per_half_hour": 0.60},
            {"start": "11:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "HG9T": {
        "weekdays": [
            {"start": "00:00:00", "end": "10:59:59", "rate_per_half_hour": 0.60},
            {"start": "11:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "HG15": {
        "weekdays": [
            {"start": "00:00:00", "end": "10:59:59", "rate_per_half_hour": 0.60},
            {"start": "11:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    },
    "HG16": {
        "weekdays": [
            {"start": "00:00:00", "end": "10:59:59", "rate_per_half_hour": 0.60},
            {"start": "11:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "saturdays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
        "sundays": [
            {"start": "00:00:00", "end": "08:59:59", "rate_per_half_hour": 0.60},
            {"start": "09:00:00", "end": "19:59:59", "rate_per_half_hour": 0.80},
            {"start": "20:00:00", "end": "23:59:59", "rate_per_half_hour": 0.60}],
    }
}
# Placeholder for URA cost calculation
def calc_ura_cost(carpark_info, start_dt, end_dt):
    # This function will be implemented later
    return 0.0

def get_day_type(date_obj):
    """Determines if a given date is a weekday, Saturday, or Sunday."""
    day_of_week = date_obj.weekday() # Monday is 0, Sunday is 6
    if day_of_week < 5:
        return 'weekdays'
    elif day_of_week == 5:
        return 'saturdays'
    else:
        return 'sundays'

def get_rate_for_time_slot(time_to_check: time, day_rates: list, default_rate: float) -> float:
    """
    Finds the applicable rate for a specific time within a list of rate segments.
    """
    for segment in day_rates:
        segment_start_time = datetime.strptime(segment["start"], "%H:%M:%S").time()
        segment_end_time = datetime.strptime(segment["end"], "%H:%M:%S").time()

        # Handle segments that cross midnight (e.g., 22:00:00 to 07:00:00)
        # Assuming segments cover the entire 24-hour period within a day,
        # or that time_to_check will always fall into one.
        if segment_start_time <= time_to_check <= segment_end_time:
            return segment["rate_per_half_hour"]
    
    # If no specific segment matches (e.g., if a gap exists in definitions), return default
    return default_rate


def calc_hdb_cost(carpark_info, parking_start_dt: datetime, parking_end_dt: datetime) -> float:
    """
    Calculates the HDB parking cost for a given car park and datetime duration.
    Assumes parking_start_dt and parking_end_dt are full datetime objects.
    This function calculates for a single contiguous period (max 24 hours from start_dt's midnight).
    """
    total_cost = 0.0
    standard_rate_per_half_hour = 0.60 # Default standard rate for HDB
    
    # Apply 10-minute grace period based on total duration before any billing
    duration_total_minutes = (parking_end_dt - parking_start_dt).total_seconds() / 60
    if duration_total_minutes <= 10:
        return 0.0

    # Determine the type of day for the start of the current parking period
    day_type = get_day_type(parking_start_dt.date())
    
    # Get the actual car park number from carpark_info
    carpark_number = carpark_info.get('number', carpark_info.get('id'))
    if carpark_number is None:
        raise ValueError("Carpark info must contain a 'number' or 'id' key.")

    # --- Standard Carpark Calculation ---
    if carpark_number not in special_rates_HDB:
        # Standard carparks are billed per half-hour, rounded up.
        num_half_hours = (parking_end_dt - parking_start_dt).total_seconds() / 1800
        billable_half_hours = math.ceil(num_half_hours)
        total_cost = billable_half_hours * standard_rate_per_half_hour
        return total_cost

    # --- Special Carpark Calculation ---
    rates_for_day_type = special_rates_HDB[carpark_number].get(day_type)
    if not rates_for_day_type:
        # Fallback if no specific rates for this day_type are defined in special_rates_HDB
        billable_half_hours = math.ceil((parking_end_dt - parking_start_dt).total_seconds() / 1800)
        return billable_half_hours * standard_rate_per_half_hour

    current_slot_start = parking_start_dt
    
    # Loop through 30-minute slots until we pass the end of the parking duration
    while current_slot_start < parking_end_dt:
        # Get the rate applicable at the *start* of this 30-minute slot
        applicable_rate = get_rate_for_time_slot(
            current_slot_start.time(),
            rates_for_day_type,
            standard_rate_per_half_hour # Default if time falls outside specific segments for special carpark
        )
        
        total_cost += applicable_rate
        
        # Move to the start of the next 30-minute slot
        current_slot_start += datetime.timedelta(minutes=30)
        
    return total_cost

# --- Main calc_cost function (handles multi-day HDB parking) ---
def calc_cost(carpark_info, parking_start_dt: datetime, parking_end_dt: datetime) -> float:
    """
    Main function to calculate cost, handling multi-day parking for HDB.

    Args:
        carpark_info (dict): Dictionary containing carpark details, including 'type' and 'number'/'id'.
        parking_start_dt (datetime): The full datetime object for parking start.
        parking_end_dt (datetime): The full datetime object for parking end.

    Returns:
        float: Total parking cost.
    """
    if carpark_info['type'] == 'HDB':
        if parking_start_dt.date() < parking_end_dt.date(): # Parking spans multiple calendar days
            total_multi_day_cost = 0.0

            # 1. Cost for the first partial day (from start_dt to 23:59:59 of first day)
            first_day_end_dt = datetime.combine(parking_start_dt.date(), time(23, 59, 59))
            total_multi_day_cost += calc_hdb_cost(carpark_info, parking_start_dt, first_day_end_dt)
            
            # 2. Cost for any full intermediate days
            current_intermediate_date = parking_start_dt.date() + timedelta(days=1)
            while current_intermediate_date < parking_end_dt.date():
                full_day_start = datetime.combine(current_intermediate_date, time(0,0,0))
                full_day_end = datetime.combine(current_intermediate_date, time(23,59,59))
                total_multi_day_cost += calc_hdb_cost(carpark_info, full_day_start, full_day_end)
                current_intermediate_date += timedelta(days=1)

            # 3. Cost for the last partial day (from 00:00:00 of last day to end_dt)
            last_day_start_dt = datetime.combine(parking_end_dt.date(), time(0, 0, 0))
            total_multi_day_cost += calc_hdb_cost(carpark_info, last_day_start_dt, parking_end_dt)
            
            return total_multi_day_cost
            
        else: # Parking entirely within one calendar day
            return calc_hdb_cost(carpark_info, parking_start_dt, parking_end_dt)
    elif carpark_info['type'] == 'URA':
        # You'll implement calc_ura_cost separately
        return 0.0 # Placeholder
    else:
        raise ValueError("Unknown carpark type")

# --- TEST CASES (JUnit Style using unittest) ---

class TestHDBParkingCost(unittest.TestCase):
    # Define some fixed dates for consistent testing
    MONDAY = date(2025, 7, 7)    # Weekday
    SATURDAY = date(2025, 7, 5)  # Saturday
    SUNDAY = date(2025, 7, 6)    # Sunday

    # Define common carpark info objects
    # Note: 'number' key is assumed to match your special_rates_HDB keys
    STANDARD_CARPARK_INFO = {'type': 'HDB', 'number': 'UNKNOWN_CARPARK'} # Will not be in special_rates_HDB
    ACB_CARPARK_INFO = {'type': 'HDB', 'number': 'ACB'}
    HG16_CARPARK_INFO = {'type': 'HDB', 'number': 'HG16'}
    SE21_CARPARK_INFO = {'type': 'HDB', 'number': 'SE21'} # Another special one

    # --- Standard Carpark Tests ---

    def test_standard_carpark_grace_period(self):
        # 5 minutes parking, should be free
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 5, 0)
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.0)

    def test_standard_carpark_under_30_min(self):
        # 15 minutes parking, should be 1 half-hour slot (0.60)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 15, 0)
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_standard_carpark_exact_30_min(self):
        # 30 minutes parking, should be 1 half-hour slot (0.60)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_standard_carpark_just_over_30_min(self):
        # 31 minutes parking, should be 2 half-hour slots (1.20)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 31, 0)
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.20)

    def test_standard_carpark_multi_hours(self):
        # 2 hours parking (4 half-hour slots) = 4 * 0.60 = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 2.40)

    # --- Special Carpark (HG16) Tests - Weekdays (0.60, 0.80, 0.60) ---

    def test_hg16_weekday_segment_1_full(self):
        # 00:00 - 10:59:59 (0.60 rate) - Park 01:00 to 01:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_hg16_weekday_segment_2_full(self):
        # 11:00 - 19:59:59 (0.80 rate) - Park 12:00 to 12:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.80)

    def test_hg16_weekday_segment_3_full(self):
        # 20:00 - 23:59:59 (0.60 rate) - Park 20:30 to 21:00 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 21, 0, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_hg16_weekday_cross_segment_1_to_2(self):
        # Park 10:30 to 11:30 (1 hour = 2 slots) on weekday
        # 10:30-11:00 (0.60) + 11:00-11:30 (0.80) = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 11, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_hg16_weekday_cross_segment_2_to_3(self):
        # Park 19:30 to 20:30 (1 hour = 2 slots) on weekday
        # 19:30-20:00 (0.80) + 20:00-20:30 (0.60) = 0.80 + 0.60 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 19, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_hg16_weekday_full_day(self):
        # Park 00:00 to 23:59:59 (48 slots total, 24 hours) on weekday
        # 11:00-20:00 (9 hours * 2 slots/hr = 18 slots @ 0.80) = 14.40
        # 00:00-11:00 (11 hours * 2 slots/hr = 22 slots @ 0.60) = 13.20 (actually 00:00 to 10:59:59 is 22 slots)
        # 20:00-24:00 (4 hours * 2 slots/hr = 8 slots @ 0.60) = 4.80
        # Total = 13.20 (00-11) + 14.40 (11-20) + 4.80 (20-24) = 32.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 0, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 59, 59)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        # Manually calculate:
        # 00:00-10:59:59 (11 hours) = 22 slots * 0.60 = 13.20
        # 11:00-19:59:59 (9 hours) = 18 slots * 0.80 = 14.40
        # 20:00-23:59:59 (4 hours) = 8 slots * 0.60 = 4.80
        # Total = 13.20 + 14.40 + 4.80 = 32.40
        self.assertAlmostEqual(cost, 32.40)


    # --- Special Carpark (HG16) Tests - Saturdays ---

    def test_hg16_saturday_segment_2_full(self):
        # 09:00 - 19:59:59 (0.80 rate) - Park 10:00 to 10:30 (1 slot)
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 10, 0, 0)
        end_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 10, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.80)

    def test_hg16_saturday_cross_segment_1_to_2(self):
        # Park 08:30 to 09:30 (1 hour = 2 slots) on Saturday
        # 08:30-09:00 (0.60) + 09:00-09:30 (0.80) = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 8, 30, 0)
        end_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 9, 30, 0)
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    # --- Special Carpark (ACB) Tests - Weekdays (0.60, 1.20, 1.40, 0.80, 0.60) ---

    def test_acb_weekday_segment_1_full(self):
        # 00:00 - 06:59:59 (0.60 rate) - Park 01:00 to 01:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)
        
    def test_acb_weekday_segment_2_full(self):
        # 07:00 - 09:59:59 (1.20 rate) - Park 07:00 to 07:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 30, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.20)

    def test_acb_weekday_segment_3_full(self):
        # 10:00 - 16:59:59 (1.40 rate) - Park 12:00 to 12:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_acb_weekday_segment_4_full(self):
        # 17:00 - 17:59:59 (0.80 rate) - Park 17:30 to 18:00 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 17, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 18, 0, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.80) # This slot 17:30-18:00 crosses into 18:00 segment.
                                         # The logic currently assigns rate based on *start* of slot.
                                         # So 17:30 gets 0.80, and 18:00 will get 0.60 if calculated as a separate slot.
                                         # The correct expected output for 17:30-18:00 would be 0.80.

    def test_acb_weekday_cross_multiple_segments(self):
        # Park 09:30 to 11:30 (2 hours = 4 slots) on weekday
        # 09:30-10:00 (0.5hr in 1.20 zone) = 1 slot * 1.20 = 1.20
        # 10:00-10:30 (0.5hr in 1.40 zone) = 1 slot * 1.40 = 1.40
        # 10:30-11:00 (0.5hr in 1.40 zone) = 1 slot * 1.40 = 1.40
        # 11:00-11:30 (0.5hr in 1.40 zone) = 1 slot * 1.40 = 1.40
        # Total = 1.20 + 1.40 + 1.40 + 1.40 = 5.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 11, 30, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 5.40)

    # --- Overnight Parking Tests (using calc_cost) ---

    def test_overnight_standard_carpark(self):
        # Park 23:00 Monday to 01:00 Tuesday (standard carpark)
        # Mon: 23:00 - 23:59:59 (2 slots * 0.60) = 1.20
        # Tue: 00:00 - 01:00 (2 slots * 0.60) = 1.20
        # Total = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day + 1, 1, 0, 0) # Next day
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 2.40)

    def test_overnight_hg16_to_next_day_same_type(self):
        # Park 22:00 Saturday to 02:00 Sunday (HG16)
        # Sat: 22:00-23:59:59 (4 slots * 0.60) = 2.40
        # Sun: 00:00-02:00 (4 slots * 0.60) = 2.40
        # Total = 4.80
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 2, 0, 0) # Next day is Sunday
        cost = calc_cost(self.HG16_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 4.80)

    def test_overnight_acb_crossing_to_different_day_rates(self):
        # Park 22:00 Saturday to 09:00 Sunday (ACB)
        # Sat: 22:00-23:59:59 (4 slots * 0.60) = 2.40
        # Sun: 00:00-07:59:59 (16 slots * 0.60) = 9.60
        # Sun: 08:00-09:00 (2 slots * 0.80) = 1.60
        # Total = 2.40 + 9.60 + 1.60 = 13.60
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 9, 0, 0) # Next day is Sunday
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 13.60)

    def test_multi_day_parking_standard(self):
        # Park Monday 10:00 AM to Wednesday 10:00 AM (Standard Carpark)
        # Mon: 10:00 - 23:59:59 (14 hours = 28 slots * 0.60) = 16.80
        # Tue: 00:00 - 23:59:59 (24 hours = 48 slots * 0.60) = 28.80
        # Wed: 00:00 - 10:00 (10 hours = 20 slots * 0.60) = 12.00
        # Total = 16.80 + 28.80 + 12.00 = 57.60
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day + 2, 10, 0, 0) # Two days later
        cost = calc_cost(self.STANDARD_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 57.60)

    def test_multi_day_parking_acb(self):
        # Park Monday 09:00 AM to Wednesday 09:00 AM (ACB)
        # Mon: 09:00-09:59:59 (2 slots * 1.20) = 2.40
        # Mon: 10:00-16:59:59 (14 slots * 1.40) = 19.60
        # Mon: 17:00-17:59:59 (2 slots * 0.80) = 1.60
        # Mon: 18:00-23:59:59 (12 slots * 0.60) = 7.20
        # Mon Total = 2.40 + 19.60 + 1.60 + 7.20 = 30.80 (for 09:00 to 23:59:59)

        # Tue: 00:00-06:59:59 (14 slots * 0.60) = 8.40
        # Tue: 07:00-09:59:59 (6 slots * 1.20) = 7.20
        # Tue: 10:00-16:59:59 (14 slots * 1.40) = 19.60
        # Tue: 17:00-17:59:59 (2 slots * 0.80) = 1.60
        # Tue: 18:00-23:59:59 (12 slots * 0.60) = 7.20
        # Tue Total = 8.40 + 7.20 + 19.60 + 1.60 + 7.20 = 44.00 (full day)

        # Wed: 00:00-06:59:59 (14 slots * 0.60) = 8.40
        # Wed: 07:00-09:00 (4 slots * 1.20) = 4.80
        # Wed Total = 8.40 + 4.80 = 13.20 (for 00:00 to 09:00)

        # Grand Total = 30.80 + 44.00 + 13.20 = 88.00
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day + 2, 9, 0, 0)
        cost = calc_cost(self.ACB_CARPARK_INFO, start_dt, end_dt)
        self.assertAlmostEqual(cost, 88.00)


# This block runs the tests when the script is executed
if __name__ == '__main__':
    print("Running HDB Parking Cost Tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)