import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
import io
import json
from PIL import Image

# --- Streamlit Page Setup ---
st.set_page_config(page_title="InImageAd", layout="wide")
st.title("InImageAd – Logo Detection & Brand Linking")

st.sidebar.header("Instructions")
st.sidebar.markdown(
    """
    - Upload one or more image files (jpg, jpeg, png)
    - Detected brand logos will be displayed with hyperlinks
    - Powered by Google Vision + your own brand metadata
    """
)

# --- Load Google Credentials ---
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# --- Load Brand Links ---
try:
    with open("brand_links_500.json", "r") as f:
        brand_links = json.load(f)
except Exception as e:
    st.warning("Brand link file could not be loaded.")
    brand_links = {}

# --- File Uploader ---
uploaded_files = st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, start=1):
        st.subheader(f"Image {idx}")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)

        content = uploaded_file.read()
        image_bytes = vision.Image(content=content)

        # --- Run logo detection ---
        response = client.logo_detection(image=image_bytes)
        logos = response.logo_annotations

        if logos:
            st.write("### Detected Logos:")
            for logo in logos:
                brand = logo.description
                confidence = round(logo.score * 100, 2)
                brand_key = brand.lower().replace(" ", "")
                url = brand_links.get(brand_key)

                st.markdown(f"- **{brand}** ({confidence}%)")

                if url:
                    st.markdown(f"  → [Visit {brand}]({url})")
                else:
                    st.markdown("  → No link available")

                st.write("---")
        else:
            st.info("No logos detected.")
