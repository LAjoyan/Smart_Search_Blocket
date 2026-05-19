import json
import os
from blocket_api import BlocketAPI


def find_ads_list(data):
    """Searches through the API response (recursively) to find the list of ads."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # 1. Check if the list is under common keywords
        for key in ["data", "items", "ads", "docs", "search_results", "hits"]:
            if key in data and isinstance(data[key], list):
                print(f"-> Found the list under the key: '{key}'")
                return data[key]

        # 2. If not, search through all keys to see where there is a list
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"-> Found the list hidden under the key: '{key}'")
                return value
            elif isinstance(value, dict):
                # Search deeper if the data is nested
                deeper_list = find_ads_list(value)
                if deeper_list:
                    return deeper_list
    return []


def main():
    os.makedirs("data", exist_ok=True)
    api = BlocketAPI()

    print("Fetching ads for 'iPhone 13'...")
    try:
        results = api.search(query="iPhone 13")

        # Print to see what the API response looks like
        print(f"The API response is of type: {type(results)}")
        if isinstance(results, dict):
            print(f"The API response's top-level keys: {list(results.keys())}")

        # Run our smart detective function!
        ads_list = find_ads_list(results)

        if not ads_list:
            print("Could not find the list of ads. Saving the raw data instead.")
            ads_list = results
        else:
            print(f"✅ Perfect! Found  {len(ads_list)} real ads in the data.")

        # Save to JSON
        file_path = "data/historical_ads.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(ads_list, f, indent=4, ensure_ascii=False)

        print(f"✅ Saved the data to {file_path}")

    except Exception as e:
        print(f"❌An error occurred:  {e}")


if __name__ == "__main__":
    main()
