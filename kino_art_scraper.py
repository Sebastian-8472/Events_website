import requests
from bs4 import BeautifulSoup
import json
import re
from transformers import pipeline

class KinoArtManager:
    def __init__(self, url="https://www.kinoart.cz/en/cycles/expat-friendly"):
        self.url = url
        self.events = []
        
        # Comprehensive Czech to English Mapping for Dates
        self.date_translation = {
            "pondělí": "Monday", "úterý": "Tuesday", "středa": "Wednesday",
            "čtvrtek": "Thursday", "pátek": "Friday", "sobota": "Saturday",
            "neděle": "Sunday",
            "ledna": "January", "února": "February", "března": "March",
            "dubna": "April", "května": "May", "června": "June",
            "července": "July", "srpna": "August", "září": "September",
            "října": "October", "listopadu": "November", "prosince": "December"
        }

        print("Initializing Translation Engine (Czech to English)...")
        # Helsinki-NLP/opus-mt-cs-en: Specifically for Czech to English
        self.translator = pipeline(
            "translation", 
            model="Helsinki-NLP/opus-mt-cs-en", 
            device=-1
        )

    def translate_date(self, date_raw):
        """Converts Czech date words to English equivalents."""
        d = date_raw.lower()
        for cz, en in self.date_translation.items():
            d = d.replace(cz, en)
        return d.title()

    def scrape_events(self):
        print(f"Scraping {self.url}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

        self.events = []
        movie_blocks = soup.find_all('div', class_='events-calendar__event') 
        
        for block in movie_blocks:
            try:
                title_orig = block.find('h3', class_='title').text.strip()
                date_raw = block.find('p', class_='events-calendar__event-time').text.strip()
                
                # Fix the Date
                eng_date = self.translate_date(date_raw)
                
                ticket_link = "No link found"
                for tag in block.find_all('a', class_='button'):
                    if 'Tickets' in tag.text:
                        ticket_link = tag['href']
                        break
                
                self.events.append({
                    "title_orig": title_orig,
                    "title_en": "", 
                    "date_string": eng_date,
                    "ticket_url": ticket_link
                })
            except Exception:
                continue
        return self.events

    def translate_events(self):
        if not self.events: return
        print(f"Translating {len(self.events)} titles to English...")
        for event in self.events:
            result = self.translator(event['title_orig'], max_length=100)
            event['title_en'] = result[0]['translation_text']

    def save_to_json(self, filename="events.json"):
        """Generates the JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {filename}")

    def generate_html(self, output_filename="index.html"):
        """Generates the English index.html."""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Kino Art - Expat Friendly</title>
            <style>
                :root {{ --bec-red: #e30613; }}
                body {{ font-family: 'Open Sans', sans-serif; padding: 40px; color: #333; }}
                .container {{ max-width: 850px; margin: 0 auto; }}
                header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 30px; }}
                .event-card {{ display: flex; padding: 20px 0; border-bottom: 1px solid #ddd; text-decoration: none; color: inherit; transition: 0.2s; }}
                .event-card:hover {{ background: #f9f9f9; padding-left: 10px; }}
                .date-column {{ min-width: 250px; color: var(--bec-red); font-weight: bold; font-size: 0.9rem; text-transform: uppercase; }}
                .title-en {{ font-size: 1.2rem; font-weight: bold; display: block; }}
                .title-orig {{ font-size: 0.85rem; color: #777; font-style: italic; }}
                .btn {{ color: var(--bec-red); font-weight: bold; margin-left: auto; align-self: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header><h1>Kino Art - Expat Friendly Program</h1></header>
                {event_items}
            </div>
        </body>
        </html>
        """
        items_html = ""
        for e in self.events:
            items_html += f"""
            <a href="{e['ticket_url']}" class="event-card" target="_blank">
                <div class="date-column">{e['date_string']}</div>
                <div class="info">
                    <span class="title-en">{e['title_en']}</span>
                    <span class="title-orig">{e['title_orig']}</span>
                </div>
                <div class="btn">TICKETS →</div>
            </a>"""
        
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_template.format(event_items=items_html))
        print(f"HTML successfully generated as {output_filename}")

if __name__ == "__main__":
    manager = KinoArtManager()
    manager.scrape_events()
    manager.translate_events()
    manager.save_to_json("events.json") # Generates the JSON
    manager.generate_html("events.html") # Generates the HTML
    print("\nAll files updated and translated to English!")