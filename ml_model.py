# ml_model.py

def predict_popular_meal(reservations, top_n=5):
    if not reservations:
        return []

    counts = {}
    for r in reservations:
        counts[r.meal_name] = counts.get(r.meal_name, 0) + 1

    # Sort meals by count descending
    sorted_meals = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    # Return top N popular meals
    return sorted_meals[:top_n]  # list of tuples [(meal_name, count), ...]


def predict_rush_hour(reservations):
    # Example: return top 3 busiest hours
    counts = {}
    for r in reservations:
        if r.status != 'Approved':
            continue
        counts[r.time_slot] = counts.get(r.time_slot, 0) + 1

    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_counts[:3]  # list of tuples


