import streamlit as st
from google.cloud import vision
import os
import json
from PIL import Image, ExifTags
import uuid

# Set up Google Vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["gcp_service_account"]

BRAND_LINKS = {
    "Audi": "https://www.audi.co.uk/",
    "Nike": "https://www.nike.com/gb",
    "McDonald's": "https://www.mcdonalds.com/gb/en-gb.html",
    "Apple": "https://www.apple.com/uk/",
    "Maxell": "https://www.maxell.eu.com/",
    "Bank of America": "https://www.bankofamerica.com/",
    "Peroni Brewery": "https://www.peroniitaly.com/"
}

def get_exif_data(image):
    try:
        image = Image.open(image)
        exif_data = {}
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                exif_data[decoded] = value
        return exif_data
    except Exception:
        return {}

def detect_logos(image_bytes):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_bytes)
    response = client.logo_detection(image=image)
    return response.logo_annotations

def fake_scene_classification():
    return "urban outdoor", 0.88

def fake_ai_detection_score():
    return 0.42

def fake_safety_score():
    return 0.03

st.set_page_config(page_title="InImageAd - Scanner", layout="centered")
st.title("InImageAd - Logo & Metadata Scanner")

uploaded_files = st.file_uploader("Upload image(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for img in uploaded_files:
        st.image(img, caption="Uploaded Image", use_column_width=True)
        image_bytes = img.read()
        image_id = str(uuid.uuid4())
        metadata = {}

        # Logo Detection
        logos = detect_logos(image_bytes)
        metadata["logos"] = []
        st.subheader("Detected Logos:")
        if logos:
            for logo in logos:
                brand = logo.description
                score = round(logo.score * 100, 2)
                metadata["logos"].append({"brand": brand, "score": score})
                st.markdown(f"**{brand}** — {score}% confidence")
                link = BRAND_LINKS.get(brand)
                if link:
                    st.markdown(f"[Visit Brand Site]({link})")
                else:
                    st.write("No link mapped")
                st.write("---")
        else:
            st.write("No logos detected.")

        # EXIF
        exif = get_exif_data(img)
        metadata["exif"] = exif

        # Scene & AI scoring
        scene, scene_score = fake_scene_classification()
        ai_score = fake_ai_detection_score()
        safety_score = fake_safety_score()
        metadata.update({
            "scene_type": scene,
            "scene_confidence": scene_score,
            "ai_generated_score": ai_score,
            "safety_score": safety_score
        })

        # Save metadata
        json_name = f"{image_id}.jpeg.json"
        with open(os.path.join(base_path, json_name), "w") as f:
            json.dump(metadata, f, indent=2)
        st.success(f"Metadata saved to {json_name}")
