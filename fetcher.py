import json
import os
from blocket_api import BlocketAPI

def find_ads_list(data):
    """Söker igenom API-svaret (rekursivt) för att hitta listan med annonser."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 1. Kolla om listan ligger i vanliga nyckelord
        for key in ['data', 'items', 'ads', 'docs', 'search_results', 'hits']:
            if key in data and isinstance(data[key], list):
                print(f"-> Hittade listan under nyckeln: '{key}'")
                return data[key]

        # 2. Om inte, leta igenom alla nycklar för att se var det finns en lista
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"-> Hittade listan gömd under nyckeln: '{key}'")
                return value
            elif isinstance(value, dict):
                # Sök djupare om datan är nästlad
                deeper_list = find_ads_list(value)
                if deeper_list:
                    return deeper_list
    return []

def main():
    os.makedirs("data", exist_ok=True)
    api = BlocketAPI()

    print("Hämtar annonser för 'iPhone 13'...")
    try:
        results = api.search(query="iPhone 13")

        # Printa för att se hur API-svaret ser ut
        print(f"API-svaret är av typen: {type(results)}")
        if isinstance(results, dict):
            print(f"API-svarets översta nycklar: {list(results.keys())}")

        # Kör vår smarta detektiv-funktion!
        ads_list = find_ads_list(results)

        if not ads_list:
            print("Kunde inte hitta listan med annonser. Sparar rådatan istället.")
            ads_list = results
        else:
            print(f"✅ Perfekt! Hittade {len(ads_list)} riktiga annonser i datan.")

        # Spara ner till JSON
        file_path = "data/historical_ads.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ads_list, f, indent=4, ensure_ascii=False)

        print(f"✅ Sparade ner datan till {file_path}")

    except Exception as e:
        print(f"❌ Ett fel uppstod: {e}")

if __name__ == "__main__":
    main()