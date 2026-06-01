#!/usr/bin/env python3
"""
Skybound daily challenge.

A daily run seeds the procedural generator from the calendar date, so every
player gets the same layout that day, and the best level reached is tracked
per date in the save. Whether the current run is a daily run is a runtime flag
(not persisted).
"""

from datetime import date

from utils.save_manager import get_save_manager

_active = False  # runtime: is the current run a daily challenge?


def is_active():
    return _active


def set_active(value):
    global _active
    _active = bool(value)


def today_key(today=None):
    """Date key in YYYY-MM-DD form."""
    return (today or date.today()).isoformat()


def daily_seed(today=None):
    """Deterministic integer seed from the date (e.g. 2026-06-01 -> 20260601)."""
    return int(today_key(today).replace("-", ""))


def get_daily_best(today=None):
    """Best level reached on a given day (0 if none)."""
    return int(get_save_manager().get("daily_bests").get(today_key(today), 0))


def record_daily_result(level, today=None):
    """Record ``level`` as today's best if it beats the stored one.

    Returns the (possibly updated) best for the day.
    """
    key = today_key(today)
    sm = get_save_manager()
    bests = sm.get("daily_bests")
    if int(level) > bests.get(key, 0):
        bests[key] = int(level)
        sm.set("daily_bests", bests)
    return bests.get(key, 0)
