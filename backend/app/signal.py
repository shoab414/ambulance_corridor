from enum import Enum


class SignalState(Enum):
    NORMAL = "NORMAL"
    GREEN_REQUESTED = "GREEN_REQUESTED"
    CLEARANCE = "CLEARANCE"
    EMERGENCY_GREEN = "EMERGENCY_GREEN"

class TrafficSignal:

    def __init__(self, junction_id):
        self.junction_id = junction_id
        self.state = SignalState.NORMAL

    def request_green(self):
        if self.state != SignalState.NORMAL:
            return {
                "success": False,
                "message": "Signal is already handling another request"
            }

        self.state = SignalState.GREEN_REQUESTED

        return {
            "success": True,
            "message": "Green request accepted",
            "junction_id": self.junction_id,
            "state": self.state.value
        }

    def start_clearance(self):
        if self.state != SignalState.GREEN_REQUESTED:
            return {
                "success": False,
                "message": "Clearance cannot start"
            }

        self.state = SignalState.CLEARANCE

        return {
            "success": True,
            "junction_id": self.junction_id,
            "state": self.state.value
        }

    def activate_emergency_green(self):
        if self.state != SignalState.CLEARANCE:
            return {
                "success": False,
                "message": "Emergency green cannot be activated"
            }

        self.state = SignalState.EMERGENCY_GREEN

        return {
            "success": True,
            "junction_id": self.junction_id,
            "state": self.state.value
        }

    def release(self):

        self.state = SignalState.NORMAL

        return {
            "success": True,
            "junction_id": self.junction_id,
            "state": self.state.value
        }

    def get_status(self):

        return {
            "junction_id": self.junction_id,
            "state": self.state.value
        }

if __name__ == "__main__":

    signal = TrafficSignal("J001")

    print(signal.get_status())

    print(signal.request_green())

    print(signal.start_clearance())

    print(signal.activate_emergency_green())

    print(signal.release())

    print(signal.get_status())