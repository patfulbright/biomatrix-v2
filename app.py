# BioMatrix 3.0 - Stable Version with Consistent Output and Fixed Formatting

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
        Evaluate the following biotechnology product for internal development using these 9 criteria. Your role is to determine whether a scientific product or IP should be developed internally. 
        Each criterion should be scored on a 0–5 decimal scale and include the five sub-category scores and explanations.

        Use this output format for every product:
        
        1. [Criterion] (Score: X.X)
        - [Subcategory 1] (X.X): Explanation
        - [Subcategory 2] (X.X): Explanation
        - [Subcategory 3] (X.X): Explanation
        - [Subcategory 4] (X.X): Explanation
        - [Subcategory 5] (X.X): Explanation

        Repeat this for all 9 criteria. Then at the end, 3-5 sentence summary explaining whether this product should be developed internally or not and why:
        "Total Score: X.X / 45.0"

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
                    {"role": "system", "content": "You are an expert bioscience analyst scoring internal products for development."},
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.1
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

# Save last result and refresh leaderboard
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
            "Rank": idx + 1,
            "Name": p.name,
            "Category": p.category,
            "Stage": p.stage,
            "Score": p.total_score,
            "Tags": p.tags,
            "Description": p.description,
            "Explanation": p.explanation
        } for idx, p in enumerate(sorted(products, key=lambda x: float(x.total_score if x.total_score != "N/A" else 0), reverse=True))])

        filter_score = st.slider("Minimum Score to Display", min_value=0, max_value=45, value=0)
        df = df[df["Score"].apply(pd.to_numeric, errors='coerce') >= filter_score]

        st.success(f"Loaded {len(df)} product(s) from the database.")
        st.dataframe(df.drop(columns=["Explanation"]), use_container_width=True)

        if st.download_button("⬇️ Download CSV", data=df.to_csv(index=False), file_name="biomatrix_leaderboard.csv"):
            st.toast("CSV downloaded")

        if st.checkbox("🔍 Show Full Explanations"):
            for _, row in df.iterrows():
                with st.expander(f"{row['Name']} - Score: {row['Score']}"):
                    st.markdown("### Show Criteria Results")
                    st.markdown(row["Explanation"])
                    st.markdown("---")

        # Delete a specific product
        with st.expander("🗑️ Delete a Product"):
            delete_id = st.number_input("Enter Product ID to Delete", min_value=1, step=1)
            if st.button("Delete Product"):
                db = SessionLocal()
                product_to_delete = db.query(Product).filter(Product.id == delete_id).first()
                if product_to_delete:
                    db.delete(product_to_delete)
                    db.commit()
                    st.success(f"✅ Product with ID {delete_id} deleted.")
                else:
                    st.error(f"No product found with ID {delete_id}.")
                db.close()

        # Reset entire leaderboard
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
