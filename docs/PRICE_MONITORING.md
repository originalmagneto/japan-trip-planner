# Flight Price Monitoring

Automatické sledovanie zmien cien vybraných letov s alertami pri významných zmenách.

## Ako to funguje

1. **Watch list** (`data/price_watch.json`) — zoznam letov, ktoré chceš sledovať
2. **Cron job** (`scripts/check_prices.py`) — beží periodicky (napr. každých 6 hodín)
3. **Price history** (`data/price_history.jsonl`) — append-only log všetkých pozorovaní
4. **Alerts** — Hermes ti pošle Telegram notifikáciu pri zmene >5% alebo ak cena klesne pod target

## Nastavenie watch listu

### Manuálne (pre testing)

```bash
cp data/price_watch.example.json data/price_watch.json
# Edituj price_watch.json — pridaj svoje search URL a target ceny
```

### Programovo

```python
from src.monitoring.price_watch import add_flight_to_watch

add_flight_to_watch(
    flight_id="f1",
    search_url="https://www.google.com/travel/flights/search?tfs=...",
    target_price=5000  # Alert ak cena klesne pod 5000 EUR
)
```

## Spustenie cron jobu cez Hermes

```bash
# Manuálny test
python scripts/check_prices.py

# Vytvor Hermes cron job (denne o 9:00 a 18:00)
hermes cronjob create \
  --name "Flight Price Monitor" \
  --schedule "0 9,18 * * *" \
  --script scripts/check_prices.py \
  --no-agent

# Zoznam jobov
hermes cronjob list

# Spusti teraz (testing)
hermes cronjob run <job_id>
```

## Formát watch listu

```json
[
  {
    "flight_id": "f1",
    "search_url": "https://www.google.com/travel/flights/...",
    "target_price_eur": 5000,
    "last_price_eur": 5500,
    "last_checked": "2026-08-16T08:00:00Z"
  }
]
```

- `flight_id` — ID z `trip_data.json`
- `search_url` — Google Flights search URL (tfs parameter)
- `target_price_eur` — Alert ak cena klesne pod túto hodnotu (optional)
- `last_price_eur` — Posledná pozorovaná cena (auto-updated)
- `last_checked` — Timestamp poslednej kontroly (auto-updated)

## Alert typy

### Price Change Alert (>5% zmena)

```
📉 f1: 5500€ → 5200€ (-5.5%)
```

### Target Hit Alert

```
🎯 f14 — Target price hit!
   Current: 4400€ ≤ Target: 4500€
```

## Price History

Každá kontrola sa zapíše do `data/price_history.jsonl`:

```jsonl
{"flight_id": "f1", "price_eur": 5500, "observed_at": "2026-08-16T08:00:00Z", "search_url": "..."}
{"flight_id": "f1", "price_eur": 5200, "observed_at": "2026-08-16T14:00:00Z", "search_url": "..."}
```

Tento log môžeš analyzovať:

```bash
# Graf cien v čase
cat data/price_history.jsonl | jq -r '[.observed_at, .price_eur] | @csv'

# Priemerná cena za posledný týždeň
cat data/price_history.jsonl | jq -s 'map(.price_eur) | add / length'
```

## Implementačný status

- ✅ Watch list management (add/remove/load)
- ✅ Price history logging (JSONL append)
- ✅ Alert detection (price change >5%, target hit)
- ✅ Hermes cron job wrapper
- ✅ 4 unit testy
- ⏸️ **Actual scraping** — placeholder, vyžaduje browser_exec integration

## Ďalšie kroky

1. **Integrovať browser_exec** do `check_flight_price()` — skutočné scrapovanie Google Flights
2. **Rate limiting** — max 10 URL / hodinu (Google Flights anti-bot)
3. **Retry logic** — 3 pokusy pri CAPTCHA/blocking
4. **Rich alerts** — priložiť screenshot, link na booking
5. **Historical charts** — vizualizácia price trendu v Telegram

## Troubleshooting

### "No flights in watch list"

```bash
# Pridaj prvý let
python -c "from src.monitoring.price_watch import add_flight_to_watch; \
  add_flight_to_watch('f1', 'https://...', 5000)"
```

### "Price unavailable (blocked or error)"

Google Flights blokuje scraping. Riešenia:
- Znížiť frekvenciu (1x denne namiesto 4x)
- Použiť rotating proxies
- Použiť oficiálne API (napr. Amadeus, Kiwi.com)

### Cron job nebeží

```bash
# Over že je vytvorený
hermes cronjob list

# Over logy
hermes cronjob logs <job_id>
```
