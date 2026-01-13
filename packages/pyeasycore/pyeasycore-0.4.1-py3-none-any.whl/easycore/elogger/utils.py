# -*- coding: utf-8 -*-
# author: NhanDD3 <hp.duongducnhan@gmail.com>
import time


def calculate_elapsed_ms(start_ns: int) -> float:
    """Calculate elapsed milliseconds from start time in nanoseconds"""
    return round((time.time_ns() - start_ns) / 1_000_000, 2)
