# app.py
import streamlit as st
import json
import os

from streamlit_autorefresh import st_autorefresh

from notifier import notify_new_ad

# Konfigurera sidan
st.set_page_config(page_title="Smart Sök Blocket", page_icon="🚀", layout="wide")

st.title("🚀 Smart Sökning på Blocket")
st.markdown("Övervakar Blocket live efter relevanta och trygga annonser.")

# Auto-refresh every 10s — picks up new ads written by main_scanner.py
st_autorefresh(interval=10_000, key="scanner_poll")

DATA_FILE = "data/live_ads.json"

col_a, col_b, col_c = st.columns([1, 1, 4])
with col_a:
    if st.button("🔄 Uppdatera resultat"):
        st.rerun()
with col_b:
    if st.button("🧪 Testa notifiering"):
        st.toast("🆕 Test — så här ser en ny annons ut!", icon="✅")
        notify_new_ad(
            {
                "heading": "TEST: iPhone 13 Pro Max 512GB",
                "price": {"amount": 4500},
                "location": "Stockholm",
                "canonical_url": "https://www.blocket.se",
            },
            score=9,
            reasons=["Test notification", "All systems working"],
        )

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

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        ads = json.load(f)

    # --- New-ad detection: anything we haven't seen since the app started ---
    if "seen_ad_ids" not in st.session_state:
        # First load — seed with everything currently in the file so we don't
        # spam toasts for ads that were already there when the user opened the app.
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
                    # In-app toast (bottom-right of browser) + native OS popup (top-right of screen)
                    st.toast(
                        f"🆕 New ad ({score}/10) — {ad.get('heading', '')[:60]}",
                        icon="🚨" if score < 5 else ("⚠️" if score < 8 else "✅"),
                    )
                    notify_new_ad(ad, score, reasons)
                    # Also persist to the banner so it doesn't vanish in 4s
                    st.session_state.recent_new_ads.append(
                        {
                            "heading": ad.get("heading", "(no title)"),
                            "price": price or "—",
                            "score": score,
                            "url": ad.get("canonical_url", ""),
                        }
                    )
            st.session_state.seen_ad_ids = current_ids

    # Filtrera annonserna baserat på er trovärdighetspoäng
    good_ads = [ad for ad in ads if ad.get('trust_score', 0) >= 5]
    suspicious_ads = [ad for ad in ads if ad.get('trust_score', 0) < 5]

    st.markdown("---")

    # KRAV 4: Visa misstänkta annonser (Minst 3)
    if len(suspicious_ads) > 0:
        st.subheader("🚨 Varning: Misstänkta/Irrelevanta annonser")
        st.warning("Dessa annonser har fått lågt trovärdighetsindex på grund av orimliga priser, saknad information eller felaktig kategori.")

        # Vi visar max de 3 sämsta för att uppfylla domarnas krav
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
                    st.error(f"Trovärdighet: {ad.get('trust_score', 0)}/10 🔴")

    st.markdown("---")

    # Visa de relevanta, bra annonserna
    st.subheader(f"✅ Relevanta & Trygga annonser ({len(good_ads)} st)")

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
                if score >= 8:
                    st.success(f"Trovärdighet: {score}/10 🟢")
                else:
                    st.warning(f"Trovärdighet: {score}/10 🟡")

else:
    st.info("Väntar på att scannern ska hitta annonser... Kör din main_scanner.py i en annan terminal!")