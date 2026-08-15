#!/usr/bin/env python3
"""Build the interactive, self-contained Japan trip presentation."""
from __future__ import annotations

import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/japan-trip-interactive.html"

DAYS = [
    (1, "Odlet", "VIE/BUD → Japonsko", "Let", "https://www.google.com/maps/search/Haneda+Airport"),
    (2, "Prílet do Tokia", "Asakusa, Senso-ji", "Chôdza + metro", "https://www.google.com/maps/search/Asakusa"),
    (3, "Tokio", "Ueno, Tokyo National Museum, Ameyoko", "Metro", "https://www.google.com/maps/dir/Asakusa/Ueno+Park/Tokyo+National+Museum"),
    (4, "Tokio", "Meiji Jingu, cisárske záhrady, Nihonbashi", "Metro", "https://www.google.com/maps/dir/Meiji+Jingu/Tokyo+Imperial+Palace/Nihonbashi"),
    (5, "Výlet", "Nikko alebo Kamakura", "Denný vlak", "https://www.google.com/maps/search/Nikko"),
    (6, "Tokio → Kanazawa", "Hokuriku Shinkansen, Higashi Chaya", "Shinkansen", "https://www.google.com/maps/dir/Tokyo+Station/Kanazawa+Station"),
    (7, "Kanazawa", "Kenroku-en, hrad, samurajská štvrť", "Chôdza + bus", "https://www.google.com/maps/dir/Kenrokuen/Kanazawa+Castle/Nagamachi+Samurai+District"),
    (8, "Kanazawa → Kjóto", "Gion, Yasaka Shrine, Pontocho", "Vlak", "https://www.google.com/maps/dir/Kanazawa+Station/Kyoto+Station"),
    (9, "Kjóto", "Kiyomizu-dera, Higashiyama, Fushimi Inari", "Bus + vlak", "https://www.google.com/maps/dir/Kiyomizu-dera/Fushimi+Inari+Taisha"),
    (10, "Kjóto", "Arashiyama, Tenryu-ji, Togetsukyo", "JR + chôdza", "https://www.google.com/maps/dir/Kyoto+Station/Arashiyama"),
    (11, "Kjóto", "Kinkaku-ji, Ryoan-ji, Ninna-ji", "Bus / taxi", "https://www.google.com/maps/dir/Kinkaku-ji/Ryoan-ji/Ninna-ji"),
    (12, "Výlet", "Nara: Todaiji, Kasuga Taisha, Naramachi", "JR/Kintetsu", "https://www.google.com/maps/dir/Nara+Station/Todaiji/Kasuga+Taisha"),
    (13, "Kjóto", "Nishiki Market alebo voľný deň", "Miestna doprava", "https://www.google.com/maps/search/Kyoto"),
    (14, "Kjóto → Osaka", "Osaka Castle, Dotonbori", "Miestny vlak", "https://www.google.com/maps/dir/Kyoto+Station/Osaka+Castle/Dotonbori"),
    (15, "Výlet", "Himeji Castle", "JR", "https://www.google.com/maps/dir/Osaka+Station/Himeji+Castle"),
    (16, "Osaka", "Shitennoji, Shinsekai, Kuromon Market", "Metro", "https://www.google.com/maps/dir/Shitennoji/Shinsekai/Kuromon+Market"),
    (17, "Rezerva", "Osaka alebo presun do Tokia podľa letu", "Vlak", "https://www.google.com/maps/search/Osaka"),
    (18, "Návrat", "Hotel → letisko", "Let", "https://www.google.com/maps/search/Kansai+International+Airport"),
]

