import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def scrape_cinema(url, cinema_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Logic for Kino Art and Kino Scala
        if "kinoart" in url or "kinoscala" in url:
            items = soup.find_all('div', class_='m-program-item')
            for item in items:
                title = item.find('h3', class_='m-program-item__title').text.strip()
                date_raw = item.find('div', class_='m-program-item__date').text.strip()
                link_el = item.find('a', class_='m-program-item__link')
                link = (url.split('/en')[0] + link_el['href']) if link_el else url
                
                # Standardizing date to ISO format YYYY-MM-DD
                parts = date_raw.split('.')
                day = parts[0].strip().zfill(2)
                month_str = parts[1].strip()
                
                month_map = {
                    "January": "01", "February": "02", "March": "03", "April": "04", 
                    "May": "05", "June": "06", "July": "07", "August": "08", 
                    "September": "09", "October": "10", "November": "11", "December": "12",
                    "1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06"
                }
                month = month_map.get(month_str, "02") 
                iso_date = f"2026-{month}-{day}" # Adjust year as needed
                
                events.append({
                    "title": title, "date": iso_date, "display_date": f"{day}. {month_str[:3]}",
                    "url": link, "cinema": cinema_name, "class": cinema_name.split()[1].lower()
                })

        # Simplified logic for Velky Spalicek
        elif "velkyspalicek" in url:
            # We add a placeholder date for now as Cinema City uses dynamic JS for dates
            events.append({
                "title": "Check Cinema City Schedule", "date": "2026-12-31", "display_date": "Live",
                "url": url, "cinema": "Velký Špalíček", "class": "spalicek"
            })
            
    except Exception as e:
        print(f"Error scraping {cinema_name}: {e}")
    return events

def generate_html(events):
    # Sort everything chronologically
    events.sort(key=lambda x: x['date'])
    events_json = json.dumps(events)
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brno Cinema - Next 2 Months</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --bec-red: #e30613; --bec-dark: #333; --bec-gray: #f4f4f4; }}
        body {{ font-family: 'Open Sans', sans-serif; background: #fff; margin: 0; padding: 20px; color: #4a4a4a; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 30px; padding-bottom: 10px; }}
        h1 {{ font-family: 'Montserrat'; text-transform: uppercase; margin: 0; font-size: 1.8rem; }}
        .view-label {{ color: #888; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 20px; display: block; }}
        
        .event-card {{ display: flex; align-items: center; padding: 18px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; transition: 0.2s; }}
        .event-card:hover {{ background: var(--bec-gray); }}
        
        .date-box {{ min-width: 70px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 20px; }}
        .day {{ display: block; font-size: 1.5rem; font-weight: 700; color: var(--bec-dark); }}
        .month {{ font-size: 0.8rem; text-transform: uppercase; color: var(--bec-red); font-weight: 700; }}
        
        .title-area {{ flex-grow: 1; }}
        .title {{ font-family: 'Montserrat'; font-size: 1.1rem; display: block; font-weight: 700; }}
        .cinema-tag {{ display: inline-block; font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; text-transform: uppercase; margin-top: 5px; color: white; }}
        .art {{ background: var(--bec-red); }} .scala {{ background: #000; }} .spalicek {{ background: #ff5a00; }}
        
        .buy-btn {{ font-weight: bold; color: var(--bec-red); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>Cinema Program</h1></header>
        <span class="view-label">Upcoming events (Next 60 Days)</span>
        <div id="eventList"></div>
    </div>

    <script>
        const events = {events_json};

        function render() {{
            const list = document.getElementById('eventList');
            const today = new Date();
            const twoMonthsFromNow = new Date();
            twoMonthsFromNow.setDate(today.getDate() + 60);

            const filtered = events.filter(e => {{
                const d = new Date(e.date);
                return d >= today && d <= twoMonthsFromNow;
            }});

            list.innerHTML = filtered.map(e => `
                <a href="${{e.url}}" class="event-card" target="_blank">
                    <div class="date-box">
                        <span class="day">${{e.display_date.split('.')[0]}}</span>
                        <span class="month">${{e.display_date.split(' ')[1]}}</span>
                    </div>
                    <div class="title-area">
                        <span class="title">${{e.title}}</span>
                        <span class="cinema-tag ${{e.class}}">${{e.cinema}}</span>
                    </div>
                    <div class="buy-btn">TICKETS →</div>
                </a>
            `).join('');
        }}
        render();
    </script>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    all_events = []
    all_events += scrape_cinema("https://www.kinoart.cz/en/programme", "Kino Art")
    all_events += scrape_cinema("https://www.kinoscala.cz/en/programme", "Kino Scala")
    all_events += scrape_cinema("https://www.velkyspalicek.cz/", "Velký Špalíček")
    generate_html(all_events)