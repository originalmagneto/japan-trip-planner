# Data entry rules

## `flight-observations.csv`

- `price_eur` is the total checkout price for all 5 travellers, not a teaser fare.
- `passengers` must be `5` for a comparable offer.
- `carry_on_included` must be `yes` only when the fare conditions explicitly include the required cabin baggage.
- `booking_url` must point to the booking result or the exact search query.
- Never enter an estimated or remembered price as a live observation.

## `accommodation.csv`

- `total_eur` is the total for all guests and all rooms for the stated stay.
- `rooms` must be `2` for the base plan.
- Include the exact room configuration in `notes`.
- Record cancellation conditions and taxes in `notes`.
