import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import time
import os
import requests

# -------------------------
# Dynamic Driver Download
# -------------------------
def ensure_chromedriver():
    driver_url = "https://github.com/Philomathic01/Keyword_scanner/raw/main/chromedriver.exe"
    driver_path = "chromedriver.exe"

    if not os.path.exists(driver_path):
        with st.spinner("Downloading ChromeDriver..."):
            response = requests.get(driver_url)
            with open(driver_path, "wb") as f:
                f.write(response.content)
    return driver_path

# -------------------------
# Scraper Class
# -------------------------
class Scraper:
    def __init__(self, url):
        self.url = url

    def run_scraper(self):
        driver_path = ensure_chromedriver()

        options = Options()
        options.add_argument("--headless")  # Headless for no browser pop-up
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        driver.get(self.url)
        time.sleep(2)  # Let the page load
        src = driver.page_source
        soup = bs(src, "html.parser")
        driver.quit()

        body = soup.find("body")
        self.body_text = body.get_text(separator=" ", strip=True) if body else ""

    def search_keywords(self, full_text, keywords):
        found = {}
        for word in keywords:
            count = len(re.findall(r'\b' + re.escape(word) + r'\b', full_text, re.IGNORECASE))
            if count > 0:
                found[word] = count
        return found

# ------------------------------
# Streamlit Interface
# ------------------------------
st.title("🕷️ Pharma Keyword Scanner (Body Only)")

url = st.text_input("Enter a website URL:", "https://www.fda.gov/")

if url and not url.startswith("http"):
    st.warning("Please enter a valid URL starting with 'http://' or 'https://'")

if st.button("Scrape Website"):
    scraper = Scraper(url)
    with st.spinner("Scraping in progress..."):
        scraper.run_scraper()

    # Keyword matching
    target_keywords = [
        "pharma", "drug", "compliance", "regulatory affairs", "research & development",
        "r&d", "oncology", "biotech", "api", "cmo", "cro", "formulation", "manufacturing",
        "medic", "vaccine", "genomic", "bioscience", "lifescience", "clinic",
        "drugs", "nutraceutical", "pharmacy", "supply"
    ]

    found_keywords = scraper.search_keywords(scraper.body_text, target_keywords)

    st.subheader("🔍 Keyword Highlights")
    if found_keywords:
        for word, count in found_keywords.items():
            st.markdown(f"✅ **`{word}`** found **{count} time(s)**")
    else:
        st.warning("No target keywords found in the page body.")

    # Save keyword hits
    keyword_df = pd.DataFrame(found_keywords.items(), columns=["Keyword", "Count"])
    st.download_button("🧪 Download Keyword Hits CSV", data=keyword_df.to_csv(index=False),
                       file_name="keyword_hits.csv", mime="text/csv")
