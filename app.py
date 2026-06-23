import streamlit as st
import pandas as pd
from agent import run_agent

st.set_page_config(
    page_title="AI E-Commerce Insights Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI E-Commerce Insights Agent")
st.markdown("Ask any business question about the Olist e-commerce dataset — get instant AI-powered insights.")

st.divider()

question = st.text_input(
    label="💬 Ask a business question:",
    placeholder="e.g. What are the top 5 product categories by revenue?"
)

with st.expander("💡 Not sure what to ask? Click here for examples"):
    st.markdown("""
    - What are the top 5 product categories by revenue?
    - Which state has the most customers?
    - What is the most popular payment method?
    - How many orders were delivered in 2018?
    - Which product category has the highest cancellation rate?
    - What is the average order value by product category?
    """)

if st.button("🔍 Analyse", type="primary"):

    if not question.strip():
        st.warning("Please type a question first!")
    else:
        with st.spinner("🤔 Agent is thinking..."):
            result = run_agent(question)

        full_insight = result["insight"]
        recommendation_text = ""
        main_insight_text = full_insight

        for marker in ["4. Recommendation", "4) Recommendation", "**4.", "4."]:
            if marker in full_insight:
                parts = full_insight.split(marker, 1)
                main_insight_text = parts[0].strip()
                recommendation_text = marker + parts[1].strip()
                break

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Generated SQL Query")
            st.code(result["sql_query"], language="sql")

            st.subheader("📊 Data Summary")
            st.text(result["data_summary"])

            # Why this? Build the chart using a smarter column detection
            df = result["dataframe"]
            if df is not None and not df.empty and "error" not in df.columns:

                # Why this? Identify which columns are numeric and which are labels
                # by actually trying to convert each column to float
                numeric_cols = []
                label_cols = []

                for col in df.columns:
                    try:
                        pd.to_numeric(df[col], errors="raise")
                        numeric_cols.append(col)
                    except (ValueError, TypeError):
                        label_cols.append(col)

                # Why this? Skip UUID columns — they're long hex strings
                # not useful as chart labels
                clean_label_cols = []
                for col in label_cols:
                    sample = str(df[col].iloc[0])
                    is_uuid = len(sample) > 30 and all(
                        c in "0123456789abcdef-" for c in sample.lower()
                    )
                    if not is_uuid:
                        clean_label_cols.append(col)

                if numeric_cols and clean_label_cols and len(df) > 1:
                    st.subheader("📈 Visual Chart")

                    # Why this? Use the best label column and
                    # group by it to handle duplicate category names
                    label_col = clean_label_cols[0]
                    value_col = numeric_cols[0]

                    # Why this? Convert to numeric explicitly
                    # in case pandas stored it as string
                    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

                    # Why this? Group by label and sum values
                    # handles cases where same category appears multiple times
                    chart_df = (
                        df.groupby(label_col)[value_col]
                        .sum()
                        .sort_values(ascending=False)
                    )

                    st.bar_chart(chart_df)

        with col2:
            st.subheader("💡 Business Insight")
            st.markdown(main_insight_text)

            if recommendation_text:
                st.subheader("✅ Recommendation")
                st.success(recommendation_text)

st.divider()
st.caption("Built with Python · LangChain · Groq (Llama 3.1) · SQLite · Pandas · Streamlit")