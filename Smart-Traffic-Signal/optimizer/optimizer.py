import json
import pandas as pd

from config import MIN_GREEN, MAX_GREEN, COORDINATION_OVERRIDE_THRESHOLD
from normalization import normalize_density, normalize_waiting
from live_score import calculate_live_score
from merge import merge_live_and_historical
from coordination import get_coordination_signal
from emergency_route import get_emergency_route_priority
from emergency_context import build_emergency_context


def calculate_green_time(score):
    return round(MIN_GREEN + score * (MAX_GREEN - MIN_GREEN))


# ---------------------------------------------------------------
# Readers -- one function per input source. If any of Member 2's
# formats change again, fix the matching reader here only.
# ---------------------------------------------------------------

def read_live_lanes(json_path):
    with open(json_path) as f:
        return json.load(f)


def read_historical_trend(csv_path):
    return pd.read_csv(csv_path).to_dict(orient="records")


def read_adjacency(csv_path):
    return pd.read_csv(csv_path).to_dict(orient="records")


def read_ambulance_events(csv_path):
    return pd.read_csv(csv_path).to_dict(orient="records")


# ---------------------------------------------------------------
# Adapter: merges live + historical into one internal shape
# ---------------------------------------------------------------

def build_lane_inputs(live_rows, historical_rows):
    """
    live_rows: list of dicts exactly as 02_live_lane_aggregation.py
      prints, one per lane.
    historical_rows: list of dicts from the historical_trend Hive
      table (intersection_id, lane, trend_date, historical_trend).

    *** ADAPTER POINT *** -- the only place to edit if Member 2's
    field names change again.
    """
    # keep only the latest trend_date per lane
    hist_lookup = {}
    for row in historical_rows:
        lane = row["lane"]
        existing = hist_lookup.get(lane)
        if existing is None or row["trend_date"] > existing["trend_date"]:
            hist_lookup[lane] = row

    lanes = {}
    for row in live_rows:
        lane = row["lane"]
        hist = hist_lookup.get(lane, {"historical_trend": 0.0})
        lanes[lane] = {
            "live_raw": {
                "vehicle_count": row["vehicle_count"],
                "avg_waiting": row["avg_waiting"],
                "congestion": row["congestion"],
                "emergency_flag": row.get("emergency_flag", False),
            },
            "historical_trend": hist.get("historical_trend", 0.0),
        }
    return lanes


# ---------------------------------------------------------------
# Core decision logic
# ---------------------------------------------------------------

def resolve_signal_decision(lane_inputs, network_state=None, emergency_context=None):
    """
    Explicit tiered conflict resolution:
        Emergency > Coordination > Historical trend > Live-only

    Each tier is checked in order. The first tier with a clear signal
    decides the lane; lower tiers aren't consulted once a higher tier
    fires. Deliberately NOT one blended formula across all factors --
    the team asked for explicit precedence, not implied weighting.
    """
    lanes = list(lane_inputs.keys())

    # ---- Tier 1: Emergency (local flag OR corridor-predicted) ----
    emergency_scores = {
        lane: get_emergency_route_priority(
            lane,
            local_emergency_flag=lane_inputs[lane]["live_raw"]["emergency_flag"],
            emergency_context=emergency_context,
        )
        for lane in lanes
    }
    if any(score > 0 for score in emergency_scores.values()):
        selected = max(emergency_scores, key=emergency_scores.get)
        return {
            "selected_lane": selected,
            "tier": "emergency",
            "score": emergency_scores[selected],
            "green_time": MAX_GREEN,
            "all_scores": emergency_scores,
        }

    # ---- Tier 2: Coordination signal (network-level ML) ----
    coordination_scores = {
        lane: get_coordination_signal(lane, network_state) for lane in lanes
    }
    top_coord_lane = max(coordination_scores, key=coordination_scores.get)
    if coordination_scores[top_coord_lane] >= COORDINATION_OVERRIDE_THRESHOLD:
        green_time = calculate_green_time(coordination_scores[top_coord_lane])
        return {
            "selected_lane": top_coord_lane,
            "tier": "coordination",
            "score": coordination_scores[top_coord_lane],
            "green_time": green_time,
            "all_scores": coordination_scores,
        }

    # ---- Tier 3 & 4: Historical trend + Live, merged ----
    merged_scores = {}
    for lane, data in lane_inputs.items():
        live = data["live_raw"]
        density = normalize_density(live["vehicle_count"])
        waiting = normalize_waiting(live["avg_waiting"])
        congestion = live["congestion"]

        live_score = calculate_live_score(density, waiting, congestion)
        merged_scores[lane] = merge_live_and_historical(
            live_score, data["historical_trend"]
        )

    selected = max(merged_scores, key=merged_scores.get)
    green_time = calculate_green_time(merged_scores[selected])
    return {
        "selected_lane": selected,
        "tier": "trend_live",
        "score": round(merged_scores[selected], 3),
        "green_time": green_time,
        "all_scores": {k: round(v, 3) for k, v in merged_scores.items()},
    }


# ---------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------

def run_optimizer(intersection_id, live_json_path, historical_csv_path,
                   adjacency_csv_path=None, ambulance_csv_path=None,
                   network_state=None):
    live_rows = read_live_lanes(live_json_path)
    historical_rows = read_historical_trend(historical_csv_path)
    lane_inputs = build_lane_inputs(live_rows, historical_rows)

    emergency_context = None
    if adjacency_csv_path and ambulance_csv_path:
        adjacency_rows = read_adjacency(adjacency_csv_path)
        ambulance_rows = read_ambulance_events(ambulance_csv_path)
        emergency_context = build_emergency_context(
            intersection_id, adjacency_rows, ambulance_rows
        )

    return resolve_signal_decision(lane_inputs, network_state, emergency_context)


def print_result(title, result):
    print("=" * 46)
    print(f" {title}")
    print("=" * 46)
    print(f"Decision tier   : {result['tier']}")
    print(f"NEXT GREEN      : {result['selected_lane'].upper()}")
    print(f"Score           : {result['score']}")
    print(f"GREEN TIME      : {result['green_time']} seconds")
    print(f"All lane scores : {result['all_scores']}\n")


if __name__ == "__main__":
    # ---- Scenario 1: normal mode (Tier 3/4: trend + live) at J1 ----
    result_normal = run_optimizer(
        intersection_id="J1",
        live_json_path="sample_live_lanes.json",
        historical_csv_path="sample_historical_trend.csv",
    )
    print_result("SCENARIO 1: NORMAL MODE (J1)", result_normal)

    # ---- Scenario 2: local emergency at J1 (ambulance physically there) ----
    result_local_emergency = run_optimizer(
        intersection_id="J1",
        live_json_path="sample_live_lanes_local_emergency.json",
        historical_csv_path="sample_historical_trend.csv",
    )
    print_result("SCENARIO 2: LOCAL EMERGENCY (J1, West)", result_local_emergency)

    # ---- Scenario 3: corridor emergency at J2 (ambulance inbound from J1) ----
    result_corridor = run_optimizer(
        intersection_id="J2",
        live_json_path="sample_live_lanes_j2.json",
        historical_csv_path="sample_historical_trend_j2.csv",
        adjacency_csv_path="sample_adjacency.csv",
        ambulance_csv_path="sample_ambulance_events.csv",
    )
    print_result("SCENARIO 3: CORRIDOR EMERGENCY (J2, pre-clear from J1)", result_corridor)