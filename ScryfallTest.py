import time
import requests
import json
import re

def extract_card_name(line):
    # Strip comments and trim whitespace
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    # Match everything after the quantity (e.g. '1') and before the first '('
    match = re.match(r'\d+\s+(.*?)\s+\(', line)
    if match:
        return match.group(1).strip()
    else:
        # Fallback: try to remove quantity and use rest
        parts = line.split(' ', 1)
        return parts[1].strip() if len(parts) > 1 else None

def fetch_card_data(card_name):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(url)
    time.sleep(0.0075)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch: {card_name} (status {response.status_code})")
        return None

def process_decklist(deck_file, output_file):
    seen = set()
    all_cards = []

    with open(deck_file, 'r', encoding='utf-8') as file:
        for line in file:
            card_name = extract_card_name(line)
            if card_name and card_name not in seen:
                seen.add(card_name)
                card_data = fetch_card_data(card_name)
                if card_data:
                    all_cards.append(card_data)

    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(all_cards, out_file, indent=2)

    print(f"✅ Fetched data for {len(all_cards)} cards and saved to {output_file}")

# === USAGE ===
process_decklist("deck.txt", "deck_data.json")
