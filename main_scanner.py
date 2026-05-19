import time
import json
import os
from fetcher import find_ads_list
from blocket_api import BlocketAPI
from trust_score import calculate_trust

def start_continuous_scanner(query, avg_price):
    api = BlocketAPI()
    seen_ad_ids = set()

    # Create the 'data' folder if it doesn't already exist
    os.makedirs("data", exist_ok=True)

    # A list that saves all ads we have found
    saved_ads = []

    print(f"🚀 Starting monitoring for '{query}' every 30 seconds...")

    while True:
        try:
            results = api.search(query=query)
            ads_list = find_ads_list(results)

            new_ads_found = False # Keeps track of whether we should update the file

            for ad in ads_list:
                ad_id = ad.get("id")

                # If it is a COMPLETELY NEW ad we haven't seen before
                if ad_id and ad_id not in seen_ad_ids:
                    seen_ad_ids.add(ad_id)
                    heading = ad.get("heading", "Unknown title")

                    # Analyze the trustworthiness
                    score, reasons = calculate_trust(ad, avg_price)

                    # Save the score and the reasons inside the ad's data
                    ad['trust_score'] = score
                    ad['trust_reasons'] = reasons

                    # Add the ad to our "save-list"
                    saved_ads.append(ad)
                    new_ads_found = True


                    print(f"🚨 NEW AD: {heading} | Score: {score}/10")

            # If we found new ads, save the list to the json file!
            if new_ads_found:
                with open("data/live_ads.json", "w", encoding="utf-8") as f:
                    json.dump(saved_ads, f, indent=4, ensure_ascii=False)
                print("💾 Saved new data to Streamlit (live_ads.json)!")

            # Pause for 30 seconds
            time.sleep(30)

        except Exception as e:
            print(f"⚠️ An error occurred: {e}. Trying again in 30 seconds...")
            time.sleep(30)

if __name__ == "__main__":
    AVERAGE_IPHONE_13_PRICE = 5000
    start_continuous_scanner(query="iPhone 13", avg_price=AVERAGE_IPHONE_13_PRICE)