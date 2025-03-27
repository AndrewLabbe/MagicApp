import requests
import json

def fetch_card_data(card_name, output_file):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        card_data = response.json()
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(card_data, f, indent=2)
        print(f"Data for '{card_name}' written to {output_file}")
    else:
        print(f"Failed to fetch data for '{card_name}'. Status code: {response.status_code}")

# Usage
fetch_card_data("Sol Ring", "sol_ring_data.txt")
