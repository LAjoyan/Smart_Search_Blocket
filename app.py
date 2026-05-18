# app.py
import streamlit as st
import json
import os

# Konfigurera sidan
st.set_page_config(page_title="Smart Sök Blocket", page_icon="🚀", layout="wide")

st.title("🚀 Smart Sökning på Blocket")
st.markdown("Övervakar Blocket live efter relevanta och trygga annonser.")

# Låtsas att din main_scanner.py har sparat de bästa annonserna i denna fil
DATA_FILE = "data/live_ads.json"

# Knapp för att manuellt uppdatera sidan
if st.button("🔄 Uppdatera resultat"):
    st.rerun()

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        ads = json.load(f)

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