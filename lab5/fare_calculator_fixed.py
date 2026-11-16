
"""Fare calculation, fare-card management, and secure stop parsing."""

import hashlib
import math
from pathlib import Path

import paramiko
from defusedxml import sax
from xml.sax.handler import ContentHandler

DISTANCE_SLABS = [(2, 10), (5, 20), (12, 30), (21, 40), (32, 50)]
MAX_FARE = 60
DAILY_CAP = 150
OFF_PEAK_DISCOUNT = 0.10
CONCESSIONS = {"student": 0.25, "senior": 0.50}
cards = {}


def base_of(km):
    """Return the base fare for a given distance."""
    return fare_for_distance(km)


def fare_for_distance(km):
    """Calculate the base fare using distance slabs."""
    for limit, fare in DISTANCE_SLABS:
        if km < limit:
            return fare
    return MAX_FARE


def is_peak(time_hhmm):
    """Check whether a time falls within peak hours."""
    hour = int(time_hhmm.split(":")[0])
    return (8 <= hour <= 10) or (17 <= hour <= 20)


def journey_fare(km, time_hhmm, categories):
    """Calculate a journey fare after applicable discounts."""
    fare = base_of(km)

    if not is_peak(time_hhmm):
        fare *= 1 - OFF_PEAK_DISCOUNT

    for category in categories:
        if category not in CONCESSIONS:
            raise ValueError(f"Unknown concession category: {category}")
        fare *= 1 - CONCESSIONS[category]

    return round(fare, 2)


def daily_total(journeys):
    """Calculate the daily fare total subject to the daily cap."""
    fares = [
        journey_fare(km, time, categories)
        for km, time, categories in journeys
    ]
    return min(sum(fares), DAILY_CAP)


def issue_card(card_id, balance=0):
    """Create a fare card with an initial balance."""
    if balance < 0:
        raise ValueError("Initial balance cannot be negative.")
    cards[card_id] = {"balance": balance, "trips": []}


def tap_out(card_id, km, time_hhmm, categories=None):
    """Deduct a journey fare and record the trip."""
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")

    if categories is None:
        categories = []

    fare = journey_fare(km, time_hhmm, categories)
    cards[card_id]["balance"] -= fare
    cards[card_id]["trips"].append((km, time_hhmm, fare))
    return cards[card_id]["balance"]


def top_up(card_id, amount):
    """Add a positive amount to a fare card."""
    if card_id not in cards:
        raise KeyError(f"Unknown card: {card_id}")
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Top-up amount must be positive and finite.")

    cards[card_id]["balance"] = round(
        cards[card_id]["balance"] + amount, 2
    )
    return cards[card_id]["balance"]


def cheapest_route(routes):
    """Return the route with the lowest base fare."""
    if not routes:
        raise ValueError("At least one route is required.")
    return min(routes, key=base_of)


def ticket_checksum(ticket_text):
    """Return the SHA-256 checksum of ticket text."""
    return hashlib.sha256(ticket_text.encode("utf-8")).hexdigest()


class StopHandler(ContentHandler):
    """Collect stop names while parsing XML."""

    def __init__(self):
        """Initialize the stop collection."""
        super().__init__()
        self.stops = []

    def startElement(self, name, attrs):
        """Record the name of each stop element."""
        if name == "stop" and "name" in attrs:
            self.stops.append(attrs["name"])

    def endElement(self, name):
        """Handle the end of an XML element."""
        pass


def load_stops(xml_text):
    """Parse XML safely and return the stop names."""
    stop_handler = StopHandler()
    sax.parseString(xml_text.encode("utf-8"), stop_handler)
    return stop_handler.stops


def push_fares_to_gate(gate_host, fare_file):
    """Transfer a fare file to a trusted remote host using SFTP."""
    local_path = Path(fare_file)
    if not local_path.is_file():
        raise FileNotFoundError(f"Fare file not found: {fare_file}")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.RejectPolicy())

    try:
        client.connect(gate_host, username="depot", timeout=10)
        with client.open_sftp() as sftp:
            remote_path = f"fare_upload_{local_path.name}"
            sftp.put(str(local_path), remote_path)
    finally:
        client.close()


def main():
    """Run fare calculator examples."""
    print("Fare for exactly 2 km:", fare_for_distance(2))
    print("Fare for exactly 32 km:", fare_for_distance(32))
    print("Is 20:45 peak?", is_peak("20:45"))

    print(
        "Student + senior card, 10 km off-peak:",
        journey_fare(10, "14:00", ["student", "senior"]),
    )

    day = [
        (30, "08:15", []),
        (30, "18:30", []),
        (40, "21:00", []),
        (35, "22:30", []),
    ]
    print("Daily total (cap 150):", daily_total(day))

    issue_card("C1", 25)
    print(
        "Balance after a 30 km trip with Rs.25:",
        tap_out("C1", 30, "09:00"),
    )

    issue_card("C2", 0)
    print(
        "Top up 0.1 then 0.2:",
        top_up("C2", 0.1),
        top_up("C2", 0.2),
    )

    print(
        "Cheapest of routes 12 km / 5 km / 21 km:",
        cheapest_route([12, 5, 21]),
    )
    print("Ticket checksum:", ticket_checksum("C1|30km|09:00"))
    print(
        "Stops:",
        load_stops(
            "<line><stop name='Central'/>"
            "<stop name='Market'/></line>"
        ),
    )


if __name__ == "__main__":
    main()
