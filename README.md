# Smart_Search_Blocket

# 🚀 Smart Search for Blocket (Hackathon Edition)

> ⚠️ **NOTE: This project was developed during a time-limited Hackathon. The code is a "Proof of Concept" (prototype) and is currently not 100% finished or optimized for production.**

## 📖 About the Project
This project is an intelligent search tool built on top of the Swedish classifieds platform, Blocket. Instead of a traditional search, this application acts as a smart assistant that automatically monitors, analyzes, and scores listings in real-time.

The goal is to help users save time, quickly find the most relevant listings, and warn against potential scams or "junk" listings (e.g., showing phone cases when searching for a smartphone).

## ✨ Main Features
The project fulfills the Hackathon challenge requirements through the following features:
* **🔍 Categorized Search:** Interactive search where the user can enter keywords and select a category directly in the terminal.
* **⏱️ Continuous Monitoring:** Scans the Blocket API every 30 seconds to immediately find newly published listings.
* **📊 Trust Score Index (1-10):** A custom algorithm that analyzes the price, title length, images, and seller type to give each listing a fair and logical score.
* **🚨 Suspicious Listing Warnings:** Automatically filters and flags listings with unreasonably low prices or missing information.
* **🌐 Interactive Web Interface:** A sleek and user-friendly frontend built with Streamlit that reads data in real-time from our file-based NoSQL database (`live_ads.json`).

## 🛠️ Tech Stack
* **Language:** Python 3.12
* **Frontend:** Streamlit
* **Database:** File-based JSON database (`Producer/Consumer` architecture)
* **Package Manager:** `uv`

