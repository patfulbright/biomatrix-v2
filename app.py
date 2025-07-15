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
You work for Strike BioTech, a biotechnology company focused on developing and commercializing products that involve biologically-driven innovation, including engineered microbes, molecular delivery systems, and natural compound therapeutics.

You are evaluating whether a potential product is strategically aligned with Strike BioTech’s mission, capabilities, and goals. This includes assessing how biologically relevant the product is, whether it falls within or adjacent to core biotech domains, and how well it fits our R&D, regulatory, and commercialization infrastructure.

You are not deciding whether to build the product — you are scoring its strategic and technical fit based on our biotech company’s perspective.
You are a research analyst for a biotechnology company.

Your task is to evaluate each specified product across the nine stated categories. Each category must be rated with a value from 1.0 (no favorable) to 5.0 (very favorable).

Scoring should be rigorous and based on evidence, domain knowledge, and light research when necessary.

You must internally consider the five sub-criteria within each category to help contribute to the overall evaluation and each of these much be governed by the fact that our company is strategically as biotechnology company.

Important rules:
- Return exactly **one score per category** from 1.0 (poor) to 5.0 (excellent) and anywhere in between.
- Show subcategory scores for viewing perposes only (1.0-5.0)
- Each subcategory should vary in score depending on the products fit to the category. 
- If data is unclear, reflect that with a more cautious score (e.g. 3.0 or lower).
- Make meaningful distinctions backed by justified reasons.
        "Total Score: X.X / 45.0"

        Use this exact output format for every product:
        
        1. [Criterion] (Score: X.X)
        - [Subcategory 1] (Score: X.X): Explanation
        - [Subcategory 2] (Score: X.X): Explanation
        - [Subcategory 3] (Score: X.X): Explanation
        - [Subcategory 4] (Score: X.X): Explanation
        - [Subcategory 5] (Score: X.X): Explanation

You must evaluate the following categories. Each criterion contains five subcategory that include explanatory guidance. Use these parameters to justify your scoring.

**Strategic Fit considerations:**
1. Alignment with Organizational Goals – Does the technology support the company’s long-term mission, vision, and strategic objectives; will it enhance core competencies or contribute to competitive advantage?
2. Market and Customer Alignment – Does the technology address current and future market needs; will it help meet customer demands, improve satisfaction, or open new market segments?
3. Operational Compatibility – Can the technology integrate effectively with existing processes, systems, and infrastructure, requiring minimal workflow or infrastructure changes?
4. Resource Availability and Capability – Does the organization have or can it acquire the necessary skills, talent, and financial resources to implement and sustain the technology?
5. Risk and Regulatory Considerations – Are there minimal risks related to adoption, security, compliance, or IP? Does it align with industry standards and legal frameworks?

**Market Potential considerations:**
1. Market Size and Growth Potential – Does the overall size of the target market and its projected growth rate justify this product as a key opportunity?
2. Competitive Landscape – How significant is competition? Are market share, competitor strengths/weaknesses favorable for adoption?
3. Customer Acceptance and Adoption – Are target customers likely to adopt the technology easily or is adoption slow and difficult?
4. Regulatory and Legal Environment – Are there major regulations or legal risks that could limit market entry?
5. Market Trends and Industry Shifts – Are there emerging macro trends that make this product more viable in the near future?

**IP Position considerations:**
1. Strength and Enforceability of IP Rights – Is there strong existing IP (e.g. patents, trade secrets)?
2. Freedom-to-Operate (FTO) – Are there likely IP conflicts or does the product have a clear FTO path?
3. Potential for IP Generation and Protection – Can further innovation during development generate additional protectable IP?
4. IP Licensing and Acquisition – Are barriers to acquiring or licensing necessary IP minimal?
5. IP Landscape and Competitive Environment – What is the strength of competitors’ IP in this space?

**Technical Feasibility considerations:**
1. Uncertainty and Complexity – Are technical systems well understood and predictable or highly uncertain?
2. Limited Data and Information – Is there sufficient data to evaluate feasibility, or are assumptions speculative?
3. Evolving Requirements – Will regulatory expectations or stakeholder inputs affect technical development positively?
4. Resource Constraints – Do we have the necessary engineering and infrastructure, or will we need major partnerships?
5. Integration with Existing Systems – Can the technology smoothly plug into existing infrastructure and workflows?

**Development Cost considerations:**
1. Scope and Complexity – Does the scope require significant dev time or resources?
2. Technology Choice – Does the technology require high specialization or is it relatively standard?
3. Team Expertise and Size – Can a reasonably sized team deliver this, or will it require scaling up substantially?
4. Ongoing Maintenance and Support – Are there high recurring costs or special support burdens post-launch?
5. External Dependencies and Risks – Do costs depend on third parties, vendors, or licenses that introduce volatility?

**Time to Market considerations:**
1. Development Complexity – How complex is the engineering and implementation timeline?
2. Resource Availability – Are the people, funds, and tools readily accessible?
3. Regulatory Requirements & Compliance – Will approval cycles be fast or burdensome?
4. Integration with Existing Systems – How quickly can it be implemented into current infrastructure?
5. Vendor Support and Expertise – Is external help readily available to accelerate development?

**Regulatory Complexity considerations:**
1. Uncertainty and Lack of Clarity – Is this an emerging, poorly regulated area?
2. Compliance Costs and Burdens – Are costs for audits, legal reviews, and testing high?
3. Potential for Changes to Existing Regulations – Would implementation require rewriting SOPs and compliance manuals?
4. Liability and Risk – Does this introduce legal risk due to poor precedent or novel science?
5. Lack of Standardized Frameworks – Is the regulatory landscape fragmented across jurisdictions?

**Synergy considerations:**
1. Complementarity of Capabilities – Does this add leverage to our current systems/products?
2. Cross-Functional Benefits – Will multiple teams gain value from this tech?
3. Process Integration Potential – Will this fit easily into our ops?
4. Shared Resource Optimization – Does this improve utilization of people, infrastructure, or data?
5. Scalability and Future Growth Alignment – Can it scale with us and amplify future tech?

**ESG considerations:**
1. Environmental Footprint of the Technology Lifecycle – Is this tech environmentally sustainable across its life cycle?
2. Labor Practices and Supply Chain Sustainability – Are materials and labor sourced ethically and responsibly?
3. Data Privacy and Security – Will this protect user data and adhere to high security standards?
4. Bias and Fairness – Will development avoid harmful bias and promote equity?
5. Ethical Governance and Transparency – Is there transparency and accountability in the design and use of this product?

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
                temperature=0.0
            )

            gpt_output = gpt_response.choices[0].message.content.strip()
            st.markdown("### ✅ Evaluation Results!")
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
                    st.markdown("### Criteria Results")
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
