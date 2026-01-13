# aemo_to_tariff/powercor.py
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import time

def time_zone():
    return 'Australia/Melbourne'


tariffs = {
    'D1': {
        'name': 'Residential Single Rate',
        'periods': [
            ('Anytime', time(0, 0), time(23, 59), 9.6700)
        ]
    },
    'PRTOU': {
        'name': 'Residential TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.07),
            ('Peak', time(15, 0), time(21, 0), 20.17),
            ('Off-peak', time(21, 0), time(23, 59), 5.07),
        ]
    },
    'NDMO21': {
        'name': 'NDMO21 TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 5.61),
            ('Peak', time(15, 0), time(21, 0), 19.29),
            ('Off-peak', time(21, 0), time(23, 59), 5.61),
        ]
    },
    'NDTOU': {
        'name': 'NDTOU TOU',
        'periods': [
            ('Off-peak', time(0, 0), time(15, 0), 4.58),
            ('Peak', time(15, 0), time(21, 0), 20.60),
            ('Off-peak', time(21, 0), time(23, 59), 4.58),
        ]
    },
    'PRDS': {
        'name': 'Residential daytime saver',
        'periods': [
            ('Off-peak', time(0, 0), time(10, 0), 7.0),
            ('Day', time(10, 0), time(15, 0), 0.0),
            ('Off-peak', time(15, 0), time(16, 00), 7.0),
            ('Peak', time(16, 0), time(21, 0), 19.61),
            ('Off-peak', time(21, 0), time(23, 59), 7.0),
        ]
    }
}

demand_charges = {
    'PRDEMD': { 'Peak': 10.0},  # Residential Demand
    'PSTDEMD': { 'Peak': 10.0},  # Residential Demand
    'PSTCTD': { 'Peak': 10.0},  # Residential Demand
    'PSTNPD': { 'Peak': 10.0},  # Residential Demand
    'PSTNCD': { 'Peak': 10.0},  # Residential Demand
    'PSTNDD': { 'Peak': 10.0},  # Residential Demand
}

def get_daily_fee(tariff_code: str):
    return 41.10

def get_periods(tariff_code: str):
    tariff = tariffs.get(tariff_code)
    if not tariff:
        raise ValueError(f"Unknown tariff code: {tariff_code}")

    return tariff['periods']

def convert_feed_in_tariff(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for SA Power Networks.

    Parameters:
    - interval_datetime (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    rrp_c_kwh = rrp / 10
    
    return rrp_c_kwh

def convert(interval_datetime: datetime, tariff_code: str, rrp: float):
    """
    Convert RRP from $/MWh to c/kWh for Powercor.

    Parameters:
    - interval_time (str): The interval time.
    - tariff (str): The tariff code.
    - rrp (float): The Regional Reference Price in $/MWh.

    Returns:
    - float: The price in c/kWh.
    """
    interval_datetime = interval_datetime - timedelta(minutes=5)
    interval_time = interval_datetime.astimezone(ZoneInfo(time_zone())).time()

    rrp_c_kwh = rrp / 10
    tariff = tariffs[tariff_code]

    # Find the applicable period and rate
    for period, start, end, rate in tariff['periods']:
        if start <= interval_time < end:
            total_price = rrp_c_kwh + rate
            return total_price

        # Handle overnight periods (e.g., 22:00 to 07:00)
        if start > end and (interval_time >= start or interval_time < end):
            total_price = rrp_c_kwh + rate
            return total_price

    # Otherwise, this terrible approximation
    slope = 1.037869032618134
    intercept = 5.586606750833143
    return rrp_c_kwh * slope + intercept


def estimate_demand_fee(interval_time: datetime, tariff_code: str, demand_kw: float):
    """
    Estimate the demand fee for a given tariff code, demand amount, and time period.

    Parameters:
    - interval_time (datetime): The interval datetime.
    - tariff_code (str): The tariff code.
    - demand_kw (float): The maximum demand in kW (or kVA for 8100 and 8300 tariffs).

    Returns:
    - float: The estimated demand fee in dollars.
    """
    time_of_day = interval_time.astimezone(ZoneInfo(time_zone())).time()
    
    if tariff_code not in demand_charges:
        return 0.0  # Return 0 if the tariff doesn't have a demand charge

    charge = demand_charges[tariff_code]
    if isinstance(charge, dict):
        # Determine the time period
        if 'Peak' in charge and time(17, 0) <= time_of_day < time(20, 0):
            charge_per_kw_per_month = charge['Peak']
        elif 'Off-Peak' in charge and time(11, 0) <= time_of_day < time(13, 0):
            charge_per_kw_per_month = charge['Off-Peak']
        else:
            charge_per_kw_per_month = charge.get('Shoulder', 0.0)
    else:
        charge_per_kw_per_month = charge

    return charge_per_kw_per_month * demand_kw