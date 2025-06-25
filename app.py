import streamlit as st
import os
from google.cloud import vision

# --- Secure Credentials Handling ---
# In production, set this in your environment, or use st.secrets if deploying to Streamlit Cloud.
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["gcp_service_account"] # Uncomment for Streamlit Cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "inlaid-vehicle-463914-q9-e409a6fb6f0a.json"  # For local dev

# --- Helper: Brand URL Mapping ---
BRAND_LINKS = {
    "Audi": "https://www.audi.co.uk/",
    "Nike": "https://www.nike.com/gb",
    "McDonald's": "https://www.mcdonalds.com/gb/en-gb.html",
    "Apple": "https://www.apple.com/uk/",
    "Maxell": "https://www.maxell.eu.com/",
    "Bank of America": "https://www.bankofamerica.com/"
}

# --- Streamlit App UI ---
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform")
st.sidebar.header("Instructions")
st.sidebar.markdown(
    """
    - Upload one or more images (jpg, jpeg, png).
    - The app will detect known brand logos.
    - Click any provided brand link for more information.
    """
)

uploaded_files = st.file_uploader(
    "Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

# --- Google Vision Client (outside loop for efficiency) ---
try:
    client = vision.ImageAnnotatorClient()
except Exception as e:
    st.error("Failed to initialize Google Vision Client. Check your credentials.")
    st.stop()

# --- Main Processing Loop ---
if uploaded_files:
    for idx, uploaded_file in enumerate(uploaded_files, 1):
        st.write(f"### Image {idx}")
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        image_bytes = uploaded_file.read()
        image = vision.Image(content=image_bytes)

        # Detect logos with error handling
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
        except Exception as ex:
            st.error(f"Logo detection failed: {ex}")
            continue

        st.write("#### Detected Logos:")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                hyperlink = BRAND_LINKS.get(brand, None)

                st.markdown(f"**{brand}** — {score}% confidence")
                if hyperlink:
                    st.markdown(f"[Visit Brand Site]({hyperlink})")
                else:
                    st.write("No link mapped")
                st.write("---")
        else:
            st.info("No logos detected.")

        # Optional: Draw bounding boxes (requires PIL and more code)
        # If you want this, let me know!

# --- Footer or Debug ---
st.caption("Powered by Google Cloud Vision & Streamlit | © 2025 InImageAd")