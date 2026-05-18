# trust_score.py

def extract_price(ad):
    """Helper function to get the price, handling dictionaries if needed."""
    # FIXME: Change "price" to whatever Blocket calls the price key!
    price_data = ad.get("price") 
    if not price_data:
        return 0
    if isinstance(price_data, dict) and "value" in price_data:
        return price_data["value"]
    if isinstance(price_data, (int, float)):
        return price_data
    return 0

def calculate_trust(ad, avg_price):
    """
    Calculates a trust score between 1 and 10.
    Returns: (score, list_of_reasons)
    """
    score = 5  # Start at a neutral 5
    reasons = []

    # 1. Price Check (Unreasonable price)
    price = extract_price(ad)
    if price == 0:
        score -= 2
        reasons.append("Missing price")
    elif avg_price > 0 and price < (avg_price * 0.4): # If price is 60% cheaper than average
        score -= 3
        reasons.append(f"Unreasonably low price ({price} SEK vs avg {avg_price} SEK)")
    elif avg_price > 0 and price >= (avg_price * 0.4):
        score += 1
        reasons.append("Reasonable price")

    # 2. Description Check (Very short description)
    # FIXME: Change "body" to what the description key is called (maybe "description"?)
    description = ad.get("body", "") 
    if len(description) < 30:
        score -= 2
        reasons.append("Very short or missing description")
    elif len(description) > 150:
        score += 1
        reasons.append("Detailed description")

# 3. Images Check (Missing images)
    # FIXME: Change "images" to the correct key
    images = ad.get("images", []) 
    if len(images) == 0:
        score -= 3
        reasons.append("No images provided")
    elif len(images) >= 3:
        score += 2
        reasons.append("Multiple images provided")

    # 4. Location Check (Missing location)
    # FIXME: Check how location is stored in your EDA
    location = ad.get("location") 
    if not location:
        score -= 1
        reasons.append("Missing location info")
    else:
        score += 1
        reasons.append("Location provided")

    # 5. Cap the score between 1 and 10
    score = max(1, min(10, score))
    
    return score, reasons

# --- TEST THE CODE ---
if __name__ == "__main__":
    # Create a fake ad to test if the math works
    fake_scam_ad = {
        "title": "iPhone 13 brand new!!!",
        "price": {"value": 1500},  # Super cheap
        "body": "buy fast",        # Super short
        "images": [],              # No images
        "location": None
    }
    
    average_iphone_price = 5000 # Use the average you found in EDA
    
    final_score, final_reasons = calculate_trust(fake_scam_ad, average_iphone_price)
    print(f"Scam Ad Score: {final_score}/10")
    print("Reasons:")
    for r in final_reasons:
        print(f" - {r}")