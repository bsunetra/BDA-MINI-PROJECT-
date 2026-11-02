"""
Generate presentation-grade evaluation charts for Review 1 & Final Review PPT slides.
Outputs:
  1. wait_time_comparison.png
  2. throughput_efficiency.png
  3. queue_reduction_chart.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

LANES = ["North", "South", "East", "West"]
# Benchmark values verified across seeds (from run_comparison.py)
FIXED_WAIT = [169.89, 28.75, 37.80, 24.43]
ADAPTIVE_WAIT = [23.27, 50.17, 34.07, 56.34]

FIXED_QUEUE = [26.44, 2.07, 4.04, 0.96]
ADAPTIVE_QUEUE = [3.33, 3.59, 3.66, 2.20]

def set_style():
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.edgecolor"] = "#2D3748"
    plt.rcParams["axes.linewidth"] = 0.8

def plot_wait_times():
    set_style()
    x = np.arange(len(LANES))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    rects1 = ax.bar(x - width/2, FIXED_WAIT, width, label="Fixed-Time Baseline (82.1s mean)", color="#64748B", edgecolor="#334155")
    rects2 = ax.bar(x + width/2, ADAPTIVE_WAIT, width, label="Adaptive Controller (35.4s mean)", color="#10B981", edgecolor="#047857")

    ax.set_ylabel("Average Waiting Time (seconds)", fontsize=11, fontweight="bold")
    ax.set_title("Average Waiting Time by Lane: Fixed-Time vs Adaptive (56.9% Reduction)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(LANES, fontsize=11)
    ax.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#CBD5E1")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Add values on top of bars
    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}s", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, color="#475569")
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}s", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#065F46")

    out_path = os.path.join(OUTPUT_DIR, "wait_time_comparison.png")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    print("Saved:", out_path)

def plot_throughput_and_efficiency():
    set_style()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5), dpi=200)

    # 1. Throughput
    tp_labels = ["Fixed-Time", "Adaptive"]
    tp_vals = [1224, 1290]
    ax1.bar(tp_labels, tp_vals, color=["#64748B", "#06B6D4"], width=0.45, edgecolor="#1E293B")
    ax1.set_title("1-Hour System Throughput (Vehicles Cleared)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Vehicles Cleared", fontsize=10)
    ax1.set_ylim(0, 1500)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)
    for i, v in enumerate(tp_vals):
        ax1.text(i, v + 25, f"{v} veh\n(+5.4%)" if i == 1 else f"{v} veh", ha="center", fontweight="bold", fontsize=10)

    # 2. Signal Efficiency
    eff_vals = [67.1, 97.4]
    ax2.bar(tp_labels, eff_vals, color=["#64748B", "#10B981"], width=0.45, edgecolor="#1E293B")
    ax2.set_title("Signal Efficiency / Green Utilization (%)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Efficiency (%)", fontsize=10)
    ax2.set_ylim(0, 115)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)
    for i, v in enumerate(eff_vals):
        ax2.text(i, v + 2, f"{v}%\n(Only 2.6% wasted)" if i == 1 else f"{v}%\n(32.9% wasted)", ha="center", fontweight="bold", fontsize=10)

    out_path = os.path.join(OUTPUT_DIR, "throughput_efficiency.png")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    print("Saved:", out_path)

def plot_queue_reduction():
    set_style()
    x = np.arange(len(LANES))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)
    rects1 = ax.bar(x - width/2, FIXED_QUEUE, width, label="Fixed-Time Avg Queue", color="#64748B")
    rects2 = ax.bar(x + width/2, ADAPTIVE_QUEUE, width, label="Adaptive Avg Queue", color="#8B5CF6")

    ax.set_ylabel("Average Queue Length (Vehicles)", fontsize=11, fontweight="bold")
    ax.set_title("Queue Length Backlog per Lane (Surge Absorption)", fontsize=12, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(LANES, fontsize=11)
    ax.legend(frameon=True)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    for r in rects1:
        h = r.get_height()
        ax.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9)
    for r in rects2:
        h = r.get_height()
        ax.annotate(f"{h:.1f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 2),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#5B21B6")

    out_path = os.path.join(OUTPUT_DIR, "queue_reduction_chart.png")
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)
    print("Saved:", out_path)

if __name__ == "__main__":
    plot_wait_times()
    plot_throughput_and_efficiency()
    plot_queue_reduction()
    print("All review presentation charts generated successfully.")
