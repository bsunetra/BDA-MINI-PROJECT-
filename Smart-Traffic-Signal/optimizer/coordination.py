"""
Placeholder for the ML coordination model.

NOT BUILT YET -- the reward function it should optimize (network wait
time? throughput? something else?) is still undecided. This stub lets
the pipeline run and be demoed at single-junction scope: coordination
signal defaults to 0, so Tier 2 never fires and Tier 3/4 (trend + live)
makes every decision -- exactly as agreed for Review 1.
"""


def get_coordination_signal(lane, network_state=None):
    """
    Returns 0-1: how strongly the network-level model recommends giving
    THIS lane the green right now, because it helps neighboring
    junctions more than a purely local decision would.

    TODO once ready:
      - reward function decided
      - Member 2's decision_feedback table has enough logged history
      - Member 3's multi-junction sim feeds live network_state
    """
    if network_state is None:
        return 0.0
    return network_state.get(lane, {}).get("coordination_signal", 0.0)