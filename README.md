# Japan Trip Planner — Majo Čuprík

Komplexný, reprodukovateľný plánovač cesty do Japonska pre 5 osôb.

## Pracovné zadanie

- termín: posledný septembrový týždeň 2026, návrat približne 10.–14. októbra
- skupina: 5 osôb, 2 izby, príručná batožina
- odlety: Viedeň (VIE) a Budapešť (BUD)
- cieľ: najnižšia rozumná cena; dlhé prestupy sú prijateľné
- rozpočet: približne 1 500 € na osobu, mierne prekročenie možné
- priorita: história a tradičné Japonsko
- Okinawa: iba voliteľná alternatíva pri lacnom lete

## Štruktúra

- `docs/itinerary.md` — hlavný podrobný itinerár
- `docs/flight-options.md` — letecké varianty a odkazy na vyhľadávanie
- `docs/budget.md` — rozpočet a scenáre
- `docs/transport.md` — vlaky, rezervácie a JR Pass
- `data/raw/flight-observations.csv` — ručne alebo skriptom uložené cenové pozorovania
- `data/raw/accommodation.csv` — kandidáti ubytovania
- `src/flight_tracker.py` — validácia a vyhodnotenie pozorovaní
- `src/build_report.py` — vytvorenie markdown reportu
- `tests/` — testy dátových nástrojov
- `outputs/` — generované reporty

## Dôležité

Tento repozitár zámerne neobsahuje vymyslené aktuálne ceny. Konkrétne ceny leteniek sa ukladajú ako pozorovania s časom, URL, tarifnými podmienkami a počtom cestujúcich. Pri nákupe treba cenu znovu overiť priamo u predajcu.

## Spustenie

```bash
cd /opt/data/japan-trip-planner
python3 -m unittest discover -s tests -v
python3 src/flight_tracker.py summary
python3 src/build_report.py
```

## Sledovanie ceny

1. Otvor odkaz v `docs/flight-options.md`.
2. Skontroluj cenu pre 5 dospelých a iba príručnú batožinu.
3. Pridaj riadok do `data/raw/flight-observations.csv`.
4. Spusť `python3 src/flight_tracker.py summary`.
5. Ak cena klesne pod cieľ, zapíš ju do `data/raw/alerts.csv` alebo vytvor upozornenie v cron-e.

Automatické spoľahlivé rezervovanie ani nákup sa nevykonáva.
