"""
Member 3 - Main entry point.

Runs the SAME generated traffic (identical arrivals, identical random
seed) through the fixed-time baseline and the adaptive controller, then
prints per-lane and overall metrics (wait, queue, congestion,
throughput, signal efficiency), the before/after comparison, a signal
log, and saves a timeline chart for the review slides.

Run:
    python3 run_comparison.py            # single seed (42), full detail
    python3 run_comparison.py --multiseed  # 3 seeds, summary only --
                                            # sanity-checks the headline
                                            # number isn't a one-off
"""

import sys

from sim_config import (
    LANES,
    SIM_DURATION_SECONDS,
    FIXED_GREEN_PER_LANE,
    MAX_REASONABLE_VEHICLES,
    MAX_REASONABLE_WAIT,
)
from traffic_generator import generate_arrivals
from queue_model import FourWayIntersection
from fixed_time_controller import FixedTimeController
from adaptive_controller import AdaptiveController
from metrics import summarize_run, compare_runs, print_summary, print_comparison
from visualization import CycleLogger, print_cycle_table, plot_signal_timeline


def run_simulation(controller_factory, arrivals, label):
    """controller_factory: callable(intersection) -> controller object
    with a .step(current_second) -> lane_name method.

    Returns (summary, cycle_logger). cycle_logger records one entry
    each time the green lane changes -- the "signal state / traffic
    condition / recommended green time" trail for Review 1's demo."""
    intersection = FourWayIntersection()
    controller = controller_factory(intersection)
    queue_length_samples = {lane: [] for lane in LANES}
    congestion_samples = {lane: [] for lane in LANES}
    green_time_stats = {lane: {"green_seconds": 0, "wasted_green_seconds": 0} for lane in LANES}
    logger = CycleLogger()
    previous_lane = None

    for t in range(SIM_DURATION_SECONDS):
        this_second_arrivals = {lane: arrivals[lane][t] for lane in LANES}
        intersection.step_arrivals(t, this_second_arrivals)

        green_lane = controller.step(t)

        if green_lane != previous_lane:
            last_decision = getattr(controller, "last_decision", None)
            if last_decision is not None:
                tier = last_decision["tier"]
                green_time = last_decision["green_time"]
            else:
                tier = "fixed"
                green_time = FIXED_GREEN_PER_LANE
            logger.log(t, green_lane, tier, green_time, intersection.snapshot(t))
            previous_lane = green_lane

        # Green-time utilization: was this green second given to an
        # empty lane? Directly measures the "wasted signal time" the
        # project's own problem statement is about.
        if green_lane is not None:
            green_time_stats[green_lane]["green_seconds"] += 1
            if intersection.lanes[green_lane].current_length() == 0:
                green_time_stats[green_lane]["wasted_green_seconds"] += 1

        intersection.step_discharge(t, green_lane)

        snapshot = intersection.snapshot(t)
        for lane in LANES:
            q_len = snapshot[lane]["queue_length"]
            avg_wait = snapshot[lane]["avg_waiting_estimate"]
            queue_length_samples[lane].append(q_len)

            density_norm = min(q_len / MAX_REASONABLE_VEHICLES, 1.0)
            wait_norm = min(avg_wait / MAX_REASONABLE_WAIT, 1.0)
            congestion_samples[lane].append(0.6 * density_norm + 0.4 * wait_norm)

    summary = summarize_run(
        intersection, queue_length_samples, congestion_samples, green_time_stats, label
    )
    return summary, logger


def run_once(seed, verbose=True):
    arrivals = generate_arrivals(start_hour=8, seed=seed)

    fixed_summary, fixed_log = run_simulation(
        lambda intersection: FixedTimeController(),
        arrivals,
        f"FIXED-TIME BASELINE (seed={seed}, 1 simulated hour, 8am start)",
    )
    adaptive_summary, adaptive_log = run_simulation(
        lambda intersection: AdaptiveController(intersection),
        arrivals,
        f"ADAPTIVE CONTROLLER (seed={seed}, same traffic, same 1 hour)",
    )
    diff = compare_runs(fixed_summary, adaptive_summary)

    if verbose:
        print_summary(fixed_summary)
        print_summary(adaptive_summary)
        print_comparison(fixed_summary, adaptive_summary, diff)
        print_cycle_table(fixed_log, "FIXED-TIME (first 25 phase changes)")
        print_cycle_table(adaptive_log, "ADAPTIVE (first 25 phase changes)")
        chart_path = plot_signal_timeline(fixed_log, adaptive_log, SIM_DURATION_SECONDS)
        print(f"Signal timeline chart saved to: {chart_path}")

    return diff


def main():
    if "--multiseed" in sys.argv:
        print("Running 3 seeds to sanity-check the headline numbers aren't a one-off run.\n")
        results = []
        for seed in [42, 7, 123]:
            diff = run_once(seed, verbose=False)
            results.append((seed, diff))
            print(
                f"seed={seed:4d}  avg_wait_reduction={diff['avg_wait_reduction_pct']:6.1f}%  "
                f"throughput_change={diff['throughput_change_pct']:6.1f}%  "
                f"efficiency_change={diff['signal_efficiency_change_pts']:6.1f} pts"
            )
        avg_wait_reduction = sum(d["avg_wait_reduction_pct"] for _, d in results) / len(results)
        print(f"\nMean avg_wait_reduction across seeds: {round(avg_wait_reduction, 1)}%")
    else:
        run_once(seed=42, verbose=True)


if __name__ == "__main__":
    main()
