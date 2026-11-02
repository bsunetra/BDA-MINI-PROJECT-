"""
Member 3 - Simulation config.

Kept separate from the optimizer's own config.py (MIN_GREEN/MAX_GREEN
values match on purpose, so the adaptive controller's green_time output
is always inside the range the simulation can actually apply).
"""

LANES = ["North", "South", "East", "West"]

# --- Simulation duration ---
SIM_DURATION_SECONDS = 3600  # 1 simulated hour
TIME_STEP_SECONDS = 1        # resolution of the queue model

# --- Signal timing ---
MIN_GREEN = 10
MAX_GREEN = 45
FIXED_GREEN_PER_LANE = 20     # fixed-time baseline: same green every cycle, every lane
YELLOW_SECONDS = 0            # not modeled; green switches directly to next lane

# --- Discharge (how fast a green lane clears its queue) ---
SATURATION_FLOW_VEH_PER_SEC = 0.5   # 1 vehicle every 2 seconds, typical single-lane figure

# --- Arrival pattern (vehicles/sec, per lane, by simulated hour-of-day) ---
# Reuses the same peak-hour shape Member 2 used for the historical dataset
# generator, so the simulated demand looks like the same city rather than
# an unrelated random process.
BASE_ARRIVAL_RATE = {
    "North": 0.08,  # busiest approach
    "South": 0.04,
    "East": 0.06,
    "West": 0.02,
}
# Sum = 0.20 veh/sec at multiplier 1.0. At the evening peak multiplier
# (2.0) that's 0.40 veh/sec total demand against SATURATION_FLOW_VEH_PER_SEC
# = 0.5 veh/sec of total system capacity (only one lane discharges at a
# time) -- ~80% loaded at peak, congested but not permanently oversaturated.
# The first version of this file used demand ~3x capacity, which produced
# queues that grow without bound all hour; that's a real simulation bug,
# not a realistic "congested intersection", so it was recalibrated.


def hourly_multiplier(hour: int) -> float:
    if 7 <= hour <= 9:
        return 1.8
    if 17 <= hour <= 19:
        return 2.0
    if 0 <= hour <= 5:
        return 0.2
    if 10 <= hour <= 16:
        return 1.0
    return 0.6


# --- Normalization caps, matching Member 2's 02_live_lane_aggregation.py ---
MAX_REASONABLE_VEHICLES = 60
MAX_REASONABLE_WAIT = 90

# --- Random seed, so fixed-time and adaptive runs see identical traffic ---
RANDOM_SEED = 42

# --- Emergency scenario injected into the adaptive run only (fixed-time
# has no way to react to it -- that's the point of the comparison) ---
EMERGENCY_LANE = "West"
EMERGENCY_START_SECOND = 1800   # 30 minutes in
EMERGENCY_DURATION_SECONDS = 20
