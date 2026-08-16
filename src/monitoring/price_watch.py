"""Price monitoring cron job for flight tracking.

Monitors selected flights and alerts when prices change significantly.
"""
import json
from datetime import datetime, timezone
from pathlib import Path


WATCH_FILE = Path(__file__).resolve().parents[2] / "data/price_watch.json"
HISTORY_FILE = Path(__file__).resolve().parents[2] / "data/price_history.jsonl"


def load_watch_list() -> list[dict]:
    """Load list of flights to monitor.
    
    Format:
    {
        "flight_id": "f1",
        "target_price_eur": 5000,  # Alert if below this
        "last_price_eur": 5500,
        "last_checked": "2026-08-16T10:00:00Z",
        "search_url": "https://..."
    }
    """
    if not WATCH_FILE.exists():
        return []
    
    return json.loads(WATCH_FILE.read_text())


def save_watch_list(watches: list[dict]):
    """Save updated watch list."""
    WATCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATCH_FILE.write_text(json.dumps(watches, indent=2, ensure_ascii=False))


def record_price_history(flight_id: str, price: float | None, url: str):
    """Append price observation to history log."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    entry = {
        "flight_id": flight_id,
        "price_eur": price,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "search_url": url,
    }
    
    with HISTORY_FILE.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def check_flight_price(watch: dict) -> dict | None:
    """Check current price for a watched flight.
    
    Returns alert dict if price changed significantly, else None.
    """
    # TODO: Implement actual scraping via browser_exec
    # For now, this is a placeholder that would be called by Hermes Agent
    
    print(f"⏳ Checking {watch['flight_id']}...")
    
    # Placeholder: would fetch from watch['search_url']
    # current_price = scrape_google_flights(watch['search_url'])
    current_price = None
    
    if current_price is None:
        print(f"   ⚠️  Price unavailable (blocked or error)")
        return None
    
    # Record in history
    record_price_history(watch["flight_id"], current_price, watch["search_url"])
    
    # Check for significant change
    last_price = watch.get("last_price_eur")
    target_price = watch.get("target_price_eur")
    
    alerts = []
    
    if last_price and abs(current_price - last_price) / last_price > 0.05:
        # Price changed by more than 5%
        change_pct = ((current_price - last_price) / last_price) * 100
        alerts.append({
            "type": "price_change",
            "flight_id": watch["flight_id"],
            "old_price": last_price,
            "new_price": current_price,
            "change_pct": round(change_pct, 1),
            "direction": "up" if current_price > last_price else "down",
        })
    
    if target_price and current_price <= target_price:
        # Price hit target
        alerts.append({
            "type": "target_hit",
            "flight_id": watch["flight_id"],
            "target_price": target_price,
            "current_price": current_price,
        })
    
    # Update watch entry
    watch["last_price_eur"] = current_price
    watch["last_checked"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    return alerts[0] if alerts else None


def run_price_check():
    """Main price check loop — called by cron job."""
    watches = load_watch_list()
    
    if not watches:
        print("📭 No flights in watch list")
        return
    
    print(f"🔍 Checking {len(watches)} flights...")
    
    alerts = []
    for watch in watches:
        alert = check_flight_price(watch)
        if alert:
            alerts.append(alert)
    
    # Save updated watch list
    save_watch_list(watches)
    
    # Format alerts for user
    if alerts:
        print(f"\n🚨 {len(alerts)} price alerts:\n")
        for alert in alerts:
            if alert["type"] == "price_change":
                direction = "📉" if alert["direction"] == "down" else "📈"
                print(f"{direction} {alert['flight_id']}: {alert['old_price']}€ → {alert['new_price']}€ ({alert['change_pct']:+.1f}%)")
            elif alert["type"] == "target_hit":
                print(f"🎯 {alert['flight_id']}: Hit target price! {alert['current_price']}€ ≤ {alert['target_price']}€")
        
        return alerts  # Hermes will deliver this as notification
    else:
        print("✓ All prices stable")
        return None


def add_flight_to_watch(flight_id: str, search_url: str, target_price: float | None = None):
    """Add a flight to the watch list."""
    watches = load_watch_list()
    
    # Check if already watching
    if any(w["flight_id"] == flight_id for w in watches):
        print(f"⚠️  {flight_id} is already in watch list")
        return
    
    watches.append({
        "flight_id": flight_id,
        "search_url": search_url,
        "target_price_eur": target_price,
        "last_price_eur": None,
        "last_checked": None,
    })
    
    save_watch_list(watches)
    print(f"✓ Added {flight_id} to watch list")


def remove_flight_from_watch(flight_id: str):
    """Remove a flight from the watch list."""
    watches = load_watch_list()
    watches = [w for w in watches if w["flight_id"] != flight_id]
    save_watch_list(watches)
    print(f"✓ Removed {flight_id} from watch list")


if __name__ == "__main__":
    # For testing
    run_price_check()
