"""
Member 3 - Performance metrics.

Per Review 1's requirement: prepare the before-vs-after comparison
FORMAT now, don't fill in improvement percentages until a real run has
happened. compare_runs() below computes real numbers from whatever
simulation run you pass it -- nothing here is a placeholder percentage,
it's computed from the actual queue/wait data each run produces.

Reports all five metrics the work-allocation doc asks for: average
waiting time, average queue length, congestion, throughput, and signal
efficiency.

Congestion uses the same 0.6*density + 0.4*wait formula Member 2 uses
in 02_live_lane_aggregation.py, so it means the same thing here as it
does in the Hadoop pipeline.

Signal efficiency = % of green time actually spent clearing a queue,
vs. green given to a lane with nobody in it -- this is the metric that
speaks directly to the project's own problem statement ("wasted signal
time... green phases run on schedule, not on demand").
"""

from sim_config import LANES


def summarize_run(intersection, queue_length_samples, congestion_samples,
                   green_time_stats, label):
    """
    intersection: the FourWayIntersection after a full run (holds
      completed_waits per lane).
    queue_length_samples: dict lane -> list[int], one queue-length
      reading per simulated second.
    congestion_samples: dict lane -> list[float], one congestion score
      (0-1) per simulated second.
    green_time_stats: dict lane -> {"green_seconds": int, "wasted_green_seconds": int}
      wasted = green was given while that lane's queue was empty.
    """
    per_lane = {}
    total_waits = []
    total_throughput = 0
    total_green_seconds = 0
    total_wasted_green_seconds = 0

    for lane in LANES:
        q = intersection.lanes[lane]
        waits = q.completed_waits
        queue_samples = queue_length_samples[lane]
        cong_samples = congestion_samples[lane]
        g = green_time_stats[lane]

        avg_wait = sum(waits) / len(waits) if waits else 0.0
        max_wait = max(waits) if waits else 0.0
        avg_queue = sum(queue_samples) / len(queue_samples) if queue_samples else 0.0
        max_queue = max(queue_samples) if queue_samples else 0
        avg_congestion = sum(cong_samples) / len(cong_samples) if cong_samples else 0.0

        green_seconds = g["green_seconds"]
        wasted = g["wasted_green_seconds"]
        efficiency_pct = (
            round((green_seconds - wasted) / green_seconds * 100, 1)
            if green_seconds > 0 else 0.0
        )

        per_lane[lane] = {
            "avg_wait_sec": round(avg_wait, 2),
            "max_wait_sec": round(max_wait, 2),
            "avg_queue_length": round(avg_queue, 2),
            "max_queue_length": max_queue,
            "avg_congestion": round(avg_congestion, 3),
            "throughput_vehicles": len(waits),
            "green_seconds": green_seconds,
            "wasted_green_seconds": wasted,
            "signal_efficiency_pct": efficiency_pct,
        }
        total_waits.extend(waits)
        total_throughput += len(waits)
        total_green_seconds += green_seconds
        total_wasted_green_seconds += wasted

    overall_avg_wait = sum(total_waits) / len(total_waits) if total_waits else 0.0
    overall_efficiency_pct = (
        round((total_green_seconds - total_wasted_green_seconds) / total_green_seconds * 100, 1)
        if total_green_seconds > 0 else 0.0
    )

    return {
        "label": label,
        "per_lane": per_lane,
        "overall_avg_wait_sec": round(overall_avg_wait, 2),
        "overall_throughput_vehicles": total_throughput,
        "overall_signal_efficiency_pct": overall_efficiency_pct,
    }


def compare_runs(fixed_summary, adaptive_summary):
    """Computes the actual before/after percentage change -- only
    called after both runs have completed, per the 'no numbers before
    experiments' rule."""
    fixed_wait = fixed_summary["overall_avg_wait_sec"]
    adaptive_wait = adaptive_summary["overall_avg_wait_sec"]

    if fixed_wait > 0:
        wait_change_pct = round((fixed_wait - adaptive_wait) / fixed_wait * 100, 1)
    else:
        wait_change_pct = 0.0

    fixed_throughput = fixed_summary["overall_throughput_vehicles"]
    adaptive_throughput = adaptive_summary["overall_throughput_vehicles"]
    if fixed_throughput > 0:
        throughput_change_pct = round(
            (adaptive_throughput - fixed_throughput) / fixed_throughput * 100, 1
        )
    else:
        throughput_change_pct = 0.0

    fixed_eff = fixed_summary["overall_signal_efficiency_pct"]
    adaptive_eff = adaptive_summary["overall_signal_efficiency_pct"]
    efficiency_change_pts = round(adaptive_eff - fixed_eff, 1)

    return {
        "avg_wait_reduction_pct": wait_change_pct,
        "throughput_change_pct": throughput_change_pct,
        "signal_efficiency_change_pts": efficiency_change_pts,
    }


def print_summary(summary):
    print("=" * 78)
    print(f" {summary['label']}")
    print("=" * 78)
    for lane, m in summary["per_lane"].items():
        print(
            f"{lane:6s}  avg_wait={m['avg_wait_sec']:6.2f}s  "
            f"max_wait={m['max_wait_sec']:6.2f}s  "
            f"avg_queue={m['avg_queue_length']:5.2f}  "
            f"max_queue={m['max_queue_length']:3d}  "
            f"congestion={m['avg_congestion']:.3f}  "
            f"throughput={m['throughput_vehicles']:4d}  "
            f"efficiency={m['signal_efficiency_pct']:5.1f}%"
        )
    print("-" * 78)
    print(f"Overall avg wait      : {summary['overall_avg_wait_sec']} sec")
    print(f"Overall throughput    : {summary['overall_throughput_vehicles']} vehicles")
    print(f"Overall signal eff.   : {summary['overall_signal_efficiency_pct']}%\n")


def print_comparison(fixed_summary, adaptive_summary, diff):
    print("=" * 52)
    print(" FIXED-TIME vs ADAPTIVE -- SUMMARY")
    print("=" * 52)
    print(f"Fixed-time avg wait   : {fixed_summary['overall_avg_wait_sec']} sec")
    print(f"Adaptive avg wait     : {adaptive_summary['overall_avg_wait_sec']} sec")
    print(f"Avg wait reduction    : {diff['avg_wait_reduction_pct']}%")
    print(f"Fixed-time throughput : {fixed_summary['overall_throughput_vehicles']}")
    print(f"Adaptive throughput   : {adaptive_summary['overall_throughput_vehicles']}")
    print(f"Throughput change     : {diff['throughput_change_pct']}%")
    print(f"Fixed-time efficiency : {fixed_summary['overall_signal_efficiency_pct']}%")
    print(f"Adaptive efficiency   : {adaptive_summary['overall_signal_efficiency_pct']}%")
    print(f"Efficiency change     : {diff['signal_efficiency_change_pts']} pts")
