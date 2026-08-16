#!/usr/bin/env python3
"""Build the Japan Trip Optimizer with impeccable.style design."""
import json
from pathlib import Path

from jinja2 import Template

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/trip_data.json"
ACCOMMODATION_DATA = ROOT / "data/accommodation_options.json"
CSS_FILE = ROOT / "src/templates/impeccable.css"
TEMPLATE_FILE = ROOT / "src/templates/optimizer.html"
OUT = ROOT / "outputs/japan-optimizer.html"


def load_data() -> dict:
    """Load trip data and accommodation options."""
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if ACCOMMODATION_DATA.exists():
        lodging = json.loads(ACCOMMODATION_DATA.read_text(encoding="utf-8"))
        data["accommodations"] = lodging.get("options", [])
    return data


def build_optimizer() -> str:
    """Build the optimizer HTML with embedded CSS and data."""
    data = load_data()
    css = CSS_FILE.read_text(encoding="utf-8")
    template = Template(TEMPLATE_FILE.read_text(encoding="utf-8"))
    
    # Calculate nights for each flight
    from datetime import datetime
    for flight in data["flight_options"]:
        out = datetime.fromisoformat(flight["departure_date"])
        ret = datetime.fromisoformat(flight["return_date"])
        flight["nights"] = (ret - out).days
    
    # Generate AI recommendations
    from src.ai import add_recommendations_to_data
    data = add_recommendations_to_data(data)
    
    html = template.render(
        css=css,
        flights=data["flight_options"],
        recommendations=data.get("ai_recommendations", {}),
        trip_data_json=json.dumps(data, ensure_ascii=False).replace("</script>", "<\\/script>"),
    )
    
    return html


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build_optimizer()
    OUT.write_text(html, encoding="utf-8")
    print(OUT)
