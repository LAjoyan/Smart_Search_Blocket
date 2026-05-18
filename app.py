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

    st.subheader(f"Hittade {len(ads)} nya annonser")

    # Skapa snygga kolumner
    for ad in ads:
        # Skapa en visuell box för varje annons
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"### [{ad.get('heading')}]({ad.get('canonical_url')})")

                # Visa priset säkert
                price_data = ad.get("price")
                price = price_data.get("amount") if isinstance(price_data, dict) else "Saknas"
                st.write(f"**Pris:** {price} kr | **Plats:** {ad.get('location', 'Okänd')}")

                # --- Expandern ligger inuti den ENDA col1 ---
                with st.expander("🔍 Visa trovärdighetsanalys"):
                    for reason in ad.get('trust_reasons', []):
                        st.write(f"- {reason}")
                # -----------------------

            with col2:
                # Visa trovärdighetspoängen stort
                score = ad.get('trust_score', 0)

                if score >= 8:
                    st.success(f"Trovärdighet: {score}/10 🟢")
                elif score >= 5:
                    st.warning(f"Trovärdighet: {score}/10 🟡")
                else:
                    st.error(f"Trovärdighet: {score}/10 🔴")

else:
    st.info("Väntar på att scannern ska hitta annonser... Kör din main_scanner.py i en annan terminal!")