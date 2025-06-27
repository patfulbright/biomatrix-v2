import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from search_utils import search_web  # Web search integration

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="The BioMatrix", layout="wide")

# --- UI ---
st.title("The BioMatrix v2.0")
st.subheader("Product Scoring System")

product_name = st.text_input("Product Name")
category_input = st.text_input("Category / Use Case (e.g., supplement, diagnostic, wearable)")
stage = st.selectbox("Stage of Development", ["Concept", "Prototype", "Preclinical", "Launched"])
tags = st.text_input("Tags / Keywords (optional)")
description = st.text_area("Detailed Description", height=250)

if st.button("Evaluate Product", key="gpt_eval_button") and description.strip():
    with st.spinner("🧠 Evaluating..."):
        # Enhanced search query
        search_query = f"{product_name} {category_input} {tags} {description[:200]} biotechnology OR product OR innovation"

        try:
            search_results = search_web(search_query)
        except Exception as e:
            search_results = "Search failed or returned no usable results."
            st.warning(f"Web search failed: {e}")

        # Show web search results in expandable section
        with st.expander("🔍 View Web Search Snippets (Optional)"):
            st.text_area("Search Results", search_results, height=150)

        # Build GPT prompt
        gpt_prompt = f"""
        Evaluate the product using the following 9 criteria. For each, assign a score from 0 to 5 and provide a short explanation based on the scoring guidance below.

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
        - Provide a 1–2 sentence explanation per category.
        - At the end, calculate the total score out of 45.

        Product Details:
        - Name: {product_name}
        - Category: {category_input}
        - Stage: {stage}
        - Description: {description}
        - Tags: {tags}

        Additional Context (from web search):
        {search_results}
        """

        try:
            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a product evaluation assistant for a biotech incubator. Score products using a 9-part framework with guidance provided."
                    },
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.2
            )

            gpt_output = gpt_response.choices[0].message.content.strip()

            st.markdown("### ✅ Results")
            if gpt_output:
                st.markdown(gpt_output)
            else:
                st.warning("GPT responded, but returned no content.")
                st.json(gpt_response)

        except Exception as e:
            st.error(f"Error during GPT evaluation: {e}")
