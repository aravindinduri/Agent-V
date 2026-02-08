import streamlit as st
import os
import tempfile
import json
from dotenv import load_dotenv
from PIL import Image
from pdf2image import convert_from_path

from src.extractor import DeepSeekExtractor
from src.router import ClaimRouter

load_dotenv()

st.set_page_config(
    page_title="AI Claims Agent",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Autonomous Insurance Claims Agent")
st.markdown("Upload an FNOL (First Notice of Loss) document to automatically extract data and determine the claim workflow.")

with st.sidebar:
    st.header("Status")
    api_key = os.getenv("HF_API_TOKEN")
    if api_key:
        st.success("API Token Detected")
    else:
        st.error("Missing .env API Token")
        
    st.info("Supported formats: PDF, JPG, PNG")

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
                st.image(images[0], use_container_width=True)
            except Exception as e:
                st.error(f"Error previewing PDF: {e}")
        else:
            # It's an image
            st.image(uploaded_file, use_container_width=True)

    with col2:
        st.subheader("🤖 AI Analysis")
        
        with st.spinner("Extracting data & analyzing rules..."):
            try:
                # Initialize Agent
                extractor = DeepSeekExtractor()
                router = ClaimRouter()

                # Extract
                extracted_data = extractor.extract(temp_path)
                
                # Route
                decision = router.route(extracted_data)
                
                # --- Display Route Decision ---
                route = decision.recommendedRoute
                color = "gray"
                if route == "Fast-track": color = "green"
                elif route == "Manual Review": color = "orange"
                elif route == "Investigation Flag": color = "red"
                elif route == "Specialist Queue": color = "blue"

                st.markdown(f"""
                <div style="padding: 20px; border-radius: 10px; background-color: rgba(255, 255, 255, 0.1); border: 2px solid {color}; text-align: center;">
                    <h2 style="color: {color}; margin:0;">{route}</h2>
                    <p style="margin-top: 10px;">{decision.reasoning}</p>
                </div>
                """, unsafe_allow_html=True)

                st.divider()

                if decision.missingFields:
                    st.error(f"⚠️ Missing Fields: {', '.join(decision.missingFields)}")
                else:
                    st.success("✅ All mandatory fields present.")

                with st.expander("🔍 View Extracted Data (JSON)", expanded=True):
                    st.json(decision.extractedFields)

            except Exception as e:
                st.error(f"Processing Failed: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)