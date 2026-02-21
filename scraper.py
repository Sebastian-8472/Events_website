import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_kino_art():
    url = "https://www.kinoart.cz/en/cycles/expat-friendly"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events = []
    # Targets the movie cards on the Kino Art website
    items = soup.find_all('div', class_='m-program-item')
    
    for item in items:
        try:
            title = item.find('h3', class_='m-program-item__title').text.strip()
            # Extract date: usually "19. 2." or "19. February"
            date_info = item.find('div', class_='m-program-item__date').text.strip()
            link = "https://www.kinoart.cz" + item.find('a', class_='m-program-item__link')['href']
            
            # Splitting "19. February" into Day and Month
            parts = date_info.split('.')
            day = parts[0].strip()
            month = parts[1].strip() if len(parts) > 1 else ""

            events.append({
                "title": title,
                "day": day,
                "month": month,
                "url": link
            })
        except Exception as e:
            print(f"Skipping an item due to error: {e}")
            continue
            
    return events

def generate_html(events):
    events_json = json.dumps(events)
    # The template includes the Search Bar and BEC-inspired styling
    html_template = f"""
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
        .search-container {{ margin-bottom: 30px; }}
        #searchInput {{ width: 100%; padding: 15px; border: 2px solid var(--bec-gray); border-radius: 5px; font-size: 1rem; box-sizing: border-box; }}
        #searchInput:focus {{ outline: none; border-color: var(--bec-red); }}
        .event-card {{ display: flex; align-items: center; padding: 20px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.3s; }}
        .event-card:hover {{ background: var(--bec-gray); transform: translateX(5px); }}
        .date-box {{ min-width: 70px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 20px; }}
        .day {{ display: block; font-size: 1.6rem; font-weight: 700; color: var(--bec-dark); }}
        .month {{ font-size: 0.8rem; text-transform: uppercase; color: var(--bec-red); font-weight: 700; }}
        .title {{ font-family: 'Montserrat'; font-size: 1.2rem; flex-grow: 1; }}
        .no-results {{ padding: 20px; text-align: center; color: #999; }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>Expat Friendly Movies</h1></header>
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Type to search movies..." onkeyup="filterMovies()">
        </div>
        <div id="eventList"></div>
    </div>

    <script>
        const events = {events_json};

        function render(data) {{
            const list = document.getElementById('eventList');
            if (data.length === 0) {{
                list.innerHTML = '<div class="no-results">No movies found matching your search.</div>';
                return;
            }}
            list.innerHTML = data.map(e => `
                <a href="${{e.url}}" class="event-card" target="_blank">
                    <div class="date-box">
                        <span class="day">${{e.day}}</span>
                        <span class="month">${{e.month}}</span>
                    </div>
                    <div class="title">${{e.title}}</div>
                    <div style="font-weight:bold; color:var(--bec-red);">BUY →</div>
                </a>
            `).join('');
        }}

        function filterMovies() {{
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

if __name__ == "__main__":
    data = scrape_kino_art()
    generate_html(data)