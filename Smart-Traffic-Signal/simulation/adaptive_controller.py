"""
Member 3 - Adaptive controller.

Wraps Member 1's optimizer (resolve_signal_decision) directly in-memory
-- no files round-tripped per cycle, since this is a live simulation
loop, not a batch job. Historical trend is still read from Member 2's
CSV once at startup: the historical layer is a daily batch job in the
real architecture, so it doesn't change within one simulated hour.

Folder layout this assumes (matches Member 1's repo structure):
    Smart-Traffic-Signal/
      optimizer/        <- Member 1's code
      simulation/        <- this folder
Set OPTIMIZER_PATH to override if you're running it somewhere else.
"""

import os
import sys
import csv

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_OPTIMIZER_PATH = os.path.normpath(
    os.path.join(_THIS_DIR, "..", "optimizer")
)
OPTIMIZER_PATH = os.environ.get("OPTIMIZER_PATH", _DEFAULT_OPTIMIZER_PATH)

if OPTIMIZER_PATH not in sys.path:
    sys.path.insert(0, OPTIMIZER_PATH)

from optimizer import resolve_signal_decision  # noqa: E402  (Member 1's module)

from sim_config import (
    LANES,
    MIN_GREEN,
    MAX_GREEN,
    MAX_REASONABLE_VEHICLES,
    MAX_REASONABLE_WAIT,
    EMERGENCY_LANE,
    EMERGENCY_START_SECOND,
    EMERGENCY_DURATION_SECONDS,
)


def load_historical_trend(csv_path=None):
    """Reads Member 2's historical_trend CSV (lane, historical_trend).
    Falls back to 0.0 for any lane not present in the file."""
    if csv_path is None:
        csv_path = os.path.join(OPTIMIZER_PATH, "sample_historical_trend.csv")
    trend = {lane: 0.0 for lane in LANES}
    if os.path.exists(csv_path):
        with open(csv_path, newline="") as f:
            for row in csv.DictReader(f):
                if row["lane"] in trend:
                    trend[row["lane"]] = float(row["historical_trend"])
    return trend


class AdaptiveController:
    def __init__(self, intersection, historical_trend=None):
        self.intersection = intersection
        self.historical_trend = historical_trend or load_historical_trend()
        self.current_lane = None
        self.seconds_remaining_in_phase = 0
        self.last_decision = None

    def _is_emergency_active(self, current_second):
        return (
            EMERGENCY_START_SECOND
            <= current_second
            < EMERGENCY_START_SECOND + EMERGENCY_DURATION_SECONDS
        )

    def _build_lane_inputs(self, current_second):
        snapshot = self.intersection.snapshot(current_second)
        emergency_here = self._is_emergency_active(current_second)

        lane_inputs = {}
        for lane in LANES:
            s = snapshot[lane]
            vehicle_count = s["queue_length"]
            avg_waiting = s["avg_waiting_estimate"]
            density_norm = min(vehicle_count / MAX_REASONABLE_VEHICLES, 1.0)
            wait_norm = min(avg_waiting / MAX_REASONABLE_WAIT, 1.0)
            congestion = round(0.6 * density_norm + 0.4 * wait_norm, 3)

            lane_inputs[lane] = {
                "live_raw": {
                    "vehicle_count": vehicle_count,
                    "avg_waiting": avg_waiting,
                    "congestion": congestion,
                    "emergency_flag": bool(emergency_here and lane == EMERGENCY_LANE),
                },
                "historical_trend": self.historical_trend.get(lane, 0.0),
            }
        return lane_inputs

    def step(self, current_second):
        """Call once per simulated second. Only re-decides once the
        current phase's green_time has elapsed (a real controller
        can't change its mind mid-phase either)."""
        if self.current_lane is None or self.seconds_remaining_in_phase <= 0:
            lane_inputs = self._build_lane_inputs(current_second)
            decision = resolve_signal_decision(lane_inputs)
            self.last_decision = decision
            self.current_lane = decision["selected_lane"]
            green_time = max(MIN_GREEN, min(MAX_GREEN, decision["green_time"]))
            self.seconds_remaining_in_phase = green_time

        self.seconds_remaining_in_phase -= 1
        return self.current_lane
