MIN_GREEN = 10
MAX_GREEN = 45

# Live-score weights. Emergency is NOT in this blend -- it's its own
# top-priority tier (Tier 1), not a weighted factor here.
LIVE_WEIGHTS = {
    "density": 0.45,
    "waiting": 0.30,
    "congestion": 0.25,
}

# How much weight historical trend gets when merged with this cycle's
# live score.
LIVE_HISTORICAL_BLEND = {
    "live": 0.65,
    "historical": 0.35,
}

# Coordination signal must reach this to override the trend/live tier.
# Placeholder until the ML model + reward function exist.
COORDINATION_OVERRIDE_THRESHOLD = 0.70

# How many junctions ahead corridor emergency pre-clearing reacts to.
# TODO: still unconfirmed by the team.
PRECLEAR_DEPTH = 2

# Normalization caps (used for OUR OWN normalize_density/normalize_waiting
# in normalization.py -- separate from Member 2's own congestion caps of
# 60 vehicles / 90 sec used inside their Spark job. Not a bug, just two
# independent scales; align them later if we want exact parity).
MAX_VEHICLES = 50
MAX_WAITING_SECONDS = 60

# Only consider an inbound ambulance if it's this close (seconds) or less.
MAX_EMERGENCY_ETA_SECONDS = 40