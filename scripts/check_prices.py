#!/usr/bin/env python3
"""Hermes cron job for flight price monitoring.

This script is called by Hermes cronjob scheduler.
It checks watched flights and returns alerts for delivery.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.monitoring.price_watch import run_price_check


def main():
    """Run price check and format output for Hermes delivery."""
    alerts = run_price_check()
    
    if not alerts:
        # Silent when no alerts (Hermes won't deliver anything)
        return
    
    # Format alerts for Telegram delivery
    print("\n🛫 **Flight Price Alerts**\n")
    
    for alert in alerts:
        if alert["type"] == "price_change":
            emoji = "📉" if alert["direction"] == "down" else "📈"
            print(f"{emoji} **{alert['flight_id']}**")
            print(f"   {alert['old_price']}€ → **{alert['new_price']}€** ({alert['change_pct']:+.1f}%)\n")
        
        elif alert["type"] == "target_hit":
            print(f"🎯 **{alert['flight_id']}** — Target price hit!")
            print(f"   Current: **{alert['current_price']}€** ≤ Target: {alert['target_price']}€\n")
    
    print("\n_Checked: " + str(len(alerts)) + " flight(s) with price changes_")


if __name__ == "__main__":
    main()
