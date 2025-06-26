
import streamlit as st

st.set_page_config(page_title="The BioMatrix", layout="wide")

# Define scoring categories
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

def score_category(text, category, preference):
    text = text.lower()
    if preference == "high":
        if any(term in text for term in ["novel", "aligned", "large market", "patent", "advantage", "synergy", "sustainable"]):
            return 4.0, "Appears to align well based on key terms."
        elif any(term in text for term in ["moderate", "unclear", "developing", "neutral"]):
            return 2.0, "Moderate alignment or unclear relevance."
        else:
            return 0.0, "No strong evidence of alignment."
    else:
        if any(term in text for term in ["low", "minimal", "fast", "simple", "streamlined", "cheap"]):
            return 4.0, "Low cost/complexity based on description."
        elif any(term in text for term in ["moderate", "average", "somewhat complex"]):
            return 2.0, "Moderate burden or unclear."
        else:
            return 0.0, "High burden or no data."

st.title("The BioMatrix v2.0")
st.subheader("Product Scoring System")

description = st.text_area("Paste product description here:", height=200)

if st.button("Score Product") and description.strip():
    st.markdown("### Scoring Results")
    total_score = 0
    max_score = len(categories) * 5
    for cat, pref in categories.items():
        score, explanation = score_category(description, cat, pref)
        st.markdown(f"**{cat}**: {score:.1f} / 5")
        st.caption(f"Reason: {explanation}")
        total_score += score
    st.markdown("---")
    st.subheader(f"Total Score: {total_score:.1f} / {max_score} ({(total_score/max_score)*100:.1f}%)")
