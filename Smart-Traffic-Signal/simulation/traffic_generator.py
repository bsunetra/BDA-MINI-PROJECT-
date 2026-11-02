"""
Member 3 - Traffic arrival generator.

Produces a per-second, per-lane arrival count for the whole simulated
window, using a Poisson process whose rate follows the same peak-hour
shape Member 2 used for the historical dataset (see config.hourly_multiplier).

This is a queueing-level simulation, not a microscopic one (no individual
vehicle positions/speeds like SUMO) -- deliberate, matches the scope
Member 3 owns for Review 1 (four-way intersection + fixed/adaptive
comparison + metrics), not a full traffic simulator.
"""

import random

from sim_config import (
    LANES,
    SIM_DURATION_SECONDS,
    BASE_ARRIVAL_RATE,
    hourly_multiplier,
    RANDOM_SEED,
)


def generate_arrivals(start_hour=8, seed=RANDOM_SEED):
    """
    Returns dict: lane -> list[int], one entry per simulated second,
    arrivals[lane][t] = number of vehicles that arrived on that lane
    during second t.

    start_hour: simulated clock hour the run begins at (default 8am,
    inside the morning peak, so the comparison has real congestion to show).
    """
    rng = random.Random(seed)
    arrivals = {lane: [0] * SIM_DURATION_SECONDS for lane in LANES}

    for t in range(SIM_DURATION_SECONDS):
        sim_hour = (start_hour + t // 3600) % 24
        mult = hourly_multiplier(sim_hour)
        for lane in LANES:
            rate = BASE_ARRIVAL_RATE[lane] * mult
            arrivals[lane][t] = _poisson(rng, rate)

    return arrivals


def _poisson(rng: random.Random, rate: float) -> int:
    """
    Knuth's algorithm -- fine at these rates (< ~1 veh/sec/lane), avoids
    taking a numpy dependency just for this.
    """
    if rate <= 0:
        return 0
    import math
    l = math.exp(-rate)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= l:
            return k - 1
