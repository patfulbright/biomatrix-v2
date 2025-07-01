# BioMatrix 3.0 - Enhanced Scoring with Subcategories & Interactive Explanations

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
import json

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
st.set_page_config(page_title="BioMatrix 3.0", layout="wide")
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
        Evaluate the product for a bioscience company using the following 9 criteria. For each main category, provide a 0–5 score (including decimals), then provide 5 subcategory scores (also 0–5) that justify the main score. Include a short explanation.

        Format:
        Strategic Fit: X.X (Explanation)
        - Sub1: X.X
        - Sub2: X.X
        ...
        (Repeat for all 9 categories)
        Total Score: SUM

        Criteria:
        - Strategic Fit
        - Market Potential
        - IP Position
        - Technical Feasibility
        - Development Cost
        - Time to Market
        - Regulatory Complexity
        - Synergies
        - ESG Impact

        Product Details:
        - Name: {product_name}
        - Category: {category_input}
        - Stage: {stage}
        - Description: {description}
        - Tags: {tags}

        Context from web search:
        {search_results}
        """

        try:
            gpt_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a biotech scoring assistant."},
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.0
            )

            gpt_output = gpt_response.choices[0].message.content.strip()
            st.markdown("### ✅ Evaluation Results!")
            st.markdown(gpt_output)

            total_match = re.search(r"Total Score\s*[:\-]?\s*(\d+(\.\d+)?)", gpt_output)
            total_score = total_match.group(1) if total_match else "N/A"

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
            "#": i+1,
            "Name": p.name,
            "Category": p.category,
            "Stage": p.stage,
            "Score": p.total_score,
            "Tags": p.tags,
            "Description": p.description,
            "Explanation": p.explanation
        } for i, p in enumerate(products)])

        filter_score = st.slider("Minimum Score to Display", min_value=0, max_value=45, value=0)
        df = df[df["Score"].apply(pd.to_numeric, errors='coerce') >= filter_score]
        df = df.sort_values(by="Score", ascending=False, key=pd.to_numeric)

        st.success(f"Loaded {len(df)} product(s) from the database.")
        st.dataframe(df.drop(columns=["Explanation", "Description"]), use_container_width=True)

        if st.checkbox("🔍 Show Full Explanations"):
            for _, row in df.iterrows():
                st.markdown(f"**{row['Name']}** - Score: {row['Score']}")
                main_blocks = re.split(r"\n(?=[A-Z][a-zA-Z\s]+:\s*\d)\n", row["Explanation"])
                for block in main_blocks:
                    lines = block.strip().split("\n")
                    if len(lines) >= 2:
                        header = lines[0]
                        with st.expander(header):
                            for line in lines[1:]:
                                st.markdown(f"- {line.strip()}")
                st.markdown("---")

        with st.expander("🗑️ Delete a Product"):
            delete_id = st.text_input("Enter Product Name to Delete")
            if st.button("Delete Product"):
                db = SessionLocal()
                product_to_delete = db.query(Product).filter(Product.name == delete_id).first()
                if product_to_delete:
                    db.delete(product_to_delete)
                    db.commit()
                    st.success(f"✅ Product '{delete_id}' deleted.")
                else:
                    st.error(f"No product found with name '{delete_id}'.")
                db.close()

        with st.expander("⚠️ Reset Leaderboard"):
            confirm_reset = st.checkbox("Yes, I really want to delete ALL products.")
            if st.button("Reset Leaderboard") and confirm_reset:
                db = SessionLocal()
                db.query(Product).delete()
                db.commit()
                db.close()
                st.success("✅ Leaderboard has been reset (all entries deleted).")

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
