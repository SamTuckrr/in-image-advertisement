
import streamlit as st
import os
import json
from collections import Counter

st.set_page_config(page_title="Brand Insights", layout="wide")
st.title("🔍 Brand Insights")

scan_dir = "."
json_files = [f for f in os.listdir(scan_dir) if f.endswith(".json")]
brands = []

for file in json_files:
    with open(os.path.join(scan_dir, file), "r") as f:
        data = json.load(f)
        brands += data.get("detected_logos", [])

if brands:
    count = Counter(brands)
    st.bar_chart(count)
    st.write("### Brand Frequency Table")
    st.dataframe(count.most_common())
else:
    st.info("No logos found in scan data.")
