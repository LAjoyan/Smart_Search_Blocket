import streamlit as st
import json
import os

from streamlit_autorefresh import st_autorefresh

from notifier import notify_new_ad

# Configure the page

st.set_page_config(page_title="Smart Search Blocket", page_icon="🛡️", layout="wide")

# Auto-refresh every 10s — picks up new ads written by main_scanner.py
st_autorefresh(interval=10_000, key="scanner_poll")

# ──────────────────────────────────────────────────────────────
# CSS for Blocket style (red header, cards, badges, buttons)
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    /* Hide Streamlit's default header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Reduce top padding */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    /* Red header bar  */
    .ss-header {
        background: #ed6347;
        padding: 16px 24px;
        border-radius: 12px 12px 0 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0;
    }
    .ss-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .ss-logo {
        width: 40px;
        height: 40px;
        border: 2px solid #ffffff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 22px;
    }
    .ss-title {
        color: #ffffff;
        font-size: 20px;
        font-weight: 600;
    }
    .ss-live {
        color: #ffffff;
        font-size: 13px;
        background: rgba(255,255,255,0.2);
        padding: 4px 10px;
        border-radius: 12px;
    }

    /* Content box under header */
    .ss-body {
        background: #ffffff;
        padding: 20px 24px;
        border-radius: 0 0 12px 12px;
        border: 1px solid #e5e5e5;
        border-top: none;
        margin-bottom: 24px;
    }

    /* Green Trustworthiness button (badge) */
    .ss-trustworthiness-wrap {
        display: flex;
        justify-content: flex-end;
        margin: 12px 0;
    }
    .ss-trustworthiness {
        background: #2e7d32;
        color: #ffffff;
        padding: 8px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 7px;
    }

    /* Trustworthiness badges on ad cards */
    .badge-green {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-yellow {
        background: #fff3e0;
        color: #e65100;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-red {
        background: #ffebee;
        color: #c62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }

    /* Search box - style Streamlit's input */
    .stTextInput > div > div > input {
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 14px;
    }

    /* Red Search button */
    .stButton > button[kind="primary"] {
        background: #ed6347;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
    }
    .stButton > button[kind="primary"]:hover {
        background: #d94f33;
        color: white;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Red header with shield logo
# ──────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="ss-header">
    <div class="ss-header-left">
        <div class="ss-logo">🛡️</div>
        <span class="ss-title">Smart Search</span>
    </div>
    <span class="ss-live">⚡ Live</span>
</div>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────
# Search box + Refresh button
# ──────────────────────────────────────────────────────────────
col_search, col_btn, col_refresh = st.columns([5, 1, 1])
with col_search:
    search_query = st.text_input(
        "Search",
        value="",
        placeholder="Search for e.g. iPhone 13, MacBook, bike...",
        label_visibility="collapsed",
        key="search_input",
    )
with col_btn:
    st.button("Search", type="primary", use_container_width=True)
with col_refresh:
    if st.button("🔄", help="Refresh results", use_container_width=True):
        st.rerun()

# Green Trustworthiness indicator
st.markdown(
    """
<div class="ss-trustworthiness-wrap">
    <span class="ss-trustworthiness">🛡️ Sorted by Trustworthiness</span>
</div>
""",
    unsafe_allow_html=True,
)

# Persistent banner for recently detected new ads (toasts are ephemeral)
if st.session_state.get("recent_new_ads"):
    with st.container(border=True):
        st.markdown("### 🔔 Latest new ads found")
        for entry in st.session_state["recent_new_ads"][-5:]:
            st.markdown(
                f"- **{entry['heading']}** · {entry['price']} SEK · "
                f"Trustworthiness: {entry['score']}/10 · "
                f"[Open]({entry['url']})"
            )

# ──────────────────────────────────────────────────────────────
# # Load ads from JSON
# ──────────────────────────────────────────────────────────────
DATA_FILE = "data/live_ads.json"


def filter_by_search(ads, query):
    """Filter ads based on the search term in the title."""
    if not query.strip():
        return ads
    q = query.lower().strip()
    return [ad for ad in ads if q in ad.get("heading", "").lower()]


def render_score_badge(score):
    """Return HTML badge based on trustworthiness score."""
    if score >= 8:
        return f'<span class="badge-green">{score}/10 🟢</span>'
    elif score >= 5:
        return f'<span class="badge-yellow">{score}/10 🟡</span>'
    else:
        return f'<span class="badge-red">{score}/10 🔴</span>'


if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        ads = json.load(f)

    # --- New-ad detection: anything we haven't seen since the app started ---
    if "seen_ad_ids" not in st.session_state:
        st.session_state.seen_ad_ids = {ad.get("id") for ad in ads if ad.get("id")}
    else:
        current_ids = {ad.get("id") for ad in ads if ad.get("id")}
        new_ids = current_ids - st.session_state.seen_ad_ids
        if new_ids:
            if "recent_new_ads" not in st.session_state:
                st.session_state.recent_new_ads = []
            for ad in ads:
                if ad.get("id") in new_ids:
                    score = ad.get("trust_score", 0)
                    reasons = ad.get("trust_reasons", [])
                    price_data = ad.get("price") or {}
                    price = (
                        price_data.get("amount")
                        if isinstance(price_data, dict)
                        else price_data
                    )
                    st.toast(
                        f"🆕 New ad ({score}/10) — {ad.get('heading', '')[:60]}",
                        icon="🚨" if score < 5 else ("⚠️" if score < 8 else "✅"),
                    )
                    notify_new_ad(ad, score, reasons)
                    st.session_state.recent_new_ads.append(
                        {
                            "heading": ad.get("heading", "(no title)"),
                            "price": price or "—",
                            "score": score,
                            "url": ad.get("canonical_url", ""),
                        }
                    )
            st.session_state.seen_ad_ids = current_ids

    # Filter by search term
    ads = filter_by_search(ads, search_query)

    # Split into safe and suspicious
    good_ads = [ad for ad in ads if ad.get("trust_score", 0) >= 5]
    suspicious_ads = [ad for ad in ads if ad.get("trust_score", 0) < 5]

    # Sort safe ads by trust_score (highest first)
    good_ads.sort(key=lambda x: x.get("trust_score", 0), reverse=True)

    # ──  Suspicious ads  ────────────────────────────────────
    if len(suspicious_ads) > 0:
        st.subheader("🚨 Warning: Suspicious/Irrelevant ads")
        st.warning(
            "These ads received a low trustworthiness score because of unreasonable prices, missing information, or incorrect category."
        )

        for ad in suspicious_ads[:3]:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**[{ad.get('heading')}]({ad.get('canonical_url')})**")
                    price_data = ad.get("price")
                    price = (
                        price_data.get("amount")
                        if isinstance(price_data, dict)
                        else "Missing"
                    )
                    st.write(f"Price: {price} SEK")

                    with st.expander("🔍 Why is this suspicious?"):
                        for reason in ad.get("trust_reasons", []):
                            st.write(f"- {reason}")
                with col2:
                    score = ad.get("trust_score", 0)
                    st.markdown(render_score_badge(score), unsafe_allow_html=True)

        st.markdown("---")

    # ── Safe ads ────────────────────────────────────────
    st.subheader(f"✅ Relevant & Safe ads ({len(good_ads)} items)")

    if len(good_ads) == 0 and search_query.strip():
        st.info(f"No safe ads match '{search_query}'. Try another search term.")

    for ad in good_ads:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### [{ad.get('heading')}]({ad.get('canonical_url')})")
                price_data = ad.get("price")
                price = (
                    price_data.get("amount")
                    if isinstance(price_data, dict)
                    else "Missing"
                )
                st.write(
                    f"**Price:** {price} SEK | **Location:** {ad.get('location', 'Unknown')}"
                )

                with st.expander("🔍 Show trustworthiness analysis"):
                    for reason in ad.get("trust_reasons", []):
                        st.write(f"- {reason}")

            with col2:
                score = ad.get("trust_score", 0)
                st.markdown(render_score_badge(score), unsafe_allow_html=True)

else:
    st.info(
        "Waiting for the scanner to find ads... Run your main_scanner.py in another terminal!"
    )
