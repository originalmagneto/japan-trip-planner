"""Google Flights URL encoder and search matrix generator."""
import base64
import urllib.parse
from datetime import date, timedelta

from .schemas import FlightSearchSpace


def varint(value: int) -> bytes:
    """Encode varint for protobuf."""
    out = []
    while value > 0x7F:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    out.append(value & 0x7F)
    return bytes(out)


def tag(field: int, wire_type: int) -> bytes:
    """Encode protobuf field tag."""
    return varint((field << 3) | wire_type)


def string_field(field: int, value: str) -> bytes:
    """Encode protobuf string field."""
    raw = value.encode("utf-8")
    return tag(field, 2) + varint(len(raw)) + raw


def message_field(field: int, payload: bytes) -> bytes:
    """Encode protobuf message field."""
    return tag(field, 2) + varint(len(payload)) + payload


def airport(code: str) -> bytes:
    """Encode airport code."""
    return string_field(2, code)


def leg(date_str: str, origin: str, destination: str) -> bytes:
    """Encode flight leg: date, origin, destination."""
    return (
        string_field(2, date_str)
        + message_field(13, airport(origin))
        + message_field(14, airport(destination))
    )


def google_flights_tfs(
    origin: str,
    destination: str,
    outbound: str,
    inbound: str,
    adults: int = 5,
    cabin: str = "economy",
) -> str:
    """Build Google Flights tfs protobuf parameter."""
    payload = (
        message_field(3, leg(outbound, origin, destination))
        + message_field(3, leg(inbound, destination, origin))
        # Passenger.ADULT enum, repeated once per adult
        + b"".join(tag(8, 0) + varint(1) for _ in range(adults))
        # Seat.ECONOMY (1) and Trip.ROUND_TRIP (1)
        + tag(9, 0) + varint(1)
        + tag(19, 0) + varint(1)
    )
    return base64.b64encode(payload).decode("ascii")


def build_google_flights_url(
    origin: str,
    destination: str,
    outbound: date,
    inbound: date,
    adults: int = 5,
    cabin: str = "economy",
    currency: str = "EUR",
    market: str = "SK",
) -> str:
    """Build complete Google Flights search URL."""
    tfs = google_flights_tfs(
        origin,
        destination,
        outbound.isoformat(),
        inbound.isoformat(),
        adults,
        cabin,
    )
    query = urllib.parse.urlencode({
        "tfs": tfs,
        "hl": "en",
        "gl": market,
        "curr": currency,
    })
    return f"https://www.google.com/travel/flights/search?{query}"


def generate_search_matrix(space: FlightSearchSpace) -> list[dict]:
    """Generate all origin × dest × date combinations within search space.
    
    Returns list of dicts with: origin, destination, outbound_date, return_date, url
    """
    searches = []
    out_start, out_end = space.outbound_dates()
    ret_start, ret_end = space.return_dates()
    
    # Generate date ranges
    out_dates = []
    current = out_start
    while current <= out_end:
        out_dates.append(current)
        current += timedelta(days=1)
    
    ret_dates = []
    current = ret_start
    while current <= ret_end:
        ret_dates.append(current)
        current += timedelta(days=1)
    
    # Limit to reasonable grid (every 2 days if window > 7 days)
    if len(out_dates) > 7:
        out_dates = out_dates[::2]
    if len(ret_dates) > 7:
        ret_dates = ret_dates[::2]
    
    for origin in space.origins:
        for dest in space.destinations:
            for out_date in out_dates:
                for ret_date in ret_dates:
                    nights = (ret_date - out_date).days
                    
                    # Skip unreasonably short trips
                    if nights < 10:
                        continue
                    
                    # Skip unreasonably long trips
                    if nights > 25:
                        continue
                    
                    searches.append({
                        "origin": origin,
                        "destination": dest,
                        "outbound_date": out_date.isoformat(),
                        "return_date": ret_date.isoformat(),
                        "nights": nights,
                        "url": build_google_flights_url(
                            origin,
                            dest,
                            out_date,
                            ret_date,
                            space.travellers,
                            space.cabin,
                            space.currency,
                            space.market,
                        ),
                    })
    
    return searches
