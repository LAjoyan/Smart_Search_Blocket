from statistics import median

from blocket_api import BlocketAPI, RecommerceAd

SCAM_KEYWORDS = [
    "swish first",
    "pay first",
    "abroad",
    "quick deal",
    "contact via email",
    "email only",
    "western union",
]


def extract_price(ad):
    """Get the numeric price from a Blocket ad. Returns 0 if missing."""
    price_data = ad.get("price")
    if not price_data:
        return 0
    if isinstance(price_data, dict):
        for key in ("amount", "value"):
            if key in price_data:
                return price_data[key]
    if isinstance(price_data, (int, float)):
        return price_data
    return 0


def calculate_trust(ad, avg_price, description=None):
    """
    Calculates a trust score 1-10 with reasons.
    `description` is optional — passing it enables a real description check
    (fetched separately via fetch_description).
    """
    score = 5
    reasons = []

    # 1. Price check
    price = extract_price(ad)
    if price == 0:
        score -= 2
        reasons.append("Missing price")
    elif avg_price > 0 and price < (avg_price * 0.4):
        score -= 3
        reasons.append(
            f"Unreasonably low price ({price} SEK vs avg {int(avg_price)} SEK)"
        )
    elif avg_price > 0:
        score += 1
        reasons.append("Reasonable price")

    # 2. Title check
    heading = ad.get("heading", "") or ""
    if len(heading) < 15:
        score -= 2
        reasons.append("Very short title")
    elif len(heading) > 40:
        score += 1
        reasons.append("Descriptive title")

    # 3. Description check (only when we have the full ad detail)
    if description is not None:
        if len(description) < 30:
            score -= 2
            reasons.append("Very short description")
        elif len(description) > 150:
            score += 1
            reasons.append("Detailed description")

    # 4. Scam keywords in title or description
    text = (heading + " " + (description or "")).lower()
    hits = [k for k in SCAM_KEYWORDS if k in text]
    if hits:
        score -= 3
        reasons.append(f"Suspicious keywords: {', '.join(hits)}")

    # 5. Images
    images = ad.get("image_urls") or []
    if len(images) == 0:
        score -= 3
        reasons.append("No images provided")
    elif len(images) >= 3:
        score += 2
        reasons.append("Multiple images provided")

    # 6. Location
    location = ad.get("location")
    if not location:
        score -= 1
        reasons.append("Missing location info")
    else:
        score += 1
        reasons.append(f"Location: {location}")

    # 7. Seller type
    is_company = bool(ad.get("organisation_name")) or "retailer" in (
        ad.get("flags") or []
    )
    if is_company:
        score += 1
        reasons.append("Company seller (verified business)")
    else:
        reasons.append("Private seller")

    score = max(1, min(10, score))
    return score, reasons


def fetch_description(ad_id):
    """Fetch the full description for one ad via the detail endpoint."""
    api = BlocketAPI()
    try:
        full = api.get_ad(RecommerceAd(id=int(ad_id)))
        return (
            full["loaderData"]["item-recommerce"]["itemData"].get("description") or ""
        )
    except Exception:
        return ""


def score_all(ads, deep_scan_count=3):
    """
    Score every ad from the search list. For the `deep_scan_count` lowest-scoring
    ads, fetch the full description and re-score with it for stronger evidence.
    Returns list of (score, ad, reasons) sorted ascending (most suspicious first).

    The price baseline uses the median, which is robust to outliers. Best results
    come from category-specific searches (search_car, search_mc, etc.) where the
    result set is homogeneous.
    """
    prices = [extract_price(a) for a in ads if extract_price(a) > 0]
    avg_price = median(prices) if prices else 0

    scored = [(calculate_trust(a, avg_price), a) for a in ads]
    scored = [(s, a, r) for ((s, r), a) in scored]
    scored.sort(key=lambda x: x[0])

    # Deep-scan the most suspicious to confirm with full description
    for i in range(min(deep_scan_count, len(scored))):
        _, ad, _ = scored[i]
        desc = fetch_description(ad.get("ad_id") or ad.get("id"))
        s, r = calculate_trust(ad, avg_price, description=desc)
        scored[i] = (s, ad, r)

    scored.sort(key=lambda x: x[0])
    return scored, avg_price


if __name__ == "__main__":
    import json

    with open("data/historical_ads.json", "r", encoding="utf-8") as f:
        ads = json.load(f)

    scored, avg = score_all(ads, deep_scan_count=3)
    print(f"Loaded {len(ads)} ads. Average price: {avg:.0f} SEK\n")

    print("=== 3 MOST SUSPICIOUS ADS (deep-scanned) ===")
    for s, ad, reasons in scored[:3]:
        print(f"\n[{s}/10] {ad.get('heading', '(no title)')}")
        print(f"  URL: {ad.get('canonical_url')}")
        for r in reasons:
            print(f"  - {r}")

    print("\n\n=== 3 MOST TRUSTED ADS ===")
    for s, ad, reasons in scored[-3:]:
        print(f"\n[{s}/10] {ad.get('heading', '(no title)')}")
        for r in reasons:
            print(f"  - {r}")
