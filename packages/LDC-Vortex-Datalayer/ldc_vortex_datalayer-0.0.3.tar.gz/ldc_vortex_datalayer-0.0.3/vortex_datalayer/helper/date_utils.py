"""
Date Utilities

Utility functions for date handling.
Copied from vortex/common/utils/date_utils.py to make repository self-contained.
"""

from django.utils import timezone
import datetime
import pytz


def get_current_dtm(tz=None):
    try:
        return timezone.localtime(timezone.now(), tz)
    except Exception:
        return datetime.datetime.now(tz)


def convert_ist_date_to_utc_start_of_day(date_obj):
    if date_obj is None:
        return None

    ist_tz = pytz.timezone('Asia/Kolkata')

    start_of_day = datetime.datetime.combine(date_obj, datetime.time.min)
    start_of_day_ist = ist_tz.localize(start_of_day)
    start_of_day_utc = start_of_day_ist.astimezone(pytz.UTC)

    return start_of_day_utc


def convert_ist_date_to_utc_end_of_day(date_obj):
    if date_obj is None:
        return None

    ist_tz = pytz.timezone('Asia/Kolkata')

    end_of_day = datetime.datetime.combine(date_obj, datetime.time.max)
    end_of_day_ist = ist_tz.localize(end_of_day)
    end_of_day_utc = end_of_day_ist.astimezone(pytz.UTC)

    return end_of_day_utc

