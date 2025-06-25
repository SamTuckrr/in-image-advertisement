
import streamlit as st
import os
import json

st.set_page_config(page_title="Back Office - Overview", layout="wide")
st.title("📂 Back Office - Scan Overview")

scan_dir = "."
json_files = [f for f in os.listdir(scan_dir) if f.endswith(".json")]

if not json_files:
    st.info("No scans found yet. Upload images from the main app.")
else:
    for file in json_files:
        st.subheader(file)
        with open(os.path.join(scan_dir, file), "r") as f:
            data = json.load(f)
        st.json(data)
