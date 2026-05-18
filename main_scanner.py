import time
import json
import os
from fetcher import find_ads_list
from blocket_api import BlocketAPI
from trust_score import calculate_trust

def start_continuous_scanner(query, avg_price):
    api = BlocketAPI()
    seen_ad_ids = set()

    # NYTT 1: Skapa mappen 'data' om den inte redan finns
    os.makedirs("data", exist_ok=True)

    # NYTT 2: En lista som sparar alla annonser vi har hittat
    saved_ads = []

    print(f"🚀 Startar övervakning för '{query}' var 30:e sekund...")

    while True:
        try:
            results = api.search(query=query)
            ads_list = find_ads_list(results)

            new_ads_found = False # Håller koll på om vi ska uppdatera filen

            for ad in ads_list:
                ad_id = ad.get("id")

                # Om det är en HELT NY annons vi inte sett förut
                if ad_id and ad_id not in seen_ad_ids:
                    seen_ad_ids.add(ad_id)
                    heading = ad.get("heading", "Okänd titel")

                    # Analysera trovärdigheten
                    score, reasons = calculate_trust(ad, avg_price)

                    # NYTT 3: Spara poängen och anledningarna inuti annonsens data
                    ad['trust_score'] = score
                    ad['trust_reasons'] = reasons

                    # Lägg till annonsen i vår "spar-lista"
                    saved_ads.append(ad)
                    new_ads_found = True

                    # Fortsätt printa i terminalen för säkerhets skull
                    print(f"🚨 NY ANNONS: {heading} | Poäng: {score}/10")

            # NYTT 4: Om vi hittade nya annonser, spara listan till json-filen!
            if new_ads_found:
                with open("data/live_ads.json", "w", encoding="utf-8") as f:
                    json.dump(saved_ads, f, indent=4, ensure_ascii=False)
                print("💾 Sparade ny data till Streamlit (live_ads.json)!")

            # Pausa i 30 sekunder
            time.sleep(30)

        except Exception as e:
            print(f"⚠️ Ett fel uppstod: {e}. Försöker igen om 30 sekunder...")
            time.sleep(30)

if __name__ == "__main__":
    AVERAGE_IPHONE_13_PRICE = 5000
    start_continuous_scanner(query="iPhone 13", avg_price=AVERAGE_IPHONE_13_PRICE)