from app.signal import TrafficSignal
signals = {}


def get_signal(junction_id):
    if junction_id not in signals:
        signals[junction_id] = TrafficSignal(junction_id)

    return signals[junction_id]