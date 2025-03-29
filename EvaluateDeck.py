import json
import openai
import os
from dotenv import load_dotenv
import time

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_card_tags(card_data, model="gpt-3.5-turbo"):
    name = card_data.get("name", "")
    oracle_text = card_data.get("oracle_text", "")
    type_line = card_data.get("type_line", "")

    if not oracle_text:
        return []

    prompt = (
        f"You're analyzing Magic: The Gathering cards for a synergy-based deck builder.\n"
        f"Given the following card, extract 3 to 5 relevant tags that describe its mechanics, effects, and roles in decks.\n"
        f"Be concise and prefer mechanical/function-based tags over flavor.\n\n"
        f"Card Name: {name}\n"
        f"Type Line: {type_line}\n"
        f"Oracle Text: {oracle_text}\n\n"
        f"Tags:"
    )

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100,
        )
        output = response.choices[0].message["content"]
        tags = [tag.strip("-• ").strip() for tag in output.split("\n") if tag.strip()]
        return tags
    except Exception as e:
        print(f"❌ Error tagging '{name}': {e}")
        return []

def tag_cards_in_deck(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as infile:
        cards = json.load(infile)

    for i, card in enumerate(cards):
        print(f"🔍 Tagging card {i + 1}/{len(cards)}: {card.get('name', 'Unknown')}")
        tags = get_card_tags(card)
        card["ai_tags"] = tags
        time.sleep(0.5)  # Optional delay to avoid rate limits

    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(cards, outfile, indent=2)

    print(f"\n✅ All cards tagged and saved to {output_file}")

# === USAGE ===
tag_cards_in_deck("processed_deck_data.json", "tagged_deck_data.json")
