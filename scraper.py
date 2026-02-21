import requests
from bs4 import BeautifulSoup
import json

def scrape_cinema(url, cinema_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # TIC Brno Cinemas (Art & Scala) use 'm-program-item'
        if "kinoart" in url or "kinoscala" in url:
            items = soup.find_all('div', class_='m-program-item')
            for item in items:
                title = item.find('h3', class_='m-program-item__title').text.strip()
                date_info = item.find('div', class_='m-program-item__date').text.strip()
                link = "https://www.kinoart.cz" if "kinoart" in url else "https://www.kinoscala.cz"
                link += item.find('a', class_='m-program-item__link')['href']
                
                parts = date_info.split('.')
                day = parts[0].strip()
                month = parts[1].strip() if len(parts) > 1 else ""
                
                events.append({
                    "title": title, "day": day, "month": month, 
                    "url": link, "cinema": cinema_name
                })

        # Velky Spalicek (Cinema City) - Simplified logic as they use heavy JS
        # Note: If the direct scrape fails due to JS, it will skip gracefully
        elif "velkyspalicek" in url:
            # Cinema City is harder to scrape without Selenium, 
            # but we can grab the basic list if available in the static HTML
            items = soup.select('.movie-card') # Example selector
            for item in items:
                title = item.select_one('.movie-title').text.strip()
                # ... extraction logic ...
                events.append({"title": title, "cinema": "Velký Špalíček", "day": "TBD", "month": "Check Site"})

    except Exception as e:
        print(f"Error scraping {cinema_name}: {e}")
    
    return events

def generate_html(events):
    events_json = json.dumps(events)
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brno Cinema Hub</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --bec-red: #e30613; --bec-dark: #333; --bec-gray: #f4f4f4; }}
        body {{ font-family: 'Open Sans', sans-serif; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 20px; }}
        .search-bar {{ width: 100%; padding: 15px; margin-bottom: 20px; border: 2px solid #ddd; border-radius: 5px; }}
        .event-card {{ display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.2s; }}
        .event-card:hover {{ background: var(--bec-gray); }}
        .date-box {{ min-width: 60px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 15px; }}
        .cinema-badge {{ font-size: 0.7rem; font-weight: bold; padding: 3px 8px; border-radius: 5px; text-transform: uppercase; margin-top: 5px; display: inline-block; }}
        .scala {{ background: #000; color: #fff; }}
        .art {{ background: var(--bec-red); color: #fff; }}
        .spalicek {{ background: #ff5a00; color: #fff; }}
        .title {{ font-family: 'Montserrat'; font-size: 1.1rem; flex-grow: 1; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>Brno Cinema Hub</h1></div>
        <input type="text" id="searchInput" class="search-bar" placeholder="Search movies, cinemas, or dates..." onkeyup="filter()">
        <div id="list"></div>
    </div>
    <script>
        const events = {events_json};
        function render(data) {{
            document.getElementById('list').innerHTML = data.map(e => `
                <a href="${{e.url}}" class="event-card" target="_blank">
                    <div class="date-box">
                        <b style="font-size:1.4rem;">${{e.day}}</b><br><small>${{e.month}}</small>
                    </div>
                    <div class="title">
                        ${{e.title}}<br>
                        <span class="cinema-badge ${{e.cinema.toLowerCase().split(' ')[0]}}">${{e.cinema}}</span>
                    </div>
                    <div style="color:var(--bec-red)">TICKETS →</div>
                </a>
            `).join('');
        }}
        function filter() {{
            const val = document.getElementById('searchInput').value.toLowerCase();
            render(events.filter(e => e.title.toLowerCase().includes(val) || e.cinema.toLowerCase().includes(val)));
        }}
        render(events);
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

all_events = []
all_events += scrape_cinema("https://www.kinoart.cz/en/programme", "Kino Art")
all_events += scrape_cinema("https://www.kinoscala.cz/en/programme", "Kino Scala")
# Velky Spalicek often requires JS rendering; we'll attempt a static scrape
all_events += scrape_cinema("https://www.velkyspalicek.cz/", "Velký Špalíček")

generate_html(all_events)