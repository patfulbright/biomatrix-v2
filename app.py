# BioMatrix 3.1 - Refined Scoring, Leaderboard Ranks, and Decimal Support

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from search_utils import search_web
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import re

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+psycopg://")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    category = Column(String(100))
    stage = Column(String(50))
    description = Column(Text)
    tags = Column(String(255))
    total_score = Column(String(10))
    explanation = Column(Text)

Base.metadata.create_all(bind=engine)

# UI Config
st.set_page_config(page_title="BioMatrix 3.1", layout="wide")
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
            color: #000000;
        }
        .main {
            background-color: #ffffff;
        }
        h1, h2, h3 {
            color: #004AAD;
            text-align: center;
        }
        .stButton>button {
            background-color: #004AAD;
            color: white;
            font-weight: bold;
        }
        .stTextInput>div>input {
            background-color: #f9f9f9;
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

st.title("BioMatrix 3.0")
st.subheader("⚙️ Product Scoring System")

# Input Form
with st.form("product_eval_form"):
    st.markdown("### 🧪 Enter Product Info")
    product_name = st.text_input("Product Name")
    category_input = st.text_input("Category / Use Case")
    stage = st.selectbox("Stage of Development", ["Concept", "Prototype", "Preclinical", "Launched"])
    tags = st.text_input("Tags / Keywords (optional)")
    description = st.text_area("Detailed Description", height=250)
    submitted = st.form_submit_button("Evaluate Product")

if submitted and description.strip():
    with st.spinner("Analyzing with AI..."):
        search_query = f"{product_name} {category_input} {tags} {description[:200]} biotechnology OR product OR innovation"
        try:
            search_results = search_web(search_query)
        except Exception as e:
            search_results = "No additional context found online."
            st.warning(f"Web search failed: {e}")

        gpt_prompt = f"""
You are evaluating a biotechnology or bioscience product for a venture firm. Score each of the 9 categories from 0.0 to 5.0 based on detailed sub-criteria, then total the result (max 45). Focus on bioscience relevance.

Categories and sub-criteria (each scored 0.0–5.0, but return just one decimal-rounded score per main category):

1. Strategic Fit
- Alignment with Org Goals
- Market Fit
- Operational Compatibility
- Resource Capability
- Risk & Regulatory Fit

2. Market Potential
- Market Size
- Competitive Landscape
- Customer Adoption
- Regulatory Environment
- Market Trends

3. IP Position
- IP Strength
- Freedom to Operate
- IP Growth Potential
- Licensing Ease
- IP Competition Landscape

4. Technical Feasibility
- Engineering Certainty
- Data Sufficiency
- Reg/Stakeholder Requirements
- Resources & Infrastructure
- Integration Complexity

5. Development Cost
- Scope Accuracy
- Technology Simplicity
- Team Fit
- Long-term Maintenance
- External Risk/Dependency

6. Time to Market
- Simplicity
- Resource Availability
- Regulatory Approval
- Integration Speed
- Vendor Support

7. Regulatory Complexity
- Emerging vs Mature Tech
- Compliance Burden
- Regulation Volatility
- Legal Risk
- Framework Clarity

8. Synergies
- Product or Tech Complementarity
- Cross-Team Value
- Process Fit
- Shared Resources
- Growth Alignment

9. ESG Impact
- Environmental Lifecycle
- Ethical Sourcing
- Privacy/Security
- Bias & Fairness
- Governance & Transparency

Product Details:
- Name: {product_name}
- Category: {category_input}
- Stage: {stage}
- Description: {description}
- Tags: {tags}

Context from web search:
{search_results}

Return scores like:
Strategic Fit: 4.2
...
Total Score: 38.7
Then briefly explain each score.
        """

        try:
            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a biotech company product scoring assistant."},
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.2
            )

            gpt_output = gpt_response.choices[0].message.content.strip()
            st.markdown("### ✅ GPT Evaluation Result")
            st.markdown(gpt_output)

            match = re.search(r"Total Score\s*[:\-]?\s*(\d+(\.\d+)?)", gpt_output)
            total_score = match.group(1) if match else "N/A"

            st.session_state["last_result"] = {
                "name": product_name,
                "category": category_input,
                "stage": stage,
                "description": description,
                "tags": tags,
                "total_score": total_score,
                "explanation": gpt_output
            }

        except Exception as e:
            st.error(f"Error during GPT evaluation: {e}")

# Save last result
if "last_result" in st.session_state:
    if st.button("💾 Save Last Evaluation"):
        try:
            db = SessionLocal()
            product = Product(**st.session_state["last_result"])
            db.add(product)
            db.commit()
            db.close()
            st.success("✅ Product saved to the database!")
            del st.session_state["last_result"]
        except Exception as e:
            st.error(f"Error saving to DB: {e}")

# Leaderboard
st.markdown("---")
st.header("📊 Product Leaderboard")

try:
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()

    if not products:
        st.info("No products found in the database.")
    else:
        df = pd.DataFrame([{
            "Rank": 0,  # Placeholder
            "Name": p.name,
            "Category": p.category,
            "Stage": p.stage,
            "Score": float(p.total_score) if p.total_score.replace('.', '', 1).isdigit() else 0,
            "Tags": p.tags,
            "Description": p.description,
            "Explanation": p.explanation
        } for p in products])

        filter_score = st.slider("Minimum Score to Display", min_value=0.0, max_value=45.0, value=0.0, step=0.1)
        df = df[df["Score"] >= filter_score]
        df = df.sort_values(by="Score", ascending=False).reset_index(drop=True)
        df["Rank"] = df.index + 1

        st.success(f"Loaded {len(df)} product(s) from the database.")
        st.dataframe(df.drop(columns=["Explanation"]), use_container_width=True)

        if st.download_button("⬇️ Download CSV", data=df.to_csv(index=False), file_name="biomatrix_leaderboard.csv"):
            st.toast("CSV downloaded")

        if st.checkbox("🔍 Show Full Explanations"):
            for _, row in df.iterrows():
                st.markdown(f"**{row['Name']}** — Score: {row['Score']}")
                st.markdown(row["Explanation"])
                st.markdown("---")

        with st.expander("🗑️ Delete a Product"):
            delete_rank = st.number_input("Enter Product Rank to Delete", min_value=1, step=1)
            if st.button("Delete Product"):
                if delete_rank <= len(df):
                    product_name = df.loc[delete_rank - 1, "Name"]
                    db = SessionLocal()
                    product_to_delete = db.query(Product).filter(Product.name == product_name).first()
                    if product_to_delete:
                        db.delete(product_to_delete)
                        db.commit()
                        st.success(f"✅ Product '{product_name}' deleted.")
                    else:
                        st.error(f"No product found.")
                    db.close()
                else:
                    st.error("Invalid rank.")

        with st.expander("⚠️ Reset Leaderboard"):
            confirm_reset = st.checkbox("Yes, I really want to delete ALL products.")
            if st.button("Reset Leaderboard") and confirm_reset:
                db = SessionLocal()
                db.query(Product).delete()
                db.commit()
                db.close()
                st.success("✅ Leaderboard has been reset.")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
