#!/usr/bin/env python3
"""Build the data-driven Japan trip configurator."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/trip_data.json"
ACCOMMODATION_DATA = ROOT / "data/accommodation_options.json"
TEMPLATE = ROOT / "src/configurator_template.html"
OUT = ROOT / "outputs/japan-configurator.html"
MD = ROOT / "outputs/japan-configurator.md"


def load_data() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if ACCOMMODATION_DATA.exists():
        lodging = json.loads(ACCOMMODATION_DATA.read_text(encoding="utf-8"))
        data["accommodations"] = lodging.get("options", [])
        data["accommodation_blockers"] = lodging.get("blocked_sources", [])
        data["accommodation_observed_at"] = lodging.get("observed_at")
    return data


def money(value: float | int | None) -> str:
    if value is None:
        return "neoverené"
    return f"{value:,.2f} €".replace(",", " ").replace(".00", "")


def markdown(data: dict) -> str:
    trip = data["trip"]
    travellers = trip["travellers"]
    lines = [
        "# Japan Trip Configurator",
        "",
        f"Pracovné termíny: {trip['working_dates']['outbound']} – {trip['working_dates']['return']}",
        f"Skupina: {travellers} dospelých, {trip['rooms']} izby, príručná batožina.",
        "",
        "## Letecké možnosti",
        "",
        "| ID | Variant | Dátumy | Prestupy | Cena spolu | Cena/os. | Stav | Link |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    for flight in data["flight_options"]:
        total = flight.get("price_total_eur")
        per_person = total / travellers if total is not None else None
        status = "overená ponuka" if flight.get("verified") else "lead – checkout overiť"
        lines.append(
            f"| {flight['id']} | {flight['label']} | {flight['departure_date']} – {flight['return_date']} | "
            f"{flight.get('stops', 'neuvedené')} | {money(total)} | {money(per_person)} | {status} | "
            f"[otvoriť zdroj]({flight['search_url']}) |"
        )
        if flight.get("segments"):
            lines.extend(f"  - {segment}" for segment in flight["segments"])
    lines += ["", "## Lokácie a program", ""]
    for location in data["locations"]:
        lines += [
            f"### {location['name']}",
            "",
            f"Noci: {location['nights']} · Základňa: {location['stay_area']} · Pešia dostupnosť: {location['walkability']}",
            "",
            f"Historický klimatický kontext: {location['weather']['temperature_c']} °C; "
            f"{location['weather']['rain']} — {location['weather']['note']} "
            f"([zdroj]({location['weather']['source']}))",
            "",
            "| POI | Typ | Čas | Cena | Link |",
            "|---|---|---:|---:|---|",
        ]
        for poi in location["pois"]:
            lines.append(
                f"| {poi['name']} | {poi['type']} | {poi['time_h']} h | {poi['cost_eur']} € | "
                f"[mapa]({poi['map']}) · [info]({poi['link']}) |"
            )
        lines += ["", "Voliteľné aktivity:"]
        lines.extend(
            f"- {activity['name']} — {activity['hours']} h, cca {activity['cost_eur']} €/os. "
            f"([info]({activity['link']}))"
            for activity in location["activities"]
        )
        lines.append("")
    lines += [
        "## Ubytovanie",
        "",
        "| Mesto | Ubytovanie | Dátumy | Konfigurácia | Celkom | Stav | Link |",
        "|---|---|---|---|---:|---|---|",
    ]
    for stay in data.get("accommodations", []):
        status = "overené" if stay["verified"] else "lead – overiť detail"
        lines.append(
            f"| {stay['city']} | {stay['name']} | {stay['dates']} | {stay['configuration']} | "
            f"{money(stay['total_eur'])} | {status} | [otvoriť]({stay['url']}) |"
        )
    lines += [
        "",
        "## Presuny",
        "",
        "| Odkiaľ | Kam | Spôsob | Čas | Cena | Nákup |",
        "|---|---|---|---|---:|---|",
    ]
    for transfer in data["transfers"]:
        lines.append(
            f"| {transfer['from']} | {transfer['to']} | {transfer['mode']} | {transfer['duration']} | "
            f"{transfer['cost_eur']} € | [kúpiť/info]({transfer['buy']}) |"
        )
    lines += [
        "",
        "## Poznámka k cenám",
        "",
        "HTML umožňuje vyberať medzi uloženými ponukami, ale sám pri otvorení nehľadá nové live ceny. "
        "Neoverené leady a ponuky bez úplných tarifných podmienok treba overiť pri checkout-e pre všetkých cestujúcich.",
    ]
    return "\n".join(lines) + "\n"


def build() -> str:
    payload = json.dumps(load_data(), ensure_ascii=False).replace("</script>", "<\\/script>")
    return TEMPLATE.read_text(encoding="utf-8").replace("__TRIP_DATA__", payload)


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    md_text = markdown(load_data())
    MD.write_text(md_text, encoding="utf-8")
    try:
        try:
            from src.build_pdf import build_pdf_bytes
        except ModuleNotFoundError:
            from build_pdf import build_pdf_bytes
        (ROOT / "outputs/japan-configurator.pdf").write_bytes(build_pdf_bytes(md_text))
    except ModuleNotFoundError:
        pass
    print(OUT)
    print(MD)
