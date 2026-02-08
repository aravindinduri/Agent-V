import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv
from pdf2image import convert_from_path

from src.extractor import DeepSeekExtractor
from src.router import ClaimRouter

load_dotenv()

st.set_page_config(page_title="AI Claims Agent", page_icon="🛡️", layout="wide")

st.title("🛡️ Autonomous Insurance Claims Agent")
st.markdown("Upload an FNOL (First Notice of Loss) document to automatically extract data.")

# --- Sidebar ---
with st.sidebar:
    st.header("Status")
    if os.getenv("HF_API_TOKEN"):
        st.success("API Token Detected")
    else:
        st.error("Missing .env API Token")

# --- Main Logic ---
uploaded_file = st.file_uploader("Upload Claim Document", type=["pdf", "jpg", "png", "jpeg"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}")
    tfile.write(uploaded_file.read())
    temp_path = tfile.name

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Document Preview")
        if uploaded_file.name.lower().endswith('.pdf'):
            try:
                images = convert_from_path(temp_path, first_page=1, last_page=1)
                st.image(images[0], width="stretch") 
            except Exception as e:
                st.error(f"Error previewing PDF: {e}")
        else:
            st.image(uploaded_file, width="stretch")

    with col2:
        st.subheader("🤖 AI Analysis")
        
        with st.spinner("Extracting data & analyzing rules..."):
            try:
                extractor = DeepSeekExtractor()
                router = ClaimRouter()

                # Extract
                extracted_data = extractor.extract(temp_path)
                
                # Route
                decision = router.route(extracted_data)
                
                # --- Routing Display ---
                route = decision.recommendedRoute
                color = "#4CAF50" if route == "Fast-track" else \
                        "#FF9800" if route == "Manual Review" else \
                        "#F44336" if route == "Investigation Flag" else "#2196F3"

                st.markdown(f"""
                <div style="padding: 15px; border-radius: 8px; border: 2px solid {color}; text-align: center; margin-bottom: 20px;">
                    <h2 style="color: {color}; margin:0;">{route}</h2>
                    <p style="margin-top: 5px;">{decision.reasoning}</p>
                </div>
                """, unsafe_allow_html=True)

                # --- Data Display ---
                data_dict = decision.extractedFields
                                
                st.subheader("🔍 Extracted Data")
                st.json(data_dict)

                if decision.missingFields:
                    st.error(f"⚠️ Missing Fields: {', '.join(decision.missingFields)}")
                else:
                    st.success("✅ All mandatory fields present.")

            except Exception as e:
                st.error(f"Processing Failed: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)