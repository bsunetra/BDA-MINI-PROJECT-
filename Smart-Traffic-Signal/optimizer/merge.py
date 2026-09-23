from config import LIVE_HISTORICAL_BLEND


def merge_live_and_historical(live_score, historical_trend_score):
    """
    Combines THIS cycle's live score with the Hadoop-mined historical
    trend score for the same lane. Two separate inputs on purpose --
    live updates every cycle (Member 2's 02_live_lane_aggregation.py),
    historical updates daily (Member 2's 03_historical_trend.py).
    """
    w = LIVE_HISTORICAL_BLEND
    return w["live"] * live_score + w["historical"] * historical_trend_score