from app.eta import calculate_distance, calculate_eta
from app.routes import get_route
from app.signal_manager import get_signal


TRIGGER_TIME = 30
PASS_DISTANCE = 50


def process_ambulance_signals(ambulance):

    route = get_route()

    upcoming_junctions = []

    for junction in route:

        distance = calculate_distance(
            ambulance["latitude"],
            ambulance["longitude"],
            junction["latitude"],
            junction["longitude"]
        )

        eta = calculate_eta(
            distance,
            ambulance["speed"]
        )

        if eta is None:
            continue

        upcoming_junctions.append({
            "junction": junction,
            "distance": distance,
            "eta": eta
        })

    # Nearest junction first
    upcoming_junctions.sort(
        key=lambda x: x["distance"]
    )

    for item in upcoming_junctions:

        junction = item["junction"]
        signal = get_signal(junction["junction_id"])

        # If ambulance is already very close,
        # consider this junction passed.
        if item["distance"] <= PASS_DISTANCE:

            signal.release()

            continue

        # Request priority for the nearest junction
        # within the trigger time.
        if item["eta"] <= TRIGGER_TIME:

            signal_result = signal.request_green()

            return [{
                "junction_id": junction["junction_id"],
                "distance_meters": round(item["distance"], 2),
                "eta_seconds": round(item["eta"], 2),
                "signal": signal_result
            }]

    return []

def advance_signal(junction_id):
    signal = get_signal(junction_id)

    status = signal.get_status()
    current_state = status["state"]

    if current_state == "GREEN_REQUESTED":
        return signal.start_clearance()

    elif current_state == "CLEARANCE":
        return signal.activate_emergency_green()

    elif current_state == "EMERGENCY_GREEN":
        return {
            "success": True,
            "message": "Emergency green is active",
            "junction_id": junction_id,
            "state": current_state
        }

    return {
        "success": False,
        "message": "Signal is not ready for progression",
        "junction_id": junction_id,
        "state": current_state
    }

def check_and_release_signal(ambulance, junction_id):
    route = get_route()

    junction = None

    for item in route:
        if item["junction_id"] == junction_id:
            junction = item
            break

    if junction is None:
        return {
            "success": False,
            "message": "Junction not found"
        }

    distance = calculate_distance(
        ambulance["latitude"],
        ambulance["longitude"],
        junction["latitude"],
        junction["longitude"]
    )

    signal = get_signal(junction_id)
    status = signal.get_status()

    # 50 meters is our simulation pass threshold
    if distance <= PASS_DISTANCE:

        if status["state"] == "EMERGENCY_GREEN":
            result = signal.release()

            return {
                "success": True,
                "message": "Ambulance passed junction. Signal released.",
                "junction_id": junction_id,
                "distance_meters": round(distance, 2),
                "signal": result
            }

    return {
        "success": False,
        "message": "Ambulance has not passed the junction yet.",
        "junction_id": junction_id,
        "distance_meters": round(distance, 2),
        "state": status["state"]
    }

def get_nearby_junctions(ambulance, radius=1000):
    route = get_route()

    nearby = []

    for junction in route:

        distance = calculate_distance(
            ambulance["latitude"],
            ambulance["longitude"],
            junction["latitude"],
            junction["longitude"]
        )

        if distance <= radius:
            nearby.append({
                "junction_id": junction["junction_id"],
                "name": junction["name"],
                "distance_meters": round(distance, 2)
            })

    nearby.sort(key=lambda x: x["distance_meters"])

    return nearby