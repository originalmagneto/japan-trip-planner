"""Pydantic schemas for flight search space and observations."""
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class FlightSearchSpace(BaseModel):
    """Flight search parameters for automated research."""
    
    origins: list[str] = Field(..., description="IATA airport codes: VIE, BUD")
    destinations: list[str] = Field(..., description="City codes: TYO, OSA")
    outbound_window: tuple[str, str] = Field(..., description="ISO date range for departure")
    return_window: tuple[str, str] = Field(..., description="ISO date range for return")
    travellers: int = Field(ge=1, le=9, description="Number of adults")
    cabin: Literal["economy", "premium_economy", "business", "first"] = "economy"
    carry_on_only: bool = True
    max_stops: int | None = None
    currency: str = "EUR"
    market: str = "SK"
    
    def outbound_dates(self) -> tuple[date, date]:
        """Parse outbound window as date objects."""
        return (
            date.fromisoformat(self.outbound_window[0]),
            date.fromisoformat(self.outbound_window[1]),
        )
    
    def return_dates(self) -> tuple[date, date]:
        """Parse return window as date objects."""
        return (
            date.fromisoformat(self.return_window[0]),
            date.fromisoformat(self.return_window[1]),
        )


class FlightSegment(BaseModel):
    """Individual flight leg."""
    
    origin: str
    destination: str
    departure_time: str | None = None
    arrival_time: str | None = None
    airline: str | None = None
    flight_number: str | None = None
    duration: str | None = None


class FlightObservation(BaseModel):
    """Flight price observation from live research."""
    
    search_id: str = Field(..., description="Unique identifier: origin-dest-out-ret")
    origin: str
    destination: str
    outbound_date: str  # ISO date
    return_date: str  # ISO date
    price_total_eur: float | None = Field(None, description="Total for all travellers")
    price_per_person_eur: float | None = None
    travellers: int
    verified: bool = Field(False, description="Checkout-verified price")
    segments: list[FlightSegment] = Field(default_factory=list)
    baggage_note: str = ""
    search_url: str
    observed_at: str  # ISO datetime
    provider: str = Field(..., description="google_flights, kayak, skyscanner, etc.")
    
    def nights(self) -> int:
        """Calculate trip duration in nights."""
        out = date.fromisoformat(self.outbound_date)
        ret = date.fromisoformat(self.return_date)
        return (ret - out).days
