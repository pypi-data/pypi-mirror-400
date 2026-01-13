import logging
import re
from datetime import datetime, timedelta

def calculate_start_date(end_date: datetime, limit: int, period: str) -> datetime:
    """
    Calculate an approximate start date based on end_date, limit and period.
    Adds a buffer (2.0x for daily/weekly, 1.5x for intraday) to account for market closures.
    """
    # Parse period, e.g., '1d', '1h', '15m'
    match = re.match(r"(\d+)([a-zA-Z]+)", period)
    if not match:
        # Fallback if period format is unexpected (e.g. 'daily' in akshare)
        if period.lower() == 'daily':
            return end_date - timedelta(days=limit * 2)
        return end_date - timedelta(days=limit)
    
    value = int(match.group(1))
    raw_unit = match.group(2)
    unit = raw_unit.lower()
    
    # Calculate duration per candle
    if raw_unit == 'M': # Capital M for Month per standard
        delta = timedelta(days=value * 30)
        buffer = 2.0
    elif unit in ('m', 'min'):
        delta = timedelta(minutes=value)
        buffer = 1.5
    elif unit in ('h', 'hour'):
        delta = timedelta(hours=value)
        buffer = 1.5
    elif unit in ('d', 'day'):
        delta = timedelta(days=value)
        buffer = 2.0
    elif unit in ('w', 'week'):
        delta = timedelta(weeks=value)
        buffer = 2.0
    elif unit in ('mo', 'month'):
        delta = timedelta(days=value * 30)
        buffer = 2.0
    else:
        # Fallback
        delta = timedelta(days=1)
        buffer = 2.0
        
    # Total history needed
    total_delta = delta * limit * buffer
    return end_date - total_delta

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
