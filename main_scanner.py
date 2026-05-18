import time
from fetcher import find_ads_list
from blocket_api import BlocketAPI      # 1. TA BORT # HÄR
from trust_score import calculate_trust

def start_continuous_scanner(query, avg_price):
    api = BlocketAPI()                  # 2. TA BORT # HÄR
    seen_ad_ids = set()

    print(f"🚀 Startar övervakning för '{query}' var 30:e sekund...")

    while True:
        try:
            # 3. TA BORT # PÅ DESSA TVÅ RADER:
            results = api.search(query=query)
            ads_list = find_ads_list(results)

            # 4. TA BORT ELLER KOMMENTERA UT DENNA:
            # ads_list = []

            # 2. Kolla igenom resultaten
            for ad in ads_list:
                ad_id = ad.get("id")
                # ... (resten av koden här under förblir samma)

                # Om det är en HELT NY annons vi inte sett förut
                if ad_id and ad_id not in seen_ad_ids:
                    seen_ad_ids.add(ad_id)
                    heading = ad.get("heading", "Okänd titel")

                    # 3. Analysera trovärdigheten (Kalla på er funktion från trust_score.py)
                    score, reasons = calculate_trust(ad, avg_price)

                    # 4. Terminal-notifiering!
                    print("\n" + "="*50)
                    print(f"🚨 NY ANNONS HITTAD! 🚨")
                    print(f"Titel: {heading}")
                    print(f"Länk: {ad.get('canonical_url', 'Ingen länk')}")
                    print(f"Trovärdighetsindex: {score}/10")
                    print(f"Analys:")
                    for reason in reasons:
                        print(f" - {reason}")
                    print("="*50 + "\n")

            # 5. Pausa i 30 sekunder
            time.sleep(30)

        except Exception as e:
            print(f"⚠️ Ett fel uppstod: {e}. Försöker igen om 30 sekunder...")
            time.sleep(30)

if __name__ == "__main__":
    # Ett påhittat snittpris baserat på vad ni kommit fram till i er EDA
    AVERAGE_IPHONE_13_PRICE = 5000
    start_continuous_scanner(query="iPhone 13", avg_price=AVERAGE_IPHONE_13_PRICE)