import datetime
from datetime import datetime, date, time, timedelta
import math
import unittest # Import unittest for testing
from calc_rates import calc_cost, calc_hdb_cost, get_day_type, parse_time_str_to_obj, special_rates_HDB
import json
import os

class TestHDBParkingCost(unittest.TestCase):
    # Define some fixed dates for consistent testing
    MONDAY = date(2025, 7, 7)    # Weekday
    SATURDAY = date(2025, 7, 5)  # Saturday
    SUNDAY = date(2025, 7, 6)    # Sunday
    
    def setUp(self):
        # load carpark data from JSON files
        with open('combined_carpark_data.json', 'r') as f:
            self.combined_data = json.load(f)
            
    def test_standard_carpark_grace_period(self):
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 5, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 0.0)

    def test_standard_carpark_under_30_min(self):
        # 25 minutes parking = 25 * 0.02 = 0.50
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 25, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 0.50)

    def test_standard_carpark_exact_30_min(self):
        # 30 minutes parking = 30 * 0.02 = 0.60
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 0.60)

    def test_standard_carpark_just_over_30_min(self):
        # 31 minutes parking = 31 * 0.02 = 0.62
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 31, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 0.62)

    def test_standard_carpark_multi_hours(self):
        # 2 hours (120 mins) parking = 120 * 0.02 = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 2.40)


    # --- Special Carpark (HG16) Tests - Weekdays (0.60, 0.80, 0.60 rates) ---
    # Rates are per half-hour, but billing is per minute. So 0.60/30 = 0.02/min, 0.80/30 = 0.0266.../min

    def test_hg16_weekday_segment_1_full(self):
        # 00:00 - 10:59:59 (0.60 rate/half-hour = 0.02/min) - Park 01:00 to 01:30 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 30 * (0.60/30.0)) # 0.60

    def test_hg16_weekday_segment_2_full(self):
        # 11:00 - 19:59:59 (0.80 rate/half-hour = 0.0266.../min) - Park 12:00 to 12:30 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 30 * (0.80/30.0)) # 0.80

    def test_hg16_weekday_segment_3_full(self):
        # 20:00 - 23:59:59 (0.60 rate/half-hour = 0.02/min) - Park 20:30 to 21:00 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 21, 0, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 30 * (0.60/30.0)) # 0.60

    def test_hg16_weekday_cross_segment_1_to_2(self):
        # Park 10:30 to 11:30 (1 hour = 60 mins) on weekday
        # 10:30-11:00 (30 mins @ 0.60/half-hour) = 30 * 0.02 = 0.60
        # 11:00-11:30 (30 mins @ 0.80/half-hour) = 30 * 0.0266... = 0.80
        # Total = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 11, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 1.40)

    def test_hg16_weekday_cross_segment_2_to_3(self):
        # Park 19:30 to 20:30 (1 hour = 60 mins) on weekday
        # 19:30-20:00 (30 mins @ 0.80/half-hour) = 0.80
        # 20:00-20:30 (30 mins @ 0.60/half-hour) = 0.60
        # Total = 0.80 + 0.60 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 19, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 1.40)

    def test_hg16_weekday_full_day(self):
        # Park 00:00 to 23:59:59 (1439 mins) on weekday
        # 00:00-10:59:59 (11 hours * 60 = 660 mins @ 0.02/min) = 13.20
        # 11:00-19:59:59 (9 hours * 60 = 540 mins @ 0.0266.../min) = 14.40
        # 20:00-23:59:59 (4 hours * 60 = 240 mins @ 0.02/min) = 4.80
        # Total = 13.20 + 14.40 + 4.80 = 32.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 0, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 59, 59)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 32.40)


    # --- Special Carpark (HG16) Tests - Saturdays ---

    def test_hg16_saturday_segment_2_full(self):
        # 09:00 - 19:59:59 (0.80 rate/half-hour = 0.0266.../min) - Park 10:00 to 10:30 (30 mins)
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 10, 0, 0)
        end_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 10, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 30 * (0.80/30.0)) # 0.80

    def test_hg16_saturday_cross_segment_1_to_2(self):
        # Park 08:30 to 09:30 (1 hour = 60 mins) on Saturday
        # 08:30-09:00 (30 mins @ 0.60/half-hour) = 0.60
        # 09:00-09:30 (30 mins @ 0.80/half-hour) = 0.80
        # Total = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 8, 30, 0)
        end_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 9, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 1.40)

    # --- Special Carpark (ACB) Tests - Weekdays (0.60, 1.20, 1.40, 0.80, 0.60) ---

    def test_acb_weekday_segment_1_full(self):
        # 00:00 - 06:59:59 (0.60 rate/half-hour = 0.02/min) - Park 01:00 to 01:30 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 0.60)
        
    def test_acb_weekday_segment_2_full(self):
        # 07:00 - 09:59:59 (1.20 rate/half-hour = 0.04/min) - Park 07:00 to 07:30 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_acb_weekday_segment_3_full(self):
        # 10:00 - 16:59:59 (1.40 rate/half-hour = 0.0466.../min) - Park 12:00 to 12:30 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 1.40)

    def test_acb_weekday_segment_4_full(self):
        # 17:00 - 17:59:59 (0.80 rate/half-hour = 0.0266.../min) - Park 17:30 to 18:00 (30 mins)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 17, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 18, 0, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 0.80) # This slot 17:30-18:00 crosses into 18:00 segment.

    def test_acb_weekday_cross_multiple_segments(self):
        # Park 09:30 to 11:30 (2 hours = 120 mins) on weekday
        # 09:30-10:00 (30 mins @ 1.20/half-hour) = 30 * 0.04 = 1.20
        # 10:00-11:30 (90 mins @ 1.40/half-hour) = 90 * 0.0466... = 4.20
        # Total = 1.20 + 4.20 = 5.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 11, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 5.40)

    # --- Overnight Parking Tests (using calc_cost) ---

    def test_overnight_standard_carpark(self):
        # Park 23:00 Monday to 01:00 Tuesday (standard carpark)
        # Mon: 23:00 - 23:59:59 (60 mins * 0.02/min) = 1.20
        # Tue: 00:00 - 01:00 (60 mins * 0.02/min) = 1.20
        # Total = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day + 1, 1, 0, 0) # Next day
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertEqual(cost, 2.40)

    def test_overnight_hg16_to_next_day_same_type(self):
        # Park 22:00 Saturday to 02:00 Sunday (HG16)
        # Sat: 22:00-23:59:59 (120 mins * 0.02/min) = 2.40
        # Sun: 00:00-02:00 (120 mins * 0.02/min) = 2.40
        # Total = 4.80
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 2, 0, 0) # Next day is Sunday
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertEqual(cost, 4.80)

    def test_overnight_acb_crossing_to_different_day_rates(self):
        # Park 22:00 Saturday to 09:00 Sunday (ACB)
        # Sat: 22:00-23:59:59 (120 mins * 0.02/min) = 2.40
        # Sun: 00:00-07:59:59 (480 mins * 0.02/min) = 9.60
        # Sun: 08:00-09:00 (60 mins * 0.0266.../min) = 1.60
        # Total = 2.40 + 9.60 + 1.60 = 13.60
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 9, 0, 0) # Next day is Sunday
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertEqual(cost, 13.60)

# This block runs the tests when the script is executed
if __name__ == '__main__':
    print("Running HDB Parking Cost Tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)