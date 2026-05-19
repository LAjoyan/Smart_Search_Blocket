# app.py
import streamlit as st
import json
import os

from streamlit_autorefresh import st_autorefresh

from notifier import notify_new_ad

# Konfigurera sidan
st.set_page_config(page_title="Smart Sök Blocket", page_icon="🛡️", layout="wide")

# Auto-refresh every 10s — picks up new ads written by main_scanner.py
st_autorefresh(interval=10_000, key="scanner_poll")

# ──────────────────────────────────────────────────────────────
# CSS för Blocket-stil (röd header, kort, badges, knappar)
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dölj Streamlits standard-header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Minska padding på toppen */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    /* Röd header-bar */
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

    /* Innehållsruta under header */
    .ss-body {
        background: #ffffff;
        padding: 20px 24px;
        border-radius: 0 0 12px 12px;
        border: 1px solid #e5e5e5;
        border-top: none;
        margin-bottom: 24px;
    }

    /* Grön Trovärdighet-knapp (badge) */
    .ss-trovardighet-wrap {
        display: flex;
        justify-content: flex-end;
        margin: 12px 0;
    }
    .ss-trovardighet {
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

    /* Trovärdighet-badges på annonskort */
    .badge-grön {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-gul {
        background: #fff3e0;
        color: #e65100;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-röd {
        background: #ffebee;
        color: #c62828;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
    }

    /* Sökruta - styla Streamlits input */
    .stTextInput > div > div > input {
        border: 1px solid #d0d0d0;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 14px;
    }

    /* Röd Sök-knapp */
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
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Röd header med sköld-logo
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="ss-header">
    <div class="ss-header-left">
        <div class="ss-logo">🛡️</div>
        <span class="ss-title">Smart Sökning</span>
    </div>
    <span class="ss-live">⚡ Live</span>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# Sökruta + Uppdatera-knapp
# ──────────────────────────────────────────────────────────────
col_sok, col_btn, col_refresh = st.columns([5, 1, 1])
with col_sok:
    sok_query = st.text_input(
        "Sök",
        value="",
        placeholder="Sök efter t.ex. iPhone 13, MacBook, cykel...",
        label_visibility="collapsed",
        key="sok_input"
    )
with col_btn:
    st.button("Sök", type="primary", use_container_width=True)
with col_refresh:
    if st.button("🔄", help="Uppdatera resultat", use_container_width=True):
        st.rerun()

# Grön Trovärdighet-indikator
st.markdown("""
<div class="ss-trovardighet-wrap">
    <span class="ss-trovardighet">🛡️ Sorterat efter trovärdighet</span>
</div>
""", unsafe_allow_html=True)

# Persistent banner for recently detected new ads (toasts are ephemeral)
if st.session_state.get("recent_new_ads"):
    with st.container(border=True):
        st.markdown("### 🔔 Senast hittade nya annonser")
        for entry in st.session_state["recent_new_ads"][-5:]:
            st.markdown(
                f"- **{entry['heading']}** · {entry['price']} SEK · "
                f"Trovärdighet: {entry['score']}/10 · "
                f"[Öppna]({entry['url']})"
            )

# ──────────────────────────────────────────────────────────────
# Ladda annonser från JSON
# ──────────────────────────────────────────────────────────────
DATA_FILE = "data/live_ads.json"


def filter_by_search(ads, query):
    """Filtrera annonser baserat på sökterm i titeln."""
    if not query.strip():
        return ads
    q = query.lower().strip()
    return [ad for ad in ads if q in ad.get("heading", "").lower()]


def render_score_badge(score):
    """Returnera HTML-badge baserat på trovärdighetspoäng."""
    if score >= 8:
        return f'<span class="badge-grön">{score}/10 🟢</span>'
    elif score >= 5:
        return f'<span class="badge-gul">{score}/10 🟡</span>'
    else:
        return f'<span class="badge-röd">{score}/10 🔴</span>'


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
                    price = price_data.get("amount") if isinstance(price_data, dict) else price_data
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

    # Filtrera på sökterm
    ads = filter_by_search(ads, sok_query)

    # Dela upp i trygga och misstänkta
    good_ads = [ad for ad in ads if ad.get('trust_score', 0) >= 5]
    suspicious_ads = [ad for ad in ads if ad.get('trust_score', 0) < 5]

    # Sortera trygga annonser efter trust_score (högst först)
    good_ads.sort(key=lambda x: x.get('trust_score', 0), reverse=True)

    # ── Misstänkta annonser ────────────────────────────────────
    if len(suspicious_ads) > 0:
        st.subheader("🚨 Varning: Misstänkta/Irrelevanta annonser")
        st.warning("Dessa annonser har fått lågt trovärdighetsindex på grund av orimliga priser, saknad information eller felaktig kategori.")

        for ad in suspicious_ads[:3]:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**[{ad.get('heading')}]({ad.get('canonical_url')})**")
                    price_data = ad.get("price")
                    price = price_data.get("amount") if isinstance(price_data, dict) else "Saknas"
                    st.write(f"Pris: {price} kr")

                    with st.expander("🔍 Varför är denna misstänkt?"):
                        for reason in ad.get('trust_reasons', []):
                            st.write(f"- {reason}")
                with col2:
                    score = ad.get('trust_score', 0)
                    st.markdown(render_score_badge(score), unsafe_allow_html=True)

        st.markdown("---")

    # ── Trygga annonser ────────────────────────────────────────
    st.subheader(f"✅ Relevanta & Trygga annonser ({len(good_ads)} st)")

    if len(good_ads) == 0 and sok_query.strip():
        st.info(f"Inga trygga annonser matchar '{sok_query}'. Prova ett annat sökord.")

    for ad in good_ads:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### [{ad.get('heading')}]({ad.get('canonical_url')})")
                price_data = ad.get("price")
                price = price_data.get("amount") if isinstance(price_data, dict) else "Saknas"
                st.write(f"**Pris:** {price} kr | **Plats:** {ad.get('location', 'Okänd')}")

                with st.expander("🔍 Visa trovärdighetsanalys"):
                    for reason in ad.get('trust_reasons', []):
                        st.write(f"- {reason}")

            with col2:
                score = ad.get('trust_score', 0)
                st.markdown(render_score_badge(score), unsafe_allow_html=True)

else:
    st.info("Väntar på att scannern ska hitta annonser... Kör din main_scanner.py i en annan terminal!")