IMAGES = [
    ("Tokio", "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=1200&q=85", "Neónové Tokio a Asakusa"),
    ("Kjóto", "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=85", "Chrámy, záhrady a tradičné štvrte"),
    ("Nara", "https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=1200&q=85", "Nara a historické Japonsko"),
    ("Osaka", "https://images.unsplash.com/photo-1590559899731-a382839e5549?auto=format&fit=crop&w=1200&q=85", "Osaka a večerné ulice"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def flight_cards(rows: list[dict[str, str]]) -> str:
    if not rows:
        return '<div class="empty">Zatiaľ bez overených cenových pozorovaní. <a href="../docs/flight-options.md">Otvoriť vyhľadávacie odkazy →</a></div>'
    cards = []
    for row in sorted(rows, key=lambda r: float(r.get("price_eur", "999999") or "999999")):
        cards.append(f'''<article class="flight-card" data-price="{html.escape(row.get('price_eur',''))}">
          <div class="eyebrow">{html.escape(row.get('origin',''))} → {html.escape(row.get('destination',''))}</div>
          <h3>{html.escape(row.get('airlines','Neznáma aerolinka'))}</h3>
          <strong class="price">{html.escape(row.get('price_eur','?'))} € <small>spolu / 5 osôb</small></strong>
          <p>{html.escape(row.get('departure_date',''))} → {html.escape(row.get('return_date',''))} · {html.escape(row.get('stops','?'))} prestup(y)</p>
          <a class="button small" href="{html.escape(row.get('booking_url','#'))}" target="_blank" rel="noopener">Otvoriť ponuku ↗</a>
        </article>''')
    return "\n".join(cards)


def day_rows() -> str:
    return "\n".join(f'''<button class="day-row" data-day="{day}">
      <span class="day-number">{day:02}</span><span><b>{html.escape(title)}</b><em>{html.escape(program)}</em></span><span class="day-route">{html.escape(route)}</span><a href="{url}" target="_blank" rel="noopener">Mapa ↗</a>
    </button>''' for day, title, program, route, url in DAYS)


def build() -> str:
    flights = read_csv(ROOT / "data/raw/flight-observations.csv")
    payload = json.dumps({"days": len(DAYS), "flights": len(flights)}, ensure_ascii=False)
    image_cards = "\n".join(f'''<figure class="image-card"><img loading="lazy" src="{url}" alt="{html.escape(alt)}"><figcaption><b>{html.escape(city)}</b><span>{html.escape(alt)}</span></figcaption></figure>''' for city, url, alt in IMAGES)
    return f'''<!doctype html>
<html lang="sk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101820"><title>Japonsko 2026 · Majo & priatelia</title>
<style>
:root{{--ink:#101820;--muted:#62727d;--paper:#f6f3ed;--card:#fff;--red:#c83b4b;--gold:#e6b35a;--line:#e4ddd2;--shadow:0 18px 50px #1b283115}}*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif;line-height:1.5}}a{{color:inherit}}.wrap{{max-width:1180px;margin:auto;padding:0 24px}}.hero{{min-height:640px;color:#fff;display:flex;align-items:flex-end;background:linear-gradient(180deg,#0b182000 10%,#0b1820e8 92%),url('https://images.unsplash.com/photo-1524413840807-0c3cb6fa808d?auto=format&fit=crop&w=2200&q=90') center/cover}}.hero-inner{{padding:70px 0 72px;width:100%}}.kicker,.eyebrow{{color:var(--gold);font-size:.74rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase}}h1{{font-size:clamp(3rem,8vw,7.8rem);line-height:.9;letter-spacing:-.07em;margin:18px 0;max-width:800px}}h2{{font-size:clamp(2rem,4vw,3.6rem);line-height:1;letter-spacing:-.05em;margin:0 0 18px}}h3{{margin:6px 0;font-size:1.25rem}}.lede{{font-size:1.15rem;max-width:650px;color:#e8edf0}}.button{{display:inline-flex;align-items:center;gap:8px;border:0;border-radius:999px;background:var(--red);color:#fff;padding:13px 20px;text-decoration:none;font-weight:800;cursor:pointer;box-shadow:0 8px 20px #c83b4b35}}.button.ghost{{background:#ffffff18;border:1px solid #ffffff55}}.button.small{{padding:9px 13px;font-size:.85rem}}.hero-actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}}.section{{padding:92px 0}}.section.alt{{background:#fff}}.section-head{{display:flex;justify-content:space-between;gap:30px;align-items:end;margin-bottom:30px}}.section-head p{{max-width:480px;color:var(--muted)}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:34px}}.stat,.panel,.flight-card,.image-card{{background:var(--card);border:1px solid var(--line);border-radius:22px;box-shadow:var(--shadow)}}.stat{{padding:20px}}.stat strong{{display:block;font-size:2rem;letter-spacing:-.06em}}.stat span{{color:var(--muted);font-size:.9rem}}.gallery{{display:grid;grid-template-columns:1.3fr 1fr 1fr;grid-template-rows:250px 250px;gap:14px}}.image-card{{overflow:hidden;position:relative;margin:0;min-height:220px}}.image-card:first-child{{grid-row:span 2}}.image-card img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s}}.image-card:hover img{{transform:scale(1.05)}}.image-card figcaption{{position:absolute;bottom:0;left:0;right:0;padding:35px 18px 15px;color:#fff;background:linear-gradient(transparent,#101820dd);display:flex;flex-direction:column}}.image-card figcaption span{{font-size:.85rem;color:#e6ecef}}.tabs{{display:flex;gap:8px;overflow:auto;padding-bottom:16px}}.tab{{border:1px solid var(--line);background:#fff;border-radius:999px;padding:10px 16px;cursor:pointer;white-space:nowrap}}.tab.active{{background:var(--ink);color:#fff}}.tab-panel{{display:none}}.tab-panel.active{{display:block}}.day-list{{display:grid;gap:8px}}.day-row{{width:100%;display:grid;grid-template-columns:46px 1fr 180px 72px;gap:12px;align-items:center;text-align:left;border:1px solid var(--line);background:#fff;border-radius:15px;padding:13px 16px;cursor:pointer;color:var(--ink)}}.day-row:hover,.day-row.selected{{border-color:var(--red);transform:translateX(4px)}}.day-number{{font-size:1.15rem;font-weight:900;color:var(--red)}}.day-row em{{display:block;font-style:normal;color:var(--muted);font-size:.88rem}}.day-route{{color:var(--muted);font-size:.86rem}}.day-row a{{font-size:.78rem;font-weight:800;color:var(--red);text-decoration:none}}.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.panel{{padding:26px}}.flight-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}}.flight-card{{padding:22px}}.flight-card .price{{display:block;font-size:2rem;letter-spacing:-.05em;margin:14px 0 5px}}.flight-card small{{font-size:.7rem;font-weight:600;letter-spacing:0;color:var(--muted)}}.flight-card p{{font-size:.88rem;color:var(--muted);min-height:44px}}.empty{{padding:22px;border:1px dashed var(--line);border-radius:18px;color:var(--muted)}}.calc{{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}}.range{{width:100%;accent-color:var(--red)}}.total{{font-size:4rem;letter-spacing:-.08em;color:var(--red)}}.checklist{{display:grid;gap:10px;padding:0;list-style:none}}.checklist label{{display:flex;gap:10px;align-items:center;padding:13px;background:#fff;border:1px solid var(--line);border-radius:12px}}footer{{background:var(--ink);color:#b6c2c9;padding:50px 0}}footer a{{color:#fff}}@media(max-width:800px){{.stats,.flight-grid,.grid-2,.calc{{grid-template-columns:1fr 1fr}}.gallery{{grid-template-columns:1fr 1fr;grid-template-rows:220px 220px}}.image-card:first-child{{grid-row:auto;grid-column:span 2}}.day-row{{grid-template-columns:38px 1fr 50px}}.day-route{{display:none}}}}@media(max-width:520px){{.wrap{{padding:0 16px}}.stats,.flight-grid,.grid-2,.calc{{grid-template-columns:1fr}}.gallery{{display:block}}.image-card{{height:240px;margin-bottom:12px}}h1{{font-size:4rem}}.section{{padding:60px 0}}}}
</style></head><body>
<header class="hero"><div class="wrap hero-inner"><div class="kicker">Japan · September / October 2026</div><h1>Tradičné Japonsko, po našom.</h1><p class="lede">18 dní pre päť ľudí. Tokio, Nikko, Kanazawa, Kjóto, Nara, Osaka a Himeji — s tempom, ktoré zvládnu aj rodičia.</p><div class="hero-actions"><a class="button" href="#plan">Pozrieť itinerár ↓</a><a class="button ghost" href="../docs/flight-options.md">Lety a ponuky ↗</a></div><div class="stats"><div class="stat"><strong>18</strong><span>dní / 17–18 nocí</span></div><div class="stat"><strong>5</strong><span>cestujúcich</span></div><div class="stat"><strong>2</strong><span>izby</span></div><div class="stat"><strong>VIE/BUD</strong><span>porovnávame odlety</span></div></div></div></header>
<main><section class="section"><div class="wrap"><div class="section-head"><div><div class="kicker">Moodboard</div><h2>Od neónov k machu.</h2></div><p>Nie je to naháňačka za atrakciami. Je to cesta cez vrstvy japonskej histórie — s dobrým jedlom, pohodlnými presunmi a rezervou na dážď.</p></div><div class="gallery">{image_cards}</div></div></section>
<section class="section alt" id="plan"><div class="wrap"><div class="section-head"><div><div class="kicker">Interactive route</div><h2>Plán na každý deň.</h2></div><p>Kliknutím na deň zvýrazníš trasu na mape. Každý odkaz sa otvorí v Google Maps.</p></div><div class="tabs"><button class="tab active" data-tab="route">Itinerár</button><button class="tab" data-tab="flights">Letenky</button><button class="tab" data-tab="stays">Ubytovanie</button><button class="tab" data-tab="budget">Rozpočet</button></div><div id="route" class="tab-panel active"><div class="day-list">{day_rows()}</div></div><div id="flights" class="tab-panel"><div class="flight-grid">{flight_cards(flights)}</div><p class="muted">Ceny sa zobrazia až po uložení overených pozorovaní do <code>data/raw/flight-observations.csv</code>.</p></div><div id="stays" class="tab-panel"><div class="grid-2"><div class="panel"><div class="eyebrow">Tokio</div><h3>Ueno / Asakusa</h3><p>Historické štvrte, metro a jednoduchý príchod z letiska. Hľadať 2 izby do 10 minút od stanice.</p><a class="button small" href="../docs/accommodation.md">Otvoriť shortlist ↗</a></div><div class="panel"><div class="eyebrow">Kjóto</div><h3>Kyoto Station / Gojo</h3><p>Najpraktickejšia základňa pre Naru, Fushimi Inari, Arashiyamu aj presun do Osaky.</p><a class="button small" href="https://www.booking.com/searchresults.html?ss=Kyoto&checkin=2026-09-30&checkout=2026-10-05&group_adults=5&no_rooms=2" target="_blank" rel="noopener">Hľadať ubytovanie ↗</a></div></div></div><div id="budget" class="tab-panel"><div class="panel calc"><div><div class="eyebrow">Budget calculator</div><h3>Aká drahá bude cesta?</h3><p>Posuň cenu letenky a odhadni celkový rozpočet na osobu.</p><input id="flightRange" class="range" type="range" min="450" max="1200" step="25" value="750"><p><b><span id="flightValue">750</span> €</b> letenka / osoba</p><ul class="checklist"><li><label><input type="checkbox" data-cost="450" checked> ubytovanie 450 €</label></li><li><label><input type="checkbox" data-cost="300" checked> doprava 300 €</label></li><li><label><input type="checkbox" data-cost="350" checked> jedlo 350 €</label></li><li><label><input type="checkbox" data-cost="150" checked> vstupy, poistenie, rezerva 150 €</label></li></ul></div><div><div class="eyebrow">Odhad</div><div class="total"><span id="budgetTotal">2 000</span> €</div><p>na osobu · bez nákupov</p><a class="button small" href="../docs/budget.md">Rozpočet v Markdown ↗</a></div></div></div></div></div></section>
<section class="section"><div class="wrap grid-2"><div><div class="kicker">Travel philosophy</div><h2>Menej stresu, viac miest.</h2><p>Ubytovanie vyberáme pri stanici, shinkansen rezervujeme pre všetkých naraz a Okinawu pridáme iba vtedy, ak lacný let nenaruší historickú trasu.</p><p><a class="button" href="../outputs/japan-trip-planner.pdf">Stiahnuť PDF plán ↗</a></p></div><div class="panel"><div class="eyebrow">Checklist pred nákupom</div><ul class="checklist"><li>☐ cena je pre všetkých 5 cestujúcich</li><li>☐ príručná batožina je v cene</li><li>☐ nejde o nebezpečný self-transfer</li><li>☐ ubytovanie má 2 izby a vlastnú kúpeľňu</li><li>☐ presuny sú znesiteľné pre rodičov</li></ul></div></div></section></main><footer><div class="wrap"><b>Japan Trip Planner</b><p>Generované z dát v repozitári · aktualizácia: {html.escape(__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M'))}</p><a href="../README.md">README</a> · <a href="../docs/itinerary.md">Markdown itinerár</a></div></footer>
<script>const DATA={payload};document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('.tab,.tab-panel').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.tab).classList.add('active')}}));document.querySelectorAll('.day-row').forEach(b=>b.addEventListener('click',()=>{{document.querySelectorAll('.day-row').forEach(x=>x.classList.remove('selected'));b.classList.add('selected')}}));const range=document.getElementById('flightRange'),fv=document.getElementById('flightValue'),total=document.getElementById('budgetTotal');function calc(){{let sum=Number(range.value);fv.textContent=range.value;document.querySelectorAll('[data-cost]').forEach(c=>{{if(c.checked)sum+=Number(c.dataset.cost)}});total.textContent=sum.toLocaleString('sk-SK')}}range.addEventListener('input',calc);document.querySelectorAll('[data-cost]').forEach(c=>c.addEventListener('change',calc));calc();</script></body></html>'''


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(OUT)
