def normalize_density(vehicle_count, max_vehicles=50):
    return min(vehicle_count / max_vehicles, 1)

def normalize_waiting(waiting_time, max_waiting=60):
    return min(waiting_time / max_waiting, 1)