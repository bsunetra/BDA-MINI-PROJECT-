from config import LIVE_WEIGHTS


def calculate_live_score(density, waiting, congestion):
    return (
        LIVE_WEIGHTS["density"] * density +
        LIVE_WEIGHTS["waiting"] * waiting +
        LIVE_WEIGHTS["congestion"] * congestion
    )