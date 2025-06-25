import streamlit as st
import os
import json
from pathlib import Path

st.set_page_config(page_title="InImageAd - Back Office", layout="wide")
st.title("InImageAd - Back Office Dashboard")

# Path where metadata JSON files are stored
METADATA_DIR = Path("metadata")

# Ensure the metadata folder exists
if not METADATA_DIR.exists():
    st.warning("No metadata folder found. Upload and scan an image first.")
else:
    metadata_files = list(METADATA_DIR.glob("*.json"))
    st.subheader(f"🗂 {len(metadata_files)} Metadata Files Found")

    if metadata_files:
        selected_file = st.selectbox("Select a metadata file to view:", metadata_files)

        if selected_file:
            with open(selected_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            st.json(data)

            # Summary view
            st.markdown("### Summary")
            st.write(f"**Filename:** {data.get('file_name', 'N/A')}")
            st.write(f"**Detected Logos:** {[logo['description'] for logo in data.get('logos', [])]}")
            st.write(f"**AI Score:** {data.get('ai_detection', {}).get('score', 'Not Available')}")
            st.write(f"**Objects:** {[obj['name'] for obj in data.get('objects', [])]}")

            # Download button
            st.download_button(
                label="Download metadata JSON",
                data=json.dumps(data, indent=2),
                file_name=selected_file.name,
                mime="application/json"
            )
    else:
        st.info("No metadata files found yet. Upload and process an image first.")
