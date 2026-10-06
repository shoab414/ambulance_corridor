from pydantic import BaseModel


class AmbulanceLocation(BaseModel):
    ambulance_id: str
    latitude: float
    longitude: float
    speed: float


class StartTrip(BaseModel):
    ambulance_id: str
    destination: str