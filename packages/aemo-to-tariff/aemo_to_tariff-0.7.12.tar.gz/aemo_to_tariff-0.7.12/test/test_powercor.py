import unittest
from zoneinfo import ZoneInfo
from datetime import datetime
from aemo_to_tariff.powercor import time_zone, convert, get_daily_fee

class TestPowercor(unittest.TestCase):
    def test_convert(self):
        interval_time = datetime(2025, 7, 15, 10, 0, tzinfo=ZoneInfo(time_zone()))
        tariff_code = 'PRDS'
        rrp = 100.0
        expected_price = 17.0
        price = convert(interval_time, tariff_code, rrp)
        self.assertAlmostEqual(price, expected_price, places=2)

    def test_get_daily_fee(self):
        tariff_code = 'PRDS'
        annual_usage = 20000
        expected_fee = 41.1
        fee = get_daily_fee(tariff_code)
        self.assertEqual(fee, expected_fee)
