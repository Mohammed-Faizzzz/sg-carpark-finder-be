# tests/test_ura_rates.py
import unittest
from datetime import datetime, date
import json

# If calc_cost dispatches to URA internally:
from calc_rates import calc_cost
# If you prefer direct calls, also import:
# from calc_rates import calc_ura_cost

class TestURAParkingCost(unittest.TestCase):
    # Fixed dates for deterministic tests
    # Pick any known calendar: Mon=weekday, Sat, Sun
    MONDAY = date(2025, 7, 7)    # Weekday
    SATURDAY = date(2025, 7, 5)  # Saturday
    SUNDAY = date(2025, 7, 6)    # Sunday

    def setUp(self):
        with open('./data/combined_carpark_data.json', 'r') as f:
            self.combined_data = json.load(f)
            
        # Sanity: make sure these carparks exist and are URA
        for cp in ["P0023", "P0024", "P0028", "P0031", "P0035", "P0036", "P0038"]:
            assert cp in self.combined_data, f"{cp} missing from combined_carpark_data.json"
            assert self.combined_data[cp]["type"] == "URA", f"{cp} is not URA"

    # -------------------------
    # P0023 – free early + paid 08:30–22:00 + free overnight
    # -------------------------

    def test_p0023_free_window_morning(self):
        # 07:15–08:00 (free)
        print(self.combined_data.get("P0023").get("rates"))
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 7, 15, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 8, 0, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 0.0)

    def test_p0023_paid_exact_30_min_block(self):
        # 09:00–09:30 entirely within paid window → 1 block @ $0.60
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 0, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 30, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 0.60)

    def test_p0023_paid_45_mins_rounds_up(self):
        # 09:00–09:45 → ceil(45/30)=2 blocks → $1.20
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 0, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 45, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_p0023_cross_free_to_paid(self):
        # 08:15–09:15 → 15 mins free + 45 mins paid → 2 blocks → $1.20
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 8, 15, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 9, 15, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_p0023_evening_paid_period(self):
        # 17:30–18:30 within paid window → 2 blocks → $1.20
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 17, 30, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 18, 30, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_p0023_overnight_paid_to_free(self):
        # Fri 16:45–Sat 07:15
        # Fri: 16:45–17:00 → 15 mins → 1 block = $0.60
        # Fri: 17:00–22:00 → 5h = 10 blocks = $6.00
        # Fri: 22:00–24:00 → free
        # Sat: 00:00–07:15 → free
        # Total = $6.60
        # (Using Monday/Saturday dates from constants to keep weekday/weekend semantics)
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 16, 45, 0)
        # add one day to hit "Saturday" (we’re not using calendar add, just stitch dates from constants)
        end_dt   = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 7, 15, 0)
        cost = calc_cost(self.combined_data["P0023"], start_dt, end_dt)
        self.assertEqual(cost, 6.60)

    # -------------------------
    # P0024 – Sunday day is free (8:30–17:00); evenings mostly free
    # -------------------------

    def test_p0024_sunday_daytime_free(self):
        # Sunday 10:00–11:00: sunday_ph for 08:30–17:00 is free → $0
        start_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 10, 0, 0)
        end_dt   = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 11, 0, 0)
        cost = calc_cost(self.combined_data["P0024"], start_dt, end_dt)
        self.assertEqual(cost, 0.0)

    def test_p0024_saturday_evening_free(self):
        # Saturday 17:30–18:30: 17:00–07:00 is free → $0
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 17, 30, 0)
        end_dt   = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 18, 30, 0)
        cost = calc_cost(self.combined_data["P0024"], start_dt, end_dt)
        self.assertEqual(cost, 0.0)

    # -------------------------
    # P0028 / P0038 – both have paid 08:30–17:00 and 17:00–22:00, free otherwise
    # -------------------------

    def test_p0028_one_hour_in_paid_block(self):
        # Monday 14:00–15:00 → inside 08:30–17:00 → 2 blocks → $1.20
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 14, 0, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 15, 0, 0)
        cost = calc_cost(self.combined_data["P0028"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_p0038_cross_paid_to_free_at_night(self):
        # Monday 21:30–22:15:
        # 21:30–22:00 paid → 30 mins → 1 block ($0.60)
        # 22:00–22:15 free → $0
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 21, 30, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 22, 15, 0)
        cost = calc_cost(self.combined_data["P0038"], start_dt, end_dt)
        self.assertEqual(cost, 0.60)

    # -------------------------
    # P0031 / P0035 / P0036 – paid 08:30–17:00 weekdays & Saturdays; Sunday day often free
    # -------------------------

    def test_p0031_weekday_45_mins_rounds_to_two_blocks(self):
        # Monday 10:00–10:45 → ceil(45/30)=2 blocks → $1.20
        start_dt = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 0, 0)
        end_dt   = datetime(self.MONDAY.year, self.MONDAY.month, self.MONDAY.day, 10, 45, 0)
        cost = calc_cost(self.combined_data["P0031"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)

    def test_p0035_sunday_daytime_free(self):
        # Sunday 13:00–14:00: sunday_ph for 08:30–17:00 is free at P0035 → $0
        start_dt = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 13, 0, 0)
        end_dt   = datetime(self.SUNDAY.year, self.SUNDAY.month, self.SUNDAY.day, 14, 0, 0)
        cost = calc_cost(self.combined_data["P0035"], start_dt, end_dt)
        self.assertEqual(cost, 0.0)

    def test_p0036_saturday_one_hour_paid(self):
        # Saturday 10:00–11:00: 08:30–17:00 paid → 2 blocks → $1.20
        start_dt = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 10, 0, 0)
        end_dt   = datetime(self.SATURDAY.year, self.SATURDAY.month, self.SATURDAY.day, 11, 0, 0)
        cost = calc_cost(self.combined_data["P0036"], start_dt, end_dt)
        self.assertEqual(cost, 1.20)


if __name__ == "__main__":
    print("Running URA Parking Cost Tests...")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
