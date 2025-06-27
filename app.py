import streamlit as st

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
    else:  # for "low" preferred categories like cost/time/regulation
        if count >= 3:
            return 0.0, "High complexity or burden based on multiple terms."
        elif count == 2:
            return 2.0, "Moderate burden based on key terms."
        elif count == 1:
            return 4.0, "Low burden suggested by one keyword match."
        else:
            return 5.0, "No negative indicators found – likely low burden."

# UI
st.title("The BioMatrix v2.0")
st.subheader("Product Scoring System")

description = st.text_area("Paste product description here:", height=250)

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
    st.subheader(f"Total Score: {total_score:.1f} / {max_score} ({(total_score / max_score) * 100:.1f}%)")
