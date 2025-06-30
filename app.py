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

# Set up Streamlit
st.set_page_config(page_title="The BioMatrix", layout="wide")
st.title("The BioMatrix v3.0")
st.subheader("Product Scoring System (Now with DB!)")

# Set up SQLAlchemy
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

# Create the table if it doesn't exist
Base.metadata.create_all(bind=engine)

# --- UI Inputs ---
product_name = st.text_input("Product Name")
category_input = st.text_input("Category / Use Case (e.g., supplement, diagnostic, wearable)")
stage = st.selectbox("Stage of Development", ["Concept", "Prototype", "Preclinical", "Launched"])
tags = st.text_input("Tags / Keywords (optional)")
description = st.text_area("Detailed Description", height=250)

# GPT Evaluation
if st.button("Evaluate Product", key="gpt_eval_button") and description.strip():
    with st.spinner("🧠 Evaluating..."):
        search_query = f"{product_name} {category_input} {tags} {description[:200]} biotechnology OR product OR innovation"

        try:
            search_results = search_web(search_query)
        except Exception as e:
            search_results = "No additional context found online."
            st.warning(f"Web search failed: {e}")

        gpt_prompt = f"""
        Evaluate the product using the following 9 criteria. For each, assign a score from 0 to 5 and provide a short explanation based on the scoring guidance below.

        Scoring Guidance:
        - Strategic Fit
        - Market Potential
        - IP Position
        - Technical Feasibility
        - Development Cost
        - Time to Market
        - Regulatory Complexity
        - Synergies
        - ESG Impact

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
            st.markdown(gpt_output)

            match = re.search(r"Total Score\s*[:\-]?\s*(\d+)", gpt_output)
            total_score = match.group(1) if match else "N/A"

            # Store in session state
            st.session_state.last_result = {
                "name": product_name,
                "category": category_input,
                "stage": stage,
                "description": description,
                "tags": tags,
                "total_score": total_score,
                "explanation": gpt_output,
            }

        except Exception as e:
            st.error(f"Error during GPT evaluation: {e}")

# Save to DB (outside GPT block)
if st.session_state.get("last_result"):
    if st.button("💾 Save Last Evaluation"):
        try:
            db = SessionLocal()
            product = Product(**st.session_state.last_result)
            db.add(product)
            db.commit()
            db.close()
            st.success("✅ Product saved to the database!")
            del st.session_state["last_result"]
        except Exception as e:
            st.error(f"Error saving to DB: {e}")

# --- Leaderboard Section ---
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
            "Name": p.name,
            "Category": p.category,
            "Stage": p.stage,
            "Score": p.total_score,
            "Tags": p.tags,
            "Description": p.description,
            "Explanation": p.explanation
        } for p in products])
        df = df.sort_values(by="Score", ascending=False, key=pd.to_numeric)
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading leaderboard: {e}")
