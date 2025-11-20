# utils.py
from datetime import datetime
DATE_FMT = "%Y-%m-%d"

def parse_int(val, default=None):
    try:
        return int(val)
    except:
        return default

def format_date(datestr):
    try:
        return datetime.strptime(datestr, DATE_FMT).date()
    except:
        return None
