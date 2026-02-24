import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime


class KinoArtScraper:
    """
    Scraper per la pagina Expat Friendly di Kino Art.

    Funzionalità:
      - scrape_events()    → scarica gli eventi e li salva nel database interno
      - save_to_json()     → esporta il database in un file JSON
      - generate_html()    → genera una pagina HTML nello stile di Kino Art
    """

    URL = "https://www.kinoart.cz/en/cycles/expat-friendly"

    # Simula un browser reale per evitare blocchi anti-bot
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self):
        self.database: list[dict] = []
        self.error: str | None = None

    # ──────────────────────────────────────────────
    # 1. SCRAPING
    # ──────────────────────────────────────────────

    def scrape_events(self) -> list[dict]:
        print(f"[Scraper] Fetching data from {self.URL} ...")

        try:
            response = requests.get(self.URL, headers=self.HEADERS, timeout=20)
            response.raise_for_status()
        except requests.RequestException as e:
            self.error = f"Network error: {e}"
            print(f"[Scraper] ERROR – {self.error}", file=sys.stderr)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        self.database = []

        blocks = soup.find_all("div", class_="events-calendar__event")

        if not blocks:
            self.error = "No event blocks found – the page structure may have changed."
            print(f"[Scraper] WARNING – {self.error}", file=sys.stderr)
            return []

        for block in blocks:
            try:
                title = block.find("h3", class_="title").text.strip()

                raw_time = (
                    block.find("p", class_="events-calendar__event-time")
                    .text.strip()
                    .replace("\n", " ")
                    .replace("\t", "")
                )
                date_time = " ".join(raw_time.split())

                ticket_url = "No link found"
                for tag in block.find_all("a", class_="button"):
                    if "Tickets" in tag.text:
                        ticket_url = tag["href"]
                        break

                self.database.append(
                    {"title": title, "date": date_time, "ticket_url": ticket_url}
                )

            except AttributeError:
                continue

        print(f"[Scraper] Found {len(self.database)} events.")
        return self.database

    # ──────────────────────────────────────────────
    # 2. SALVATAGGIO JSON
    # ──────────────────────────────────────────────

    def save_to_json(self, filepath: str = "events.json") -> None:
        """Salva il database in JSON. Crea sempre il file, anche se vuoto."""
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.database, f, indent=4, ensure_ascii=False)
        print(f"[JSON] Saved {len(self.database)} events → {filepath}")

    # ──────────────────────────────────────────────
    # 3. GENERAZIONE HTML
    # ──────────────────────────────────────────────

    def generate_html(self, filepath: str = "events.html") -> None:
        """Genera sempre l'HTML, anche in caso di errore o database vuoto."""
        generated_at = datetime.now().strftime("%d %B %Y, %H:%M")

        if self.error:
            body_content = f"""
            <div class="status-box status-box--error">
                <span class="material-icons icon">error_outline</span>
                <p><strong>Scraping failed</strong></p>
                <p>{self.error}</p>
            </div>"""
        elif not self.database:
            body_content = """
            <div class="status-box status-box--empty">
                <span class="material-icons icon">event_busy</span>
                <p>No upcoming Expat Friendly events found at the moment.<br>
                Check back next week!</p>
            </div>"""
        else:
            cards = ""
            for event in self.database:
                ticket_button = (
                    f'<a class="button" href="{event["ticket_url"]}" target="_blank">'
                    f'<span class="material-icons icon">confirmation_number</span> Tickets</a>'
                    if event["ticket_url"] != "No link found"
                    else '<span class="no-ticket">No ticket link available</span>'
                )
                cards += f"""
            <div class="events-calendar__event">
                <div class="events-calendar__event-text">
                    <div class="events-calendar__event-description">
                        <div class="events-calendar__event-title">
                            <h3 class="title">{event["title"]}</h3>
                        </div>
                        <p class="events-calendar__event-time">
                            <span class="material-icons icon">schedule</span>
                            {event["date"]}
                        </p>
                        <p class="events-calendar__event-buttons">
                            {ticket_button}
                        </p>
                    </div>
                </div>
            </div>"""

            body_content = f'<h2 class="section-title">Upcoming Screenings</h2>{cards}'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expat Friendly – Kino Art</title>
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {{ box-sizing: border-box; }}
        body {{ margin: 0; font-family: 'Roboto', Arial, sans-serif; background: #f4f0e8; color: #1a1a1a; }}
        a {{ color: inherit; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .site-header {{ background: #1a1a1a; color: #f4f0e8; padding: 18px 40px; display: flex; align-items: center; justify-content: space-between; }}
        .site-header .logo {{ font-size: 1.6rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }}
        .site-header nav a {{ color: #f4f0e8; margin-left: 24px; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.05em; }}
        .cycle-header {{ background: #1a1a1a; color: #f4f0e8; padding: 48px 40px 32px; border-bottom: 4px solid #e50070; }}
        .cycle-header h1 {{ font-size: 2.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin: 0 0 12px; }}
        .cycle-header p {{ max-width: 720px; line-height: 1.6; font-size: 0.95rem; color: #ccc; margin: 0; }}
        .cycle-header .meta {{ margin-top: 16px; font-size: 0.8rem; color: #888; }}
        .events-wrapper {{ max-width: 1100px; margin: 40px auto; padding: 0 24px 60px; }}
        .section-title {{ font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.1em; border-left: 4px solid #e50070; padding-left: 12px; margin-bottom: 24px; }}
        .events-calendar__event {{ background: #fff; border-radius: 2px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.08); transition: box-shadow .2s; }}
        .events-calendar__event:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,.14); }}
        .events-calendar__event-text {{ padding: 20px 24px; }}
        .events-calendar__event-description {{ display: flex; flex-direction: column; gap: 8px; }}
        .title {{ font-size: 1.25rem; font-weight: 700; margin: 0; }}
        .events-calendar__event-time {{ display: flex; align-items: center; gap: 6px; font-size: 0.88rem; color: #555; margin: 0; font-style: italic; }}
        .button {{ display: inline-flex; align-items: center; gap: 6px; background: #1a1a1a; color: #f4f0e8; padding: 8px 16px; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; border-radius: 2px; transition: background .2s; }}
        .button:hover {{ background: #e50070; text-decoration: none; }}
        .no-ticket {{ font-size: 0.82rem; color: #aaa; font-style: italic; }}
        .status-box {{ display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; padding: 60px 24px; border-radius: 4px; text-align: center; font-size: 1rem; }}
        .status-box .material-icons {{ font-size: 3rem; }}
        .status-box--empty {{ background: #fff; color: #888; }}
        .status-box--error {{ background: #fff0f0; color: #c0392b; border: 1px solid #f5c6c6; }}
        .material-icons.icon {{ font-size: 1rem; vertical-align: middle; }}
        .site-footer {{ background: #1a1a1a; color: #888; text-align: center; padding: 24px; font-size: 0.8rem; }}
        @media (max-width: 600px) {{
            .cycle-header {{ padding: 32px 20px 24px; }}
            .cycle-header h1 {{ font-size: 2rem; }}
            .events-wrapper {{ padding: 0 12px 40px; }}
            .site-header {{ padding: 14px 20px; }}
            .site-header nav {{ display: none; }}
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <span class="logo">Kino Art</span>
        <nav>
            <a href="https://www.kinoart.cz/en" target="_blank">Home</a>
            <a href="{self.URL}" target="_blank">Expat Friendly</a>
        </nav>
    </header>
    <div class="cycle-header">
        <h1>Expat Friendly</h1>
        <p>European and global art films with English subtitles, plus Czech films subtitled in English – making cinema in Brno accessible to everyone.</p>
        <p class="meta">Updated on {generated_at} · {len(self.database)} events</p>
    </div>
    <div class="events-wrapper">
        {body_content}
    </div>
    <footer class="site-footer">
        &copy; Kino Art Brno &nbsp;|&nbsp; Data scraped automatically from
        <a href="{self.URL}" target="_blank" style="color:#e50070;">{self.URL}</a>
    </footer>
</body>
</html>
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[HTML] Generated → {filepath}  ({len(self.database)} events)")


# ── Utilizzo ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    scraper = KinoArtScraper()
    scraper.scrape_events()
    scraper.save_to_json()
    scraper.generate_html()
