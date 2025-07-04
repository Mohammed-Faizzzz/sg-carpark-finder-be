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
        

    # --- Standard Carpark Tests ---

    def test_standard_carpark_grace_period(self):
        # 5 minutes parking, should be free
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 5, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.0)

    def test_standard_carpark_under_30_min(self):
        # 15 minutes parking, should be 1 half-hour slot (0.60)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 15, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_standard_carpark_exact_30_min(self):
        # 30 minutes parking, should be 1 half-hour slot (0.60)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_standard_carpark_just_over_30_min(self):
        # 31 minutes parking, should be 2 half-hour slots (1.20)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 31, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.20)

    def test_standard_carpark_multi_hours(self):
        # 2 hours parking (4 half-hour slots) = 4 * 0.60 = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 2.40)

    # --- Special Carpark (HG16) Tests - Weekdays (0.60, 0.80, 0.60) ---

    def test_hg16_weekday_segment_1_full(self):
        # 00:00 - 10:59:59 (0.60 rate) - Park 01:00 to 01:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_hg16_weekday_segment_2_full(self):
        # 11:00 - 19:59:59 (0.80 rate) - Park 12:00 to 12:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.80)

    def test_hg16_weekday_segment_3_full(self):
        # 20:00 - 23:59:59 (0.60 rate) - Park 20:30 to 21:00 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 21, 0, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)

    def test_hg16_weekday_cross_segment_1_to_2(self):
        # Park 10:30 to 11:30 (1 hour = 2 slots) on weekday
        # 10:30-11:00 (0.60) + 11:00-11:30 (0.80) = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 11, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_hg16_weekday_cross_segment_2_to_3(self):
        # Park 19:30 to 20:30 (1 hour = 2 slots) on weekday
        # 19:30-20:00 (0.80) + 20:00-20:30 (0.60) = 0.80 + 0.60 = 1.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 19, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 20, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_hg16_weekday_full_day(self):
        # Park 00:00 to 23:59:59 (48 slots total, 24 hours) on weekday
        # 11:00-20:00 (9 hours * 2 slots/hr = 18 slots @ 0.80) = 14.40
        # 00:00-11:00 (11 hours * 2 slots/hr = 22 slots @ 0.60) = 13.20 (actually 00:00 to 10:59:59 is 22 slots)
        # 20:00-24:00 (4 hours * 2 slots/hr = 8 slots @ 0.60) = 4.80
        # Total = 13.20 (00-11) + 14.40 (11-20) + 4.80 (20-24) = 32.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 0, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 59, 59)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
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
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.80)

    def test_hg16_saturday_cross_segment_1_to_2(self):
        # Park 08:30 to 09:30 (1 hour = 2 slots) on Saturday
        # 08:30-09:00 (0.60) + 09:00-09:30 (0.80) = 0.60 + 0.80 = 1.40
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 8, 30, 0)
        end_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 9, 30, 0)
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    # --- Special Carpark (ACB) Tests - Weekdays (0.60, 1.20, 1.40, 0.80, 0.60) ---

    def test_acb_weekday_segment_1_full(self):
        # 00:00 - 06:59:59 (0.60 rate) - Park 01:00 to 01:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 1, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 0.60)
        
    def test_acb_weekday_segment_2_full(self):
        # 07:00 - 09:59:59 (1.20 rate) - Park 07:00 to 07:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.20)

    def test_acb_weekday_segment_3_full(self):
        # 10:00 - 16:59:59 (1.40 rate) - Park 12:00 to 12:30 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 12, 30, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 1.40)

    def test_acb_weekday_segment_4_full(self):
        # 17:00 - 17:59:59 (0.80 rate) - Park 17:30 to 18:00 (1 slot)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 17, 30, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 18, 0, 0)
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
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
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 5.40)

    # --- Overnight Parking Tests (using calc_cost) ---

    def test_overnight_standard_carpark(self):
        # Park 23:00 Monday to 01:00 Tuesday (standard carpark)
        # Mon: 23:00 - 23:59:59 (2 slots * 0.60) = 1.20
        # Tue: 00:00 - 01:00 (2 slots * 0.60) = 1.20
        # Total = 2.40
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 23, 0, 0)
        end_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day + 1, 1, 0, 0) # Next day
        cost = calc_cost(self.combined_data["Y79M"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 2.40)

    def test_overnight_hg16_to_next_day_same_type(self):
        # Park 22:00 Saturday to 02:00 Sunday (HG16)
        # Sat: 22:00-23:59:59 (4 slots * 0.60) = 2.40
        # Sun: 00:00-02:00 (4 slots * 0.60) = 2.40
        # Total = 4.80
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 2, 0, 0) # Next day is Sunday
        cost = calc_cost(self.combined_data["HG16"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 4.80)

    def test_overnight_acb_crossing_to_different_day_rates(self):
        # Park 22:00 Saturday to 09:00 Sunday (ACB)
        # Sat: 22:00-23:59:59 (4 slots * 0.60) = 2.40
        # Sun: 00:00-07:59:59 (16 slots * 0.60) = 9.60
        # Sun: 08:00-09:00 (2 slots * 0.80) = 1.60
        # Total = 2.40 + 9.60 + 1.60 = 13.60
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 22, 0, 0)
        end_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 9, 0, 0) # Next day is Sunday
        cost = calc_cost(self.combined_data["ACB"], start_dt, end_dt)
        self.assertAlmostEqual(cost, 13.60)

# This block runs the tests when the script is executed
if __name__ == '__main__':
    print("Running HDB Parking Cost Tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)