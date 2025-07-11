from datetime import datetime, time, date, timedelta # Ensure these are imported
import math

# Use datetime for parsing and manipulating time strings, currently using time which cannot be subtracted

# Example start and end times for testing
# get only the time part of the current datetime without the decimal part
# now = datetime.now().time().replace(microsecond=0)

# print(f"Current time: {now}")

# 1. Helper to parse time strings (e.g., "07.00 AM" to datetime.time object)
def parse_time_str_to_obj(time_str: str) -> time:
    """Converts 'HH:MM AM/PM' string to datetime.time object. Assume the start day is today."""
    try:
        return datetime.strptime(time_str, "%I:%M %p").time()
    except ValueError as e:
        print(f"Error parsing time string '{time_str}': {e}")

# print(parse_time_str_to_obj(end_time))  # Example usage

# 2. Helper to parse duration strings (e.g., "30 mins", "0 mins", "810 mins") to timedelta
def parse_duration_str_to_minutes(duration_str: str) -> int:
    """Converts 'X mins' string to integer minutes."""
    try:
        return int(duration_str.replace(' mins', '').strip())
    except ValueError:
        logger.warning(f"Could not parse duration string: {duration_str}. Defaulting to 0.")
        return 0
    
# 3. Helper to parse rate strings (e.g., "$0.60", "$0.00") to float
def parse_rate_str_to_float(rate_str: str) -> float:
    """Converts '$X.YY' string to float."""
    try:
        return float(rate_str.replace('$', '').strip())
    except ValueError:
        logger.warning(f"Could not parse rate string: {rate_str}. Defaulting to 0.0.")
        return 0.0

# 4. Helper to determine day type from a datetime object
def get_day_type(dt_obj: datetime) -> str:
    """Returns 'weekday', 'saturday', or 'sunday_ph' based on datetime."""
    if dt_obj.weekday() < 5: # Monday is 0, Friday is 4
        # Need to check for Public Holidays too. This would require a list of PH.
        # For simplicity now, just check weekday.
        return "weekday"
    elif dt_obj.weekday() == 5: # Saturday is 5
        return "saturday"
    else: # Sunday is 6
        # Need to check for Public Holidays.
        return "sunday_ph"

# 5. Helper to get the correct rate from a rule based on day type
def get_rate_for_day(rate_rule: dict, day_type: str) -> dict:
    """
    Gets the min_duration and rate for a specific day type from a rate_rule.
    Returns {'min_duration': int, 'rate': float}
    """
    day_specific_rates = rate_rule.get(day_type)
    if day_specific_rates:
        min_duration = parse_duration_str_to_minutes(day_specific_rates.get('min_duration', '0 mins'))
        rate_val = parse_rate_str_to_float(day_specific_rates.get('rate', '$0.00'))
        return {"min_duration": min_duration, "rate": rate_val}
    return {"min_duration": 0, "rate": 0.0}

# input: datetime objects, carpark dictionary with rate rules
def calc_cost(carpark, start_time, end_time):
    if carpark['type'] == 'HDB':
        start_date, end_date = start_time.date(), end_time.date()
        if end_date > start_date: # overnight parking
            # Calculate cost for the first day, set end_time to 23:59:59
            first_day_end_time = datetime.combine(start_date, time(23, 59, 59))
            second_day_start_time = datetime.combine(end_date, time(0, 0, 0))
            return calc_hdb_cost(carpark['carpark_number'], start_time, first_day_end_time) + calc_hdb_cost(carpark['carpark_number'], second_day_start_time, end_time)
        else:
            return calc_hdb_cost(carpark['carpark_number'], start_time, end_time)
    elif carpark['type'] == 'URA':
        return calc_ura_cost(carpark['carpark_number'], start_time, end_time)
    else:
        raise ValueError("Unknown carpark type")

# def calc_ura_cost(carpark, start_time, end_time):
    # narrow down to rate rules based on day type
    # if spanning multiple days, calculate for each day separately then sum up
    # if not, calculate for the single day
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

def calc_hdb_cost(carpark, start_time, end_time, overnight=False): # call separately for each day if overnight, then pass overnight=True for the next day
    total_cost = 0.0
    
    # Grace period of 15 minutes
    if end_time - start_time <= timedelta(minutes=15):
        return 0.0
    
    # assume end time is always after start time (ie no overnight parking)
    # get the day type for the start time
    day_of_week_int = start_time.weekday()
    day = "weekdays" if day_of_week_int < 5 else "saturdays" if day_of_week_int == 5 else "sundays"
    rate_per_half_hour = 0.60
    rate_per_minute = rate_per_half_hour / 30.0
    
    if carpark not in special_rates_HDB:
        # divide the time (18:46:09) into half-hour slots (or part thereof)
        duration_in_minutes = math.ceil((end_time - start_time).total_seconds() / 60)
        total_cost = duration_in_minutes * rate_per_minute
        return round(total_cost, 2)
    
    # if special carpark, get the rates for the day
    rates = special_rates_HDB[carpark][day]
    
    for rate in rates:
        # convert rate start and end times to datetime.time objects
        # to compare with start_time and end_time
        rate_start = datetime.strptime(rate["start"], "%H:%M:%S").time()
        rate_end = datetime.strptime(rate["end"], "%H:%M:%S").time()
        rate_start = datetime.combine(start_time.date(), rate_start)
        rate_end = datetime.combine(start_time.date(), rate_end)
        
        # Case 1: period is within a single rate period
        if start_time >= rate_start and end_time <= rate_end:
            duration_in_minutes = math.ceil((end_time - start_time).total_seconds() / 60)
            total_cost += duration_in_minutes * rate["rate_per_half_hour"] / 30.0
            return round(total_cost, 2)
        
        # Case 2: period is later than this rate period
        if start_time > rate_end:
            continue
        
        # Case 3: overlaps occur
        if start_time >= rate_start and end_time > rate_end:
            duration_in_minutes = math.ceil((rate_end - start_time).total_seconds() / 60)
            total_cost += duration_in_minutes * rate["rate_per_half_hour"] /30
            start_time = rate_end + timedelta(seconds=1) # 19:59:59 + 1 second = 20:00:00
            continue
    return round(total_cost, 2)

# create datetime objects for start and end times
# end_time = datetime.strptime("23:59:59", "%H:%M:%S").time()
# start_time = datetime.strptime("00:00:00", "%H:%M:%S").time()
# date_tomorrow = date.today() + timedelta(days=1)
# print(start_time, end_time)
# # print(end_time - start_time)
# print(calc_hdb_cost("MP14", start_time, end_time)) # $33.60