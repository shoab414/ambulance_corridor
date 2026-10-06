from app.signal_controller import process_ambulance_signals
from fastapi import FastAPI, HTTPException
from app.routes import get_route
from app.ambulance import AmbulanceLocation, StartTrip
from app.eta import calculate_distance, calculate_eta
from app.signal_manager import get_signal
from app.signal_controller import (
    advance_signal,
    check_and_release_signal,
    get_nearby_junctions
)
app = FastAPI(
    title="Ambulance Green Corridor API",
    description="Backend for ambulance green corridor coordination",
    version="1.0.0"
)


# Temporary live ambulance storage
ambulances = {}


@app.get("/")
def home():
    return {
        "message": "Ambulance Green Corridor API is running",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/ambulance/location")
def update_location(data: AmbulanceLocation):

    ambulances[data.ambulance_id] = {
        "latitude": data.latitude,
        "longitude": data.longitude,
        "speed": data.speed
    }

    signal_results = process_ambulance_signals(
        ambulances[data.ambulance_id]
    )

    return {
        "message": "Ambulance location updated",
        "ambulance_id": data.ambulance_id,
        "latitude": data.latitude,
        "longitude": data.longitude,
        "speed": data.speed,
        "signal_actions": signal_results
    }


@app.get("/ambulance/{ambulance_id}")
def get_ambulance(ambulance_id: str):

    if ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    return {
        "ambulance_id": ambulance_id,
        **ambulances[ambulance_id]
    }

@app.post("/ambulance/start-trip")
def start_trip(data: StartTrip):

    if data.ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulances[data.ambulance_id]["destination"] = data.destination
    ambulances[data.ambulance_id]["trip_status"] = "active"

    return {
        "message": "Ambulance trip started",
        "ambulance_id": data.ambulance_id,
        "destination": data.destination,
        "trip_status": "active"
    }

@app.get("/route")
def get_ambulance_route():
    return {
        "route": get_route()
    }

@app.get("/ambulance/{ambulance_id}/eta")
def ambulance_eta(ambulance_id: str):

    if ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulance = ambulances[ambulance_id]

    route = get_route()

    results = []

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

        results.append({
            "junction_id": junction["junction_id"],
            "junction_name": junction["name"],
            "distance_meters": round(distance, 2),
            "eta_seconds": round(eta, 2) if eta is not None else None
        })

    return {
        "ambulance_id": ambulance_id,
        "speed": ambulance["speed"],
        "upcoming_junctions": results
    }

@app.get("/signal/{junction_id}")
def get_signal_status(junction_id: str):

    signal = get_signal(junction_id)

    return signal.get_status()

@app.post("/ambulance/{ambulance_id}/request-green")
def request_green(ambulance_id: str):

    if ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulance = ambulances[ambulance_id]
    route = get_route()

    trigger_time = 30
    requested_signals = []

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

        if eta is not None and eta <= trigger_time:

            signal = get_signal(junction["junction_id"])
            result = signal.request_green()

            requested_signals.append({
                "junction_id": junction["junction_id"],
                "eta_seconds": round(eta, 2),
                "signal_result": result
            })

    return {
        "ambulance_id": ambulance_id,
        "trigger_time_seconds": trigger_time,
        "requested_signals": requested_signals
    }

@app.post("/signal/{junction_id}/clearance")
def start_signal_clearance(junction_id: str):

    signal = get_signal(junction_id)

    return signal.start_clearance()

@app.post("/signal/{junction_id}/emergency-green")
def activate_emergency_green(junction_id: str):

    signal = get_signal(junction_id)

    return signal.activate_emergency_green()

@app.post("/signal/{junction_id}/release")
def release_signal(junction_id: str):

    signal = get_signal(junction_id)

    return signal.release()

@app.post("/signal/{junction_id}/advance")
def advance_signal_state(junction_id: str):

    return advance_signal(junction_id)

@app.post("/ambulance/{ambulance_id}/check-pass/{junction_id}")
def check_ambulance_pass(ambulance_id: str, junction_id: str):

    if ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulance = ambulances[ambulance_id]

    return check_and_release_signal(
        ambulance,
        junction_id
    )

@app.get("/ambulance/{ambulance_id}/geofence")
def ambulance_geofence(ambulance_id: str):

    if ambulance_id not in ambulances:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found"
        )

    ambulance = ambulances[ambulance_id]

    return {
        "ambulance_id": ambulance_id,
        "radius_meters": 1000,
        "nearby_junctions": get_nearby_junctions(ambulance)
    }