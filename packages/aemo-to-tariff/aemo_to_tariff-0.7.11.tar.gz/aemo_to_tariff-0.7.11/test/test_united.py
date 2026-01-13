import unittest
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.united import time_zone, convert, get_daily_fee

class TestUnited(unittest.TestCase):
    def test_convert(self):
        interval_time = datetime(2023, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'URTOU'
        rrp = 100.0
        expected_price = 15.07
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'URTOU'
        expected_fee = 41.1
        fee = get_daily_fee(tariff_code)
        self.assertEqual(fee, expected_fee)
