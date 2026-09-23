"""
Turns Member 2's intersection_adjacency + ambulance_events rows into
the emergency_context dict resolve_signal_decision() expects, for a
given intersection.
"""

from config import MAX_EMERGENCY_ETA_SECONDS

DIRECTION_TO_LANE = {"N": "North", "S": "South", "E": "East", "W": "West"}


def build_emergency_context(intersection_id, adjacency_rows, ambulance_rows,
                             max_eta_seconds=MAX_EMERGENCY_ETA_SECONDS):
    """
    adjacency_rows: rows from intersection_adjacency
      {intersection_id, neighbor_intersection_id, direction, distance_m}
    ambulance_rows: rows from ambulance_events (latest per ambulance)
      {ambulance_id, event_ts, intersection_id, heading_deg,
       next_intersection_id, eta_seconds}

    Returns {"lane": ..., "junctions_ahead": 1} for the most urgent
    inbound ambulance at this intersection, or None if none is relevant.

    NOTE: schema only gives the immediate next hop, not a full route,
    so every inbound ambulance is treated as "1 junction ahead" -- there
    is no data yet to distinguish 1 vs 2 hops out.
    """
    adjacency_lookup = {
        (row["intersection_id"], row["neighbor_intersection_id"]): row["direction"]
        for row in adjacency_rows
    }

    candidates = []
    for amb in ambulance_rows:
        if amb.get("next_intersection_id") != intersection_id:
            continue
        direction = adjacency_lookup.get((intersection_id, amb["intersection_id"]))
        if direction is None:
            continue
        lane = DIRECTION_TO_LANE.get(direction)
        if lane is None:
            continue
        eta = amb.get("eta_seconds", 0.0)
        if eta > max_eta_seconds:
            continue
        candidates.append((lane, eta))

    if not candidates:
        return None

    lane, _eta = min(candidates, key=lambda c: c[1])  # lowest ETA = most urgent
    return {"lane": lane, "junctions_ahead": 1}