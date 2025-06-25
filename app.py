import streamlit as st
import os
import json
import piexif
import tempfile
from google.cloud import vision
from google.oauth2 import service_account
from PIL import Image
from datetime import datetime

# Load GCP credentials from Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = vision.ImageAnnotatorClient(credentials=creds)

# Top 100 global brands and 50 car brands
BRAND_LINKS = {
    "Apple": "https://www.apple.com/",
    "Nike": "https://www.nike.com/",
    "Adidas": "https://www.adidas.com/",
    "Google": "https://www.google.com/",
    "Amazon": "https://www.amazon.com/",
    "Samsung": "https://www.samsung.com/",
    "Facebook": "https://www.facebook.com/",
    "Coca-Cola": "https://www.coca-cola.com/",
    "Pepsi": "https://www.pepsi.com/",
    "Microsoft": "https://www.microsoft.com/",
    "Tesla": "https://www.tesla.com/",
    "Sony": "https://www.sony.com/",
    "McDonald's": "https://www.mcdonalds.com/",
    "Starbucks": "https://www.starbucks.com/",
    "YouTube": "https://www.youtube.com/",
    "Netflix": "https://www.netflix.com/",
    "Uber": "https://www.uber.com/",
    "Airbnb": "https://www.airbnb.com/",
    "Lego": "https://www.lego.com/",
    "Intel": "https://www.intel.com/",
    "IBM": "https://www.ibm.com/",
    "Visa": "https://www.visa.com/",
    "MasterCard": "https://www.mastercard.com/",
    "Chanel": "https://www.chanel.com/",
    "Gucci": "https://www.gucci.com/",
    "Zara": "https://www.zara.com/",
    "H&M": "https://www.hm.com/",
    "BMW": "https://www.bmw.com/",
    "Mercedes-Benz": "https://www.mercedes-benz.com/",
    "Audi": "https://www.audi.com/",
    "Volkswagen": "https://www.vw.com/",
    "Toyota": "https://www.toyota.com/",
    "Honda": "https://www.honda.com/",
    "Ford": "https://www.ford.com/",
    "Chevrolet": "https://www.chevrolet.com/",
    "Kia": "https://www.kia.com/",
    "Hyundai": "https://www.hyundai.com/",
    "Lexus": "https://www.lexus.com/",
    "Jaguar": "https://www.jaguar.com/",
    "Land Rover": "https://www.landrover.com/",
    "Porsche": "https://www.porsche.com/",
    "Ferrari": "https://www.ferrari.com/",
    "Lamborghini": "https://www.lamborghini.com/",
    "Bugatti": "https://www.bugatti.com/",
    "Rolls-Royce": "https://www.rolls-roycemotorcars.com/",
    "Bentley": "https://www.bentleymotors.com/",
    "Mazda": "https://www.mazda.com/",
    "Mitsubishi": "https://www.mitsubishi.com/",
    "Subaru": "https://www.subaru.com/",
    "Jeep": "https://www.jeep.com/",
    "Nissan": "https://www.nissan.com/"
}

# App UI
st.set_page_config(page_title="InImageAd - Logo Detection", layout="centered")
st.title("InImageAd - Logo Detection Platform")

st.markdown("Upload image(s) to detect logos and extract metadata.")

uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Helper to extract EXIF metadata
def extract_exif_metadata(image_file):
    metadata = {}
    try:
        image = Image.open(image_file)
        exif_data = piexif.load(image.info.get('exif', b''))
        for ifd in exif_data:
            for tag in exif_data[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                metadata[tag_name] = exif_data[ifd][tag]
    except Exception as e:
        metadata["Error"] = f"Could not extract EXIF: {e}"
    return metadata

# Process each uploaded image
if uploaded_files:
    for uploaded_file in uploaded_files:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        bytes_data = uploaded_file.read()
        image = vision.Image(content=bytes_data)

        st.subheader("Detected Logos:")
        try:
            response = client.logo_detection(image=image)
            logos = response.logo_annotations
            if logos:
                for logo in logos:
                    brand = logo.description
                    score = round(logo.score * 100, 2)
                    st.write(f"**{brand}** — {score}% confidence")
                    link = BRAND_LINKS.get(brand)
                    if link:
                        st.markdown(f"[Brand Site]({link})")
                    else:
                        st.write("No link mapped")
            else:
                st.info("No logos detected.")
        except Exception as e:
            st.error(f"Logo detection failed: {e}")

        # Extract and save metadata
        metadata = extract_exif_metadata(uploaded_file)
        filename = uploaded_file.name + ".json"
        with open(filename, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        st.success(f"Metadata saved to `{filename}`")
