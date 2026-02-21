import requests
from bs4 import BeautifulSoup
import json
def scrape_kino_art():
    url = "https://www.kinoart.cz/en/cycles/expat-friendly"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    
    # Kino Art uses specific classes for their program items
    # Note: If they change their website layout, these selectors might need a tweak
    for item in soup.select('.program-item'):
        try:
            title = item.select_one('.program-item__title').text.strip()
            date_raw = item.select_one('.program-item__date').text.strip() # e.g. "19. February"
            link = "https://www.kinoart.cz" + item.select_one('a')['href']
            
            day = date_raw.split('.')[0].strip()
            month = date_raw.split('.')[1].strip()
            
            events.append({
                "title": title,
                "day": day,
                "month": month,
                "url": link
            })
        except Exception:
            continue
            
    return events
# This part generates the HTML file with the data injected
def generate_html(events):
    events_json = json.dumps(events)
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Kino Art Expat Program</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
        <style>
            :root {{ --bec-red: #e30613; --bec-dark: #333; --bec-gray: #f4f4f4; }}
            body {{ font-family: 'Open Sans', sans-serif; padding: 40px; color: #4a4a4a; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .search-bar {{ width: 100%; padding: 12px; margin-bottom: 20px; border: 2px solid var(--bec-gray); border-radius: 8px; font-size: 1rem; }}
            .event-card {{ display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.2s; }}
            .event-card:hover {{ background: #fffcfc; border-left: 4px solid var(--bec-red); padding-left: 11px; }}
            .date-box {{ min-width: 80px; text-align: center; }}
            .day {{ display: block; font-size: 1.5rem; font-weight: 700; color: var(--bec-red); }}
            .month {{ font-size: 0.8rem; text-transform: uppercase; font-weight: 600; }}
            .title {{ font-family: 'Montserrat'; font-size: 1.1rem; margin-left: 20px; flex-grow: 1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Expat Friendly Cinema</h1>
            <input type="text" id="searchInput" class="search-bar" placeholder="Search for a movie..." onkeyup="search()">
            <div id="list"></div>
        </div>
<script>
            const events = {events_json};
            
            function render(data) {{
                const list = document.getElementById('list');
                list.innerHTML = data.map(e => `
                    <a href="${{e.url}}" class="event-card" target="_blank">
                        <div class="date-box">
                            <span class="day">${{e.day}}</span>
                            <span class="month">${{e.month}}</span>
                        </div>
                        <div class="title">${{e.title}}</div>
                        <div style="color:var(--bec-red); font-weight:bold;">→</div>
                    </a>
                `).join('');
            }}

function search() {{
                const term = document.getElementById('searchInput').value.toLowerCase();
                const filtered = events.filter(e => e.title.toLowerCase().includes(term));
                render(filtered);
            }}
render(events);
        </script>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
data = scrape_kino_art()
generate_html(data)
print("Page updated successfully!")
