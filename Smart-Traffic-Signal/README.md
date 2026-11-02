# Smart Traffic Signal: Adaptive Signal Optimization

Adaptive traffic signal optimization framework using Hadoop-based Big Data analytics, multi-factor decision logic, and live simulation.

## Project Structure

- `dashboard.html`: Interactive web dashboard & live junction simulation with scenario controls, priority reasoning, and real-time comparative metrics.
- `run_dashboard.py` / `run_dashboard.bat`: One-click dashboard launchers.
- `optimizer/`: 4-tier decision engine (`optimizer.py`) with emergency routing, historical trends, coordination signals, and normalization.
- `simulation/`: 4-way intersection simulation comparing fixed-time baseline vs. adaptive controller (`run_comparison.py`), generating timeline charts (`signal_timeline.png`).

## Running the Dashboard

### Option 1: Direct Browser Launch
Double-click `dashboard.html` or `run_dashboard.bat` to launch the live interactive dashboard in your default browser.

### Option 2: Local Python Server
Run:
```bash
python run_dashboard.py
```
Then navigate to: `http://localhost:8080/dashboard.html`

## Running the Simulation & Optimizer

### Run the Optimizer Scenarios (Normal, Local Emergency, Corridor Emergency):
```bash
cd optimizer
python optimizer.py
```

### Run the Simulation Comparison (Fixed vs Adaptive):
```bash
cd simulation
python run_comparison.py
```
Or multi-seed comparison across seeds 42, 7, 123:
```bash
python run_comparison.py --multiseed
```
