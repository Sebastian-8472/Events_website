import requests
from bs4 import BeautifulSoup
import json

def scrape_kino_art():
    url = "https://www.kinoart.cz/en/cycles/expat-friendly"
    
    # 1. Download the webpage
    print(f"Fetching data from {url}...")
    response = requests.get(url)
    
    # 2. Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    events_data = []
    
    # 3. Find all movie containers 
    movie_blocks = soup.find_all('div', class_='events-calendar__event') 
    
    for block in movie_blocks:
        try:
            # Extract the title
            title = block.find('h3', class_='title').text.strip()
            
            # Extract the date/time (Note: changed 'div' to 'p'!)
            # We use replace() to clean up messy hidden newlines in the text
            date_time = block.find('p', class_='events-calendar__event-time').text.strip().replace('\n', ' ').replace('\t', '')
            
            # Extract the ticket link (Looking for the a tag with class 'button')
            ticket_tags = block.find_all('a', class_='button')
            ticket_link = "No link found"
            
            # Loop through buttons to find the one for Tickets
            for tag in ticket_tags:
                if 'Tickets' in tag.text:
                    ticket_link = tag['href']
                    break
            
            # Store it in a dictionary
            events_data.append({
                "title": title,
                "date": date_time,
                "ticket_url": ticket_link
            })
            
        except AttributeError:
            continue

    # 4. Save the results to a JSON file
    with open('events.json', 'w', encoding='utf-8') as f:
        json.dump(events_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully saved {len(events_data)} events to events.json!")

if __name__ == '__main__':
    scrape_kino_art()
