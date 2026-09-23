"""
Emergency priority has two sources:
  1. LOCAL: emergency_flag is True for a lane RIGHT NOW (ambulance
     physically detected at this junction) -- from Member 2's live
     aggregation output.
  2. CORRIDOR: an ambulance is approaching from an upstream junction
     and hasn't arrived yet -- from Member 2's ambulance_events +
     intersection_adjacency tables, via emergency_context.py.

Local always outranks corridor -- an ambulance already here is more
urgent than one still approaching.
"""

from config import PRECLEAR_DEPTH


def get_emergency_route_priority(lane, local_emergency_flag=False, emergency_context=None):
    if local_emergency_flag:
        return PRECLEAR_DEPTH + 1  # highest possible urgency

    if emergency_context and emergency_context.get("lane") == lane:
        junctions_ahead = emergency_context.get("junctions_ahead", 0)
        if junctions_ahead <= PRECLEAR_DEPTH:
            return max(1, PRECLEAR_DEPTH - junctions_ahead + 1)

    return 0