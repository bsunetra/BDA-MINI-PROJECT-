"""
Member 3 - Four-way intersection queue model.

One queue per lane (North/South/East/West). Each second:
  - new arrivals join the back of their lane's queue
  - if that lane currently has the green, vehicles depart at
    SATURATION_FLOW_VEH_PER_SEC (capped by how many are actually queued)

Tracks, per lane, per vehicle: how long it waited (arrival second to
departure second). That per-vehicle wait list is what the metrics module
uses for exact averages -- no queue-length approximation needed.
"""

from sim_config import LANES, SATURATION_FLOW_VEH_PER_SEC


class LaneQueue:
    def __init__(self, name):
        self.name = name
        self.queue = []          # list of arrival-second timestamps, FIFO
        self.completed_waits = []  # seconds each departed vehicle waited
        self.last_green_start = None
        self.last_served_second = 0  # last second this lane's queue moved

    def add_arrivals(self, current_second, count):
        self.queue.extend([current_second] * count)

    def current_length(self):
        return len(self.queue)

    def current_wait_estimate(self, current_second):
        """Average age of vehicles currently queued -- used as the
        'avg_waiting' live signal fed to the adaptive optimizer each
        cycle (it doesn't know the future, only what's queued right now)."""
        if not self.queue:
            return 0.0
        return sum(current_second - a for a in self.queue) / len(self.queue)


class FourWayIntersection:
    """Owns one LaneQueue per lane and applies a discharge accumulator
    so a saturation flow < 1 veh/sec still departs vehicles correctly
    over many 1-second steps (e.g. 0.5/sec = 1 vehicle every 2 steps)."""

    def __init__(self):
        self.lanes = {name: LaneQueue(name) for name in LANES}
        self._discharge_accumulator = {name: 0.0 for name in LANES}

    def step_arrivals(self, current_second, arrivals_this_second):
        for lane, count in arrivals_this_second.items():
            self.lanes[lane].add_arrivals(current_second, count)

    def step_discharge(self, current_second, green_lane):
        """Call once per simulated second. Only green_lane discharges."""
        if green_lane is None:
            return 0
        self._discharge_accumulator[green_lane] += SATURATION_FLOW_VEH_PER_SEC
        depart_now = int(self._discharge_accumulator[green_lane])
        self._discharge_accumulator[green_lane] -= depart_now
        lane_obj = self.lanes[green_lane]
        departed = min(depart_now, lane_obj.current_length())
        for _ in range(departed):
            arrival_second = lane_obj.queue.pop(0)
            lane_obj.completed_waits.append(current_second - arrival_second)
        lane_obj.last_served_second = current_second
        return departed

    def snapshot(self, current_second):
        """Current queue length + wait-estimate per lane -- the shape the
        adaptive controller turns into an optimizer live_rows input."""
        return {
            lane: {
                "queue_length": q.current_length(),
                "avg_waiting_estimate": q.current_wait_estimate(current_second),
            }
            for lane, q in self.lanes.items()
        }
