import streamlit as st
import openai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="The BioMatrix", layout="wide")

# Define scoring categories and preference types
categories = {
    "Strategic Fit": "high",
    "Market Potential": "high",
    "IP Position": "high",
    "Technical Feasibility": "high",
    "Development Cost": "low",
    "Time to Market": "low",
    "Regulatory Complexity": "low",
    "Synergies": "high",
    "ESG Impact": "high"
}

# Define keywords per category
keywords = {
    "Strategic Fit": ["aligned", "mission", "goals", "vision", "core"],
    "Market Potential": ["large market", "high demand", "scalable", "growth"],
    "IP Position": ["patent", "proprietary", "IP", "intellectual property"],
    "Technical Feasibility": ["prototype", "working", "tested", "pilot"],
    "Development Cost": ["low cost", "affordable", "minimal investment", "efficient"],
    "Time to Market": ["ready", "short timeline", "launch soon", "fast"],
    "Regulatory Complexity": ["approved", "compliant", "low regulation", "simple"],
    "Synergies": ["partner", "collaboration", "integration", "shared"],
    "ESG Impact": ["sustainable", "green", "carbon", "environmental", "social", "governance"]
}

# Scoring function
def score_category(text, category, preference):
    text = text.lower()
    count = sum(1 for kw in keywords[category] if kw in text)

    if preference == "high":
        if count >= 3:
            return 5.0, "Strong alignment based on multiple keyword matches."
        elif count == 2:
            return 4.0, "Good alignment based on key terms."
        elif count == 1:
            return 2.0, "Weak alignment with one keyword match."
        else:
            return 0.0, "No alignment found."
    else:
        if count >= 3:
            return 0.0, "High complexity or burden based on multiple terms."
        elif count == 2:
            return 2.0, "Moderate burden based on key terms."
        elif count == 1:
            return 4.0, "Low burden suggested by one keyword match."
        else:
            return 5.0, "No negative indicators found – likely low burden."

# --- UI ---
st.title("The BioMatrix v2.0")
st.subheader("Product Scoring System")

product_name = st.text_input("Product Name")
category_input = st.text_input("Category / Use Case (e.g., supplement, diagnostic, wearable)")
stage = st.selectbox("Stage of Development", ["Concept", "Prototype", "Preclinical", "Launched"])
tags = st.text_input("Tags / Keywords (optional)")
description = st.text_area("Detailed Description", height=250)

if st.button("Evaluate Product") and description.strip():
    st.markdown("##
