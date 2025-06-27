import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

if st.button("Evaluate Product", key="gpt_eval_button") and description.strip():
    st.markdown("### GPT Evaluation (Beta)")

    gpt_prompt = f"""
    Evaluate the product using the following 9 criteria. For each, assign a score from 0 to 5 and provide a short explanation based on the scoring guidance provided below.

    Scoring Guidance:
    - Strategic Fit: Alignment with company mission, long-term vision, and core competencies.
    - Market Potential: Size, CAGR, competitive differentiation, and unmet need.
    - IP Position: Strength of patents, freedom to operate, licensing barriers.
    - Technical Feasibility: Maturity of the science, proof-of-concept status, scalability.
    - Development Cost: Total projected investment required to bring to market.
    - Time to Market: Time needed for R&D, trials, approval, and launch.
    - Regulatory Complexity: Likelihood and burden of obtaining regulatory approval.
    - Synergies: Ability to leverage existing platforms, partnerships, infrastructure, people.
    - ESG Impact: Environmental, social, and governance value creation.

    Instructions:
    - Score each category from 0–5.
    - Provide a 1-2 sentence explanation per category.
    - At the end, calculate the total score out of 45.

    Product Details:
    - Name: {product_name}
    - Category: {category_input}
    - Stage: {stage}
    - Description: {description}
    - Tags: {tags}
    """

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product evaluation assistant for a biotech incubator. You score products using a structured 9-part framework based on defined guidance."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.2
        )

        gpt_output = gpt_response.choices[0].message.content.strip()

        if gpt_output:
            st.markdown(gpt_output)
        else:
            st.warning("GPT responded, but no content was returned.")
            st.json(gpt_response)

    except Exception as e:
        st.error(f"Error with GPT API: {e}")


# --- UI ---
st.title("The BioMatrix v2.0")
st.subheader("Product Scoring System")

product_name = st.text_input("Product Name")
category_input = st.text_input("Category / Use Case (e.g., supplement, diagnostic, wearable)")
stage = st.selectbox("Stage of Development", ["Concept", "Prototype", "Preclinical", "Launched"])
tags = st.text_input("Tags / Keywords (optional)")
description = st.text_area("Detailed Description", height=250)

if st.button("Evaluate Product") and description.strip():
    st.markdown("### GPT Evaluation (Beta)")

    gpt_prompt = f"""
    Based on the following product information, evaluate it using the internal scoring system for the categories: Strategic Fit, Market Potential, IP Position, and Technical Feasibility.
    For each category, output:
    1. A score from 0 to 5
    2. A short explanation for why that score was given.

    Product Details:
    - Name: {product_name}
    - Category: {category_input}
    - Stage: {stage}
    - Description: {description}
    - Tags: {tags}
    """

    try:
        gpt_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a product evaluation assistant for a biotech incubator."},
                {"role": "user", "content": gpt_prompt}
            ],
            temperature=0.2
        )

        gpt_output = gpt_response.choices[0].message.content.strip()

        if gpt_output:
            st.markdown(gpt_output)
        else:
            st.warning("GPT responded, but no content was returned.")
            st.json(gpt_response)

    except Exception as e:
        st.error(f"Error with GPT API: {e}")
