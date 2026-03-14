import requests
from bs4 import BeautifulSoup
import json
import os
from transformers import pipeline

class KinoArtManager:
    """
    A class to manage Kino Art cinema events: scraping, translating, 
    and generating web/data reports.
    """

    def __init__(self, url="https://www.kinoart.cz/en/cycles/expat-friendly"):
        """
        Initializes the manager with the target URL and the translation model.
        """
        self.url = url
        self.events = []
        
        print("Initializing Translation Engine (Helsinki-NLP)...")
        # Helsinki-NLP/opus-mt-en-it: Translates English to Italian.
        # device=-1 forces the use of CPU, which is required for GitHub Actions.
        self.translator = pipeline(
            "translation", 
            model="Helsinki-NLP/opus-mt-en-it", 
            device=-1
        )

    def scrape_events(self):
        """
        Scrapes movie titles, dates, and ticket URLs from the Kino Art website.
        Matches the logic found in your original scraper (1).py script.
        """
        print(f"Fetching data from {self.url}...")
        try:
            response = requests.get(self.url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error during download: {e}")
            return []

        self.events = []
        # Find all movie containers based on the site's calendar structure
        movie_blocks = soup.find_all('div', class_='events-calendar__event') 
        
        for block in movie_blocks:
            try:
                # 1. Extract the Title
                title = block.find('h3', class_='title').text.strip()
                
                # 2. Extract Date/Time and clean newlines/tabs
                date_time = block.find('p', class_='events-calendar__event-time').text.strip().replace('\n', ' ').replace('\t', '')
                
                # 3. Extract the Ticket Link
                ticket_tags = block.find_all('a', class_='button')
                ticket_link = "No link found"
                for tag in ticket_tags:
                    if 'Tickets' in tag.text:
                        ticket_link = tag['href']
                        break
                
                # Append the gathered data to our local "database"
                self.events.append({
                    "title_en": title,
                    "title_it": "", # Placeholder for translation
                    "date_string": date_time,
                    "ticket_url": ticket_link
                })
            except AttributeError:
                # Skip blocks that do not match the expected structure
                continue
        
        print(f"Scraping completed: {len(self.events)} events found.")
        return self.events

    def translate_events(self):
        """
        Translates the English titles to Italian using the HuggingFace model.
        """
        if not self.events:
            print("No events to translate.")
            return

        print(f"Translating {len(self.events)} titles...")
        for event in self.events:
            try:
                # Perform translation
                result = self.translator(event['title_en'], max_length=100)
                event['title_it'] = result[0]['translation_text']
            except Exception as e:
                print(f"Translation error for '{event['title_en']}': {e}")
                event['title_it'] = event['title_en'] # Fallback to English

    def save_to_json(self, filename="events.json"):
        """
        Saves the processed event data into a JSON file.
        """
        if not self.events:
            print("No data to save.")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=4, ensure_ascii=False)
        print(f"JSON data saved to {filename}")

    def generate_html(self, output_filename="index.html"):
        """
        Generates a BEC-styled HTML page. 
        Note: CSS braces are doubled {{ }} to avoid Python string format errors.
        """
        if not self.events:
            print("No events available to generate HTML.")
            return

        # HTML Template with BEC Branding
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kino Art - Expat Friendly</title>
            <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
            <style>
                :root {{ --bec-red: #e30613; --bec-dark: #333; --bec-gray: #f4f4f4; }}
                body {{ font-family: 'Open Sans', sans-serif; background: #fff; margin: 0; padding: 20px; color: #4a4a4a; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 30px; padding-bottom: 10px; }}
                h1 {{ font-family: 'Montserrat'; text-transform: uppercase; margin: 0; font-size: 1.8rem; }}
                .event-card {{ display: flex; align-items: center; padding: 20px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.3s; }}
                .event-card:hover {{ background: var(--bec-gray); transform: translateX(5px); }}
                .date-box {{ min-width: 120px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 20px; }}
                .date-text {{ display: block; font-size: 0.85rem; font-weight: 700; color: var(--bec-red); text-transform: uppercase; }}
                .title-container {{ flex-grow: 1; }}
                .title-it {{ font-family: 'Montserrat'; font-size: 1.2rem; font-weight: 700; display: block; }}
                .title-en {{ font-size: 0.9rem; font-style: italic; color: #888; display: block; }}
                .buy-btn {{ font-weight: bold; color: var(--bec-red); white-space: nowrap; margin-left: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <header><h1>Kino Art - Programma per Expat</h1></header>
                <div id="eventList">
                    {event_items}
                </div>
            </div>
        </body>
        </html>
        """

        event_items_html = ""
        for e in self.events:
            # Shorten date string for display if it contains a comma
            display_date = e['date_string'].split(',')[0] if ',' in e['date_string'] else e['date_string']
            
            event_items_html += f"""
            <a href="{e['ticket_url']}" class="event-card" target="_blank">
                <div class="date-box">
                    <span class="date-text">{display_date}</span>
                </div>
                <div class="title-container">
                    <span class="title-it">{e['title_it']}</span>
                    <span class="title-en">{e['title_en']}</span>
                </div>
                <div class="buy-btn">BIGLIETTI →</div>
            </a>
            """

        # Populate the template with the generated items
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(html_template.format(event_items=event_items_html))
        
        print(f"HTML page generated successfully: {output_filename}")

# --- Automation Execution ---
if __name__ == "__main__":
    # Create the manager instance
    manager = KinoArtManager()
    
    # 1. Fetch data from the web
    manager.scrape_events()
    
    # 2. Translate titles to Italian
    manager.translate_events()
    
    # 3. Export data to JSON for other uses
    manager.save_to_json("events.json")
    
    # 4. Create the bilingual styled website (index.html)
    manager.generate_html("index.html")
    
    print("\nWorkflow completed successfully at 24:00 (Daily Update).")
    scraper.generate_html()
