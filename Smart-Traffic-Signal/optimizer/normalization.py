from config import MAX_VEHICLES, MAX_WAITING_SECONDS


def normalize_density(vehicle_count, max_vehicles=MAX_VEHICLES):
    return min(vehicle_count / max_vehicles, 1)


def normalize_waiting(waiting_time, max_waiting=MAX_WAITING_SECONDS):
    return min(waiting_time / max_waiting, 1)