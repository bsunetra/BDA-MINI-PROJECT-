"""
Member 3 - Signal visualization.

Covers the Review 1 checklist item: "signal visualization: current
signal state, traffic condition and recommended green time."

Two outputs:
  1. print_cycle_table()  -- console table, one row per phase change:
     when it started, which lane got green, why (tier), for how long,
     and what each lane's queue looked like at that moment.
  2. plot_signal_timeline() -- a Gantt-style PNG: which lane was green,
     over simulated time, fixed-time vs adaptive side by side. Emergency
     phases are colored differently so the override is visible at a
     glance -- meant for the review slides, not just the terminal.
"""

import matplotlib
matplotlib.use("Agg")  # no display in this environment / on most CI-style setups
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from sim_config import LANES

LANE_COLORS = {
    "North": "#4C72B0",
    "South": "#55A868",
    "East": "#C44E52",
    "West": "#8172B2",
}
EMERGENCY_COLOR = "#E8000B"


class CycleLogger:
    """Collects one entry per phase change during a run_simulation() call."""

    def __init__(self):
        self.entries = []

    def log(self, start_second, lane, tier, green_time, queue_snapshot):
        self.entries.append({
            "start_second": start_second,
            "lane": lane,
            "tier": tier,
            "green_time": green_time,
            "queue_snapshot": queue_snapshot,
        })

    def __len__(self):
        return len(self.entries)


def format_hms(second):
    m, s = divmod(int(second), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def print_cycle_table(logger, label, max_rows=25):
    print("=" * 78)
    print(f" SIGNAL LOG -- {label}  ({len(logger)} phase changes total)")
    print("=" * 78)
    print(f"{'time':8s} {'lane':6s} {'tier':11s} {'green':6s} "
          + " ".join(f"{l[:1]}-q" for l in LANES))
    shown = logger.entries[:max_rows]
    for e in shown:
        q = e["queue_snapshot"]
        q_str = " ".join(f"{q[l]['queue_length']:3d}" for l in LANES)
        print(
            f"{format_hms(e['start_second']):8s} {e['lane']:6s} "
            f"{e['tier']:11s} {e['green_time']:3d}s   {q_str}"
        )
    if len(logger.entries) > max_rows:
        print(f"... ({len(logger.entries) - max_rows} more phase changes not shown)")
    print()


def plot_signal_timeline(fixed_logger, adaptive_logger, sim_duration_seconds,
                          output_path="signal_timeline.png"):
    fig, axes = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

    for ax, logger, title in [
        (axes[0], fixed_logger, "Fixed-Time Baseline"),
        (axes[1], adaptive_logger, "Adaptive Controller"),
    ]:
        lane_y = {lane: i for i, lane in enumerate(LANES)}
        for i, entry in enumerate(logger.entries):
            start = entry["start_second"]
            end = (
                logger.entries[i + 1]["start_second"]
                if i + 1 < len(logger.entries)
                else sim_duration_seconds
            )
            duration = end - start
            color = EMERGENCY_COLOR if entry["tier"] == "emergency" else LANE_COLORS[entry["lane"]]
            y = lane_y[entry["lane"]]
            ax.broken_barh([(start / 60, duration / 60)], (y - 0.4, 0.8), facecolors=color)

        ax.set_yticks(list(lane_y.values()))
        ax.set_yticklabels(list(lane_y.keys()))
        ax.set_title(title)
        ax.set_xlim(0, sim_duration_seconds / 60)
        ax.grid(axis="x", linestyle="--", alpha=0.3)

    axes[1].set_xlabel("Simulated time (minutes)")

    legend_handles = [mpatches.Patch(color=c, label=l) for l, c in LANE_COLORS.items()]
    legend_handles.append(mpatches.Patch(color=EMERGENCY_COLOR, label="Emergency override"))
    fig.legend(handles=legend_handles, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1.02))

    fig.suptitle("Which lane has the green signal, over time", y=1.08)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path
