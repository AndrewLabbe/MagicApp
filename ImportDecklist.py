import time
import requests
import json
import re

def extract_card_name(line):
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    match = re.match(r'\d+\s+(.*?)\s+\(', line)
    if match:
        return match.group(1).strip()
    else:
        parts = line.split(' ', 1)
        return parts[1].strip() if len(parts) > 1 else None

def fetch_card_data(card_name):
    url = f"https://api.scryfall.com/cards/named?exact={card_name}"
    response = requests.get(url)
    time.sleep(0.0075)  # To avoid spamming Scryfall

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch: {card_name} (status {response.status_code})")
        return None

def is_commander_legal(card_data):
    return card_data.get("legalities", {}).get("commander") == "legal"

def matches_color_identity(card_data, commander_colors):
    card_colors = set(card_data.get("color_identity", []))
    return card_colors.issubset(set(commander_colors))

def allows_duplicates(card_data):
    oracle = card_data.get("oracle_text", "").lower()
    type_line = card_data.get("type_line", "").lower()
    return (
        "basic" in type_line or
        "any number of cards named" in oracle or
        "no limit to the number of cards named" in oracle
    )

def import_decklist(deck_file, output_file):
    seen = {}
    all_cards = []
    commander_colors = []
    commander_data = None

    with open(deck_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        line = line.strip()
        if line.lower().startswith("commander:"):
            commander_name = line.split(":", 1)[1].strip()
            commander_data = fetch_card_data(commander_name)

            if not commander_data:
                print(f"❌ Failed to fetch commander: {commander_name}")
                return

            if not is_commander_legal(commander_data):
                print(f"❌ Commander is not legal in Commander: {commander_name}")
                return

            commander_colors = commander_data.get("color_identity", [])
            seen[commander_name] = commander_data
            all_cards.append(commander_data)
            print(f"✅ Commander set to: {commander_name} with colors {commander_colors}")
            break

    if not commander_colors:
        print("❌ No valid commander found. Aborting.")
        return

    # Process rest of the deck
    for line in lines[i+1:]:
        card_name = extract_card_name(line)
        if not card_name:
            continue

        if card_name in seen and not allows_duplicates(seen[card_name]):
            continue

        card_data = fetch_card_data(card_name)
        if not card_data:
            continue

        if not is_commander_legal(card_data):
            print(f"Skipping illegal card: {card_name}")
            continue

        if not matches_color_identity(card_data, commander_colors):
            print(f"Skipping off-color card: {card_name}")
            continue

        seen[card_name] = card_data
        all_cards.append(card_data)

    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(all_cards, out_file, indent=2)

    print(f"✅ Fetched and validated {len(all_cards)} cards (including commander). Saved to {output_file}")

def process_decklist(deck_file, output_file):
    with open(deck_file, "r", encoding="utf-8") as infile:
        all_cards = json.load(infile)

    fields_to_keep = [
        "tcgplayer_id", "name", "mana_cost", "cmc", "type_line",
        "oracle_text", "power", "toughness", "color_identity",
        "keywords", "rarity"
    ]

    trimmed_cards = []
    for card in all_cards:
        trimmed = {field: card.get(field, None) for field in fields_to_keep}
        trimmed_cards.append(trimmed)

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(trimmed_cards, outfile, indent=2)

    print(f"✅ Trimmed data saved to '{output_file}'")

# === USAGE ===
import_decklist("deck.txt", "deck_data.json")
process_decklist("deck_data.json", "processed_deck_data.json")
