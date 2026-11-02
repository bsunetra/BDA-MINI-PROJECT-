"""
Member 3 - Fixed-time baseline controller.

The comparison case Review 1 needs: round-robins through the four
lanes in a fixed order, fixed green duration every time, completely
blind to queue length or waiting time. This is deliberately dumb --
that's the point being demonstrated against the adaptive controller.
"""

from sim_config import LANES, FIXED_GREEN_PER_LANE


class FixedTimeController:
    def __init__(self):
        self._lane_index = 0
        self.current_lane = LANES[self._lane_index]
        self.seconds_remaining_in_phase = FIXED_GREEN_PER_LANE

    def step(self, current_second=None):
        """Call once per simulated second. Advances to the next lane
        when the current one's fixed green time runs out.
        current_second is accepted but unused -- kept so this controller
        and AdaptiveController share the same call signature in
        run_comparison.py's loop."""
        self.seconds_remaining_in_phase -= 1
        if self.seconds_remaining_in_phase <= 0:
            self._lane_index = (self._lane_index + 1) % len(LANES)
            self.current_lane = LANES[self._lane_index]
            self.seconds_remaining_in_phase = FIXED_GREEN_PER_LANE
        return self.current_lane
