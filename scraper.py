import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_cinema(url, cinema_name):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    events = []
    
    month_map = {
        "1": "January", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June",
        "7": "July", "8": "August", "9": "September", "10": "October", "11": "November", "12": "December",
        "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='m-program-item')

        for item in items:
            title_el = item.find('h3', class_='m-program-item__title')
            date_el = item.find('div', class_='m-program-item__date')
            link_el = item.find('a', class_='m-program-item__link')

            if title_el and date_el:
                title = title_el.text.strip()
                date_raw = date_el.text.strip()
                
                base_url = "https://www.kinoart.cz" if "kinoart" in url else "https://www.kinoscala.cz"
                full_link = base_url + link_el['href'] if link_el else url

                # Parsing data: "19. 2." o "19. February"
                parts = date_raw.split('.')
                day = parts[0].strip().zfill(2)
                month_part = parts[1].strip()

                if month_part.isdigit():
                    month_name = month_map.get(month_part.zfill(2), "Unknown")
                else:
                    month_name = month_part

                events.append({
                    "title": title,
                    "day": day,
                    "month": month_name,
                    "url": full_link,
                    "cinema": cinema_name
                })
    except Exception as e:
        print(f"Error scraping {cinema_name}: {e}")
        
    return events

def save_events_to_file(events):
    try:
        with open("events_list.txt", "w", encoding="utf-8") as f:
            for e in events:
                # Formato richiesto: title: "Flood", day: "25", month: "February", url: link
                line = f'title: "{e["title"]}", day: "{e["day"]}", month: "{e["month"]}", url: {e["url"]}\n'
                f.write(line)
        print("Successfully created events_list.txt")
    except Exception as e:
        print(f"Error creating txt file: {e}")

def generate_html(events):
    # Ordinamento cronologico
    try:
        events.sort(key=lambda x: (datetime.strptime(x['month'], "%B").month, int(x['day'])))
    except:
        pass

    events_json = json.dumps(events, indent=4)
    
    # Crea bottoni dinamici per i mesi
    existing_months = []
    for e in events:
        if e['month'] not in existing_months and e['month'] != "Unknown":
            existing_months.append(e['month'])
    
    buttons_html = '<button class="filter-btn active" onclick="filterEvents(\'all\')">All</button>'
    for m in existing_months:
        buttons_html += f'\n            <button class="filter-btn" onclick="filterEvents(\'{m}\')">{m}</button>'

    # (Template HTML richiesto dall'utente precedentemente)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brno Cinema Program</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --bec-red: #e30613; --bec-dark: #333333; --bec-gray: #f4f4f4; --bec-text: #4a4a4a; --transition: all 0.3s ease; }}
        body {{ font-family: 'Open Sans', sans-serif; background-color: #fff; color: var(--bec-text); margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{ margin-bottom: 40px; text-align: left; }}
        h1 {{ font-family: 'Montserrat', sans-serif; color: var(--bec-dark); font-size: 2.2rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: -1px; }}
        .accent-line {{ width: 60px; height: 5px; background-color: var(--bec-red); margin-bottom: 30px; }}
        .filters {{ margin-bottom: 30px; display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 8px 18px; border: 2px solid var(--bec-gray); background: white; cursor: pointer; font-weight: 600; border-radius: 20px; transition: var(--transition); }}
        .filter-btn.active, .filter-btn:hover {{ background-color: var(--bec-red); color: white; border-color: var(--bec-red); }}
        .event-list {{ display: flex; flex-direction: column; gap: 15px; }}
        .event-card {{ display: flex; align-items: center; background: #fff; border: 1px solid #eee; padding: 20px; border-radius: 8px; transition: var(--transition); text-decoration: none; color: inherit; }}
        .event-card:hover {{ transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-color: var(--bec-red); }}
        .event-date {{ min-width: 90px; text-align: center; border-right: 2px solid var(--bec-gray); margin-right: 25px; padding-right: 15px; }}
        .date-day {{ display: block; font-size: 1.8rem; font-weight: 700; color: var(--bec-dark); line-height: 1; }}
        .date-month {{ display: block; text-transform: uppercase; font-size: 0.8rem; font-weight: 700; color: var(--bec-red); }}
        .event-info {{ flex-grow: 1; }}
        .event-category {{ font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #999; margin-bottom: 4px; }}
        .event-title {{ font-family: 'Montserrat', sans-serif; font-size: 1.25rem; color: var(--bec-dark); margin: 0; font-weight: 700; }}
        .btn-tickets {{ background-color: var(--bec-gray); color: var(--bec-dark); padding: 10px 15px; border-radius: 4px; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; transition: var(--transition); }}
        .event-card:hover .btn-tickets {{ background-color: var(--bec-red); color: white; }}
        @media (max-width: 600px) {{ .event-card {{ flex-direction: column; align-items: flex-start; }} .event-date {{ border-right: none; border-bottom: 2px solid var(--bec-gray); margin-bottom: 15px; width: 100%; text-align: left; }} .btn-tickets {{ margin-top: 15px; display: inline-block; }} }}
    </style>
</head>
<body>
<div class="container">
    <header>
        <h1>Cinema Program</h1>
        <div class="accent-line"></div>
        <div class="filters">
            {buttons_html}
        </div>
    </header>
    <div class="event-list" id="eventList"></div>
</div>
<script>
    const events = {events_json};

    function displayEvents(filter) {{
        const list = document.getElementById('eventList');
        list.innerHTML = '';
        const filtered = filter === 'all' ? events : events.filter(e => e.month === filter);
        filtered.forEach(event => {{
            const card = document.createElement('a');
            card.className = 'event-card';
            card.href = event.url;
            card.target = "_blank";
            card.innerHTML = `
                <div class="event-date">
                    <span class="date-day">${{event.day}}</span>
                    <span class="date-month">${{event.month.substring(0,3)}}</span>
                </div>
                <div class="event-info">
                    <div class="event-category">${{event.cinema}} • English Friendly</div>
                    <h2 class="event-title">${{event.title}}</h2>
                </div>
                <div class="btn-tickets">Tickets</div>
            `;
            list.appendChild(card);
        }});
    }}

    function filterEvents(month) {{
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.classList.remove('active');
            if(btn.innerText === month || (month === 'all' && btn.innerText === 'All')) btn.classList.add('active');
        }});
        displayEvents(month);
    }}
    displayEvents('all');
</script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    all_events = []
    all_events += scrape_cinema("https://www.kinoart.cz/en/cycles/expat-friendly", "Kino Art")
    #all_events += scrape_cinema("https://www.kinoscala.cz/en/programme", "Kino Scala")
    
    if all_events:
        generate_html(all_events)
        save_events_to_file(all_events)
    else:
        print("No events found, skipping file generation.")