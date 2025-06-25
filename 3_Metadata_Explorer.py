
import streamlit as st
import os
import json

st.set_page_config(page_title="Metadata Explorer", layout="wide")
st.title("📸 Metadata Explorer")

scan_dir = "."
json_files = [f for f in os.listdir(scan_dir) if f.endswith(".json")]

rows = []
for file in json_files:
    with open(os.path.join(scan_dir, file), "r") as f:
        data = json.load(f)
    row = {
        "Filename": data.get("filename"),
        "Brands": ", ".join(data.get("detected_logos", [])),
        "DateTime": data.get("exif", {}).get("DateTime", "N/A"),
        "Camera": data.get("exif", {}).get("Model", "Unknown")
    }
    rows.append(row)

if rows:
    st.dataframe(rows)
else:
    st.info("No EXIF metadata found.")
