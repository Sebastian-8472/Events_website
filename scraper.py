import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def scrape_cinema(url, cinema_name):
    headers = {'User-Agent': 'Mozilla/5.0'}
    events = []
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "kinoart" in url or "kinoscala" in url:
            items = soup.find_all('div', class_='m-program-item')
            for item in items:
                title = item.find('h3', class_='m-program-item__title').text.strip()
                date_raw = item.find('div', class_='m-program-item__date').text.strip()
                link_el = item.find('a', class_='m-program-item__link')
                link = (url.split('/en')[0] + link_el['href']) if link_el else url
                
                # Convert "19. 2." or "19. February" to YYYY-MM-DD
                parts = date_raw.split('.')
                day = parts[0].strip().zfill(2)
                # Note: We assume current year or next if it's Jan
                month_val = parts[1].strip()
                # Simple mapper for month names/numbers
                month_map = {"January": "01", "February": "02", "March": "03", "April": "04", 
                             "May": "05", "June": "06", "July": "07", "August": "08", 
                             "September": "09", "October": "10", "November": "11", "December": "12",
                             "1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06"}
                
                month = month_map.get(month_val, "02") # Default to Feb for this specific cycle
                iso_date = f"2026-{month}-{day}"
                
                events.append({
                    "title": title, 
                    "date": iso_date,
                    "display_date": f"{day}. {month_val}",
                    "url": link, 
                    "cinema": cinema_name, 
                    "class": cinema_name.split()[1].lower() if " " in cinema_name else cinema_name.lower()
                })
    except Exception as e:
        print(f"Error: {e}")
    return events

def generate_html(events):
    events_json = json.dumps(events)
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brno Cinema - 30 Day Outlook</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --bec-red: #e30613; --bec-dark: #333; --bec-gray: #f4f4f4; }}
        body {{ font-family: 'Open Sans', sans-serif; margin: 0; padding: 20px; color: #4a4a4a; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        header {{ border-bottom: 4px solid var(--bec-red); margin-bottom: 20px; }}
        .controls {{ margin-bottom: 30px; }}
        label {{ font-weight: bold; display: block; margin-bottom: 5px; font-size: 0.9rem; }}
        .search-bar {{ width: 100%; padding: 12px; border: 2px solid var(--bec-gray); border-radius: 5px; font-size: 1rem; }}
        .event-card {{ display: flex; align-items: center; padding: 15px; border-bottom: 1px solid #eee; text-decoration: none; color: inherit; }}
        .date-box {{ min-width: 80px; text-align: center; border-right: 2px solid var(--bec-red); margin-right: 20px; }}
        .day {{ display: block; font-size: 1.4rem; font-weight: 700; }}
        .cinema-tag {{ font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 10px; color: white; text-transform: uppercase; }}
        .art {{ background: var(--bec-red); }} .scala {{ background: #000; }}
        .view-info {{ font-size: 0.85rem; color: #666; margin-bottom: 10px; font-style: italic; }}
    </style>
</head>
<body>
    <div class="container">
        <header><h1>Cinema Schedule</h1></header>
        <div class="controls">
            <label>Filter by Date (e.g., "2026-02-25" or "March"):</label>
            <input type="text" id="dateSearch" class="search-bar" placeholder="Enter date..." onkeyup="filter()">
        </div>
        <div id="viewStatus" class="view-info">Showing events for the next 30 days:</div>
        <div id="eventList"></div>
    </div>

    <script>
        const events = {events_json};
        
        function filter() {{
            const term = document.getElementById('dateSearch').value.toLowerCase();
            const status = document.getElementById('viewStatus');
            
            const today = new Date();
            const nextMonth = new Date();
            nextMonth.setDate(today.getDate() + 30);

            const filtered = events.filter(e => {{
                const eventDate = new Date(e.date);
                
                if (term === "") {{
                    // DEFAULT: Show only next 30 days
                    status.innerText = "Showing events for the next 30 days:";
                    return eventDate >= today && eventDate <= nextMonth;
                }} else {{
                    // SEARCH MODE: Show anything that matches the date string
                    status.innerText = "Search results for: " + term;
                    return e.date.includes(term) || e.display_date.toLowerCase().includes(term);
                }}
            }});
            render(filtered);
        }}

        function render(data) {{
            const list = document.getElementById('eventList');
            list.innerHTML = data.length ? data.map(e => `
                <a href="${{e.url}}" class="event-card" target="_blank">
                    <div class="date-box">
                        <span class="day">${{e.date.split('-')[2]}}</span>
                        <span class="month">${{e.display_date.split(' ')[1]}}</span>
                    </div>
                    <div style="flex-grow:1">
                        <span style="font-weight:600">${{e.title}}</span><br>
                        <span class="cinema-tag ${{e.class}}">${{e.cinema}}</span>
                    </div>
                    <div style="color:var(--bec-red); font-weight:bold;">→</div>
                </a>
            `).join('') : '<p>No events found for this timeframe.</p>';
        }}

        filter(); // Run on load
    </script>
</body>
</html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    data = scrape_cinema("https://www.kinoart.cz/en/programme", "Kino Art")
    data += scrape_cinema("https://www.kinoscala.cz/en/programme", "Kino Scala")
    generate_html(data)