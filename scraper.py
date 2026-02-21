import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_cinema(url, cinema_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # TIC Brno Logic (Kino Art & Scala)
        if "kinoart" in url or "kinoscala" in url:
            items = soup.find_all('div', class_='m-program-item')
            for item in items:
                title = item.find('h3', class_='m-program-item__title').text.strip()
                date_info = item.find('div', class_='m-program-item__date').text.strip()
                link_el = item.find('a', class_='m-program-item__link')
                link = (url.split('/en')[0] + link_el['href']) if link_el else url
                
                parts = date_info.split('.')
                day = parts[0].strip().zfill(2)
                month = parts[1].strip() if len(parts) > 1 else ""
                
                events.append({
                    "title": title, "day": day, "month": month, 
                    "url": link, "cinema": cinema_name, "class": cinema_name.split()[1].lower()
                })

        # Cinema City (Velky Spalicek) logic
        elif "velkyspalicek" in url:
            # Note: Cinema City uses heavy JS. We scrape the 'no-js' fallbacks if present
            # or look for data attributes.
            items = soup.select('.movie-row, .qb-movie-item') 
            for item in items:
                title = item.select_one('h4, .qb-movie-name').text.strip()
                events.append({
                    "title": title, "day": "Now", "month": "Playing", 
                    "url": url, "cinema": "Velký Špalíček", "class": "spalicek"
                })

    except Exception as e:
        print(f"Error scraping {cinema_name}: {e}")
    return events

def generate_html(events):
    # Sort events by day (simplistic)
    events.sort(key=lambda x: x['day'] if x['day'].isdigit() else '99')
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
        body {{ font-family: 'Open Sans', sans-serif; background: #fff; margin: 0; padding: 20px; color: #4a4a4a; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 20px; padding-bottom: 10px; }}
        h1 {{ font-family: 'Montserrat'; text-transform: uppercase; margin: 0; font-size: 1.8rem; }}
        
        .controls {{ display: flex; flex-direction: column; gap: 15px; margin-bottom: 30px; }}
        .search-bar {{ width: 100%; padding: 15px; border: 2px solid var(--bec-gray); border-radius: 5px; font-size: 1rem; box-sizing: border-box; }}
        .filters {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 8px 15px; border: none; border-radius: 20px; cursor: pointer; font-weight: 600; background: var(--bec-gray); transition: 0.3s; }}
        .filter-btn.active {{ background: var(--bec-red); color: white; }}

        .event-card {{ display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.3s; }}
        .event-card:hover {{ background: var(--bec-gray); transform: translateX(5px); }}
        
        .date-box {{ min-width: 75px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 20px; }}
        .day {{ display: block; font-size: 1.6rem; font-weight: 700; color: var(--bec-dark); }}
        .month {{ font-size: 0.8rem; text-transform: uppercase; color: var(--bec-red); font-weight: 700; }}
        
        .title-area {{ flex-grow: 1; }}
        .title {{ font-family: 'Montserrat'; font-size: 1.1rem; display: block; }}
        .cinema-tag {{ display: inline-block; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; margin-top: 5px; color: white; }}
        .art {{ background: var(--bec-red); }}
        .scala {{ background: #000; }}
        .spalicek {{ background: #ff5a00; }}
        
        .buy-btn {{ font-weight: bold; color: var(--bec-red); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>Brno Cinema Hub</h1></header>
        <div class="controls">
            <input type="text" id="searchInput" class="search-bar" placeholder="Search for movies, actors, or dates..." onkeyup="filter()">
            <div class="filters">
                <button class="filter-btn active" onclick="setFilter('all', this)">All Cinemas</button>
                <button class="filter-btn" onclick="setFilter('art', this)">Kino Art</button>
                <button class="filter-btn" onclick="setFilter('scala', this)">Kino Scala</button>
                <button class="filter-btn" onclick="setFilter('spalicek', this)">Velký Špalíček</button>
            </div>
        </div>
        <div id="eventList"></div>
    </div>

    <script>
        const events = {events_json};
        let currentCinema = 'all';

        function render(data) {{
            const list = document.getElementById('eventList');
            list.innerHTML = data.map(e => `
                <a href="${{e.url}}" class="event-card" target="_blank">
                    <div class="date-box">
                        <span class="day">${{e.day}}</span>
                        <span class="month">${{e.month}}</span>
                    </div>
                    <div class="title-area">
                        <span class="title">${{e.title}}</span>
                        <span class="cinema-tag ${{e.class}}">${{e.cinema}}</span>
                    </div>
                    <div class="buy-btn">TICKETS →</div>
                </a>
            `).join('');
        }}

        function setFilter(cinema, btn) {{
            currentCinema = cinema;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            filter();
        }}

        function filter() {{
            const term = document.getElementById('searchInput').value.toLowerCase();
            const filtered = events.filter(e => {{
                const matchSearch = e.title.toLowerCase().includes(term) || e.month.toLowerCase().includes(term);
                const matchCinema = currentCinema === 'all' || e.class === currentCinema;
                return matchSearch && matchCinema;
            }});
            render(filtered);
        }}

        // Initial render: Show all movies immediately
        render(events);
    </script>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    all_data = []
    all_data += scrape_cinema("https://www.kinoart.cz/en/programme", "Kino Art")
    all_data += scrape_cinema("https://www.kinoscala.cz/en/programme", "Kino Scala")
    all_data += scrape_cinema("https://www.velkyspalicek.cz/", "Velký Špalíček")
    generate_html(all_data)