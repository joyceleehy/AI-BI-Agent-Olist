import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from agent import run_agent

# Why this? Logs errors and info to terminal for debugging
# without crashing the user's UI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI E-Commerce Insights Agent",
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────
# SESSION STATE INIT
# Why this? Session state persists data between
# Streamlit reruns — used for analysis history
# ─────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ─────────────────────────────────────────
# HELPER: DETECT BEST CHART TYPE
# Why this? Different data shapes suit different
# chart types — auto-selecting makes the app smarter
# ─────────────────────────────────────────
def detect_best_chart(df: pd.DataFrame) -> str:
    """
    Analyses the DataFrame structure and returns
    the best chart type as a string.
    """
    if df is None or df.empty:
        return "none"

    # Identify column types
    numeric_cols = []
    date_cols = []
    text_cols = []

    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_cols.append(col)
            continue
        except (ValueError, TypeError):
            pass

        # Why this? Check if the column looks like a date
        if any(keyword in col.lower() for keyword in ["date", "month", "year", "timestamp", "time"]):
            date_cols.append(col)
        else:
            sample = str(df[col].iloc[0])
            is_uuid = len(sample) > 30 and all(
                c in "0123456789abcdef-" for c in sample.lower()
            )
            if not is_uuid:
                text_cols.append(col)

    if not numeric_cols:
        return "table"

    if len(df) == 1:
        return "table"

    # Why this order? Date → Line, Small categories → Pie, Others → Bar
    if date_cols:
        return "line"
    if text_cols and len(df) <= 6:
        return "pie"
    if text_cols:
        return "bar"

    return "table"

# ─────────────────────────────────────────
# HELPER: DISPLAY KPI CARDS
# Why this? KPI cards give stakeholders an instant
# at-a-glance summary before reading the full analysis
# ─────────────────────────────────────────
def display_kpis(df: pd.DataFrame):
    if df is None or df.empty:
        return

    rows = len(df)
    cols = len(df.columns)

    # Why this? Try to find revenue and average values
    # from numeric columns automatically
    numeric_cols = []
    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_cols.append(col)
        except (ValueError, TypeError):
            pass

    total_value = None
    avg_value = None
    value_col_name = None

    if numeric_cols:
        value_col = numeric_cols[0]
        value_col_name = value_col
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
        total_value = df[value_col].sum()
        avg_value = df[value_col].mean()

    # Why this? Build KPI columns dynamically based on available data
    kpi_cols = st.columns(4 if total_value is not None else 2)

    with kpi_cols[0]:
        st.metric(
            label="📋 Rows Returned",
            value=f"{rows:,}"
        )

    with kpi_cols[1]:
        st.metric(
            label="📊 Columns",
            value=f"{cols:,}"
        )

    if total_value is not None and len(kpi_cols) > 2:
        with kpi_cols[2]:
            st.metric(
                label=f"💰 Total ({value_col_name})",
                value=f"{total_value:,.2f}"
            )

    if avg_value is not None and len(kpi_cols) > 3:
        with kpi_cols[3]:
            st.metric(
                label=f"📈 Average ({value_col_name})",
                value=f"{avg_value:,.2f}"
            )

# ─────────────────────────────────────────
# HELPER: DISPLAY CHART
# Why this? Plotly gives interactive tooltips,
# better labels, and looks more professional
# than Streamlit's default bar_chart
# ─────────────────────────────────────────
def display_chart(df: pd.DataFrame):
    if df is None or df.empty:
        st.info("No data available to chart.")
        return

    chart_type = detect_best_chart(df)
    logger.info(f"Chart type selected: {chart_type}")

    # Identify columns
    numeric_cols = []
    label_col = None

    for col in df.columns:
        try:
            pd.to_numeric(df[col], errors="raise")
            numeric_cols.append(col)
        except (ValueError, TypeError):
            sample = str(df[col].iloc[0])
            is_uuid = len(sample) > 30 and all(
                c in "0123456789abcdef-" for c in sample.lower()
            )
            if not is_uuid and label_col is None:
                label_col = col

    if not numeric_cols:
        chart_type = "table"

    try:
        if chart_type == "bar" and label_col:
            value_col = numeric_cols[0]
            df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
            chart_df = (
                df.groupby(label_col)[value_col]
                .sum()
                .reset_index()
                .sort_values(value_col, ascending=False)
            )
            fig = px.bar(
                chart_df,
                x=label_col,
                y=value_col,
                title=f"{value_col} by {label_col}",
                labels={label_col: label_col.replace("_", " ").title(),
                        value_col: value_col.replace("_", " ").title()},
                color=value_col,
                color_continuous_scale="Blues",
                text_auto=".2s"
            )
            fig.update_layout(
                xaxis_tickangle=-35,
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "line" and label_col:
            value_col = numeric_cols[0]
            df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
            fig = px.line(
                df,
                x=label_col,
                y=value_col,
                title=f"{value_col} over {label_col}",
                labels={label_col: label_col.replace("_", " ").title(),
                        value_col: value_col.replace("_", " ").title()},
                markers=True
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "pie" and label_col:
            value_col = numeric_cols[0]
            df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
            fig = px.pie(
                df,
                names=label_col,
                values=value_col,
                title=f"{value_col} breakdown by {label_col}"
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            # Why this? Fallback — show the raw dataframe as a table
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        st.info("Chart could not be generated — showing raw data instead.")
        st.dataframe(df, use_container_width=True)

# ─────────────────────────────────────────
# HELPER: DISPLAY INSIGHTS
# Why this? Each section of the insight gets its own
# styled container so stakeholders can read at a glance
# ─────────────────────────────────────────
def display_insights(insight: str):
    # Why this? Split the full insight into named sections
    sections = {
        "1. Summary": None,
        "2. Key Findings": None,
        "3. Root Cause": None,
    }

    recommendation = None
    remaining = insight

    # Extract recommendation separately
    for marker in ["4. Recommendation", "4) Recommendation", "**4.", "4."]:
        if marker in remaining:
            parts = remaining.split(marker, 1)
            remaining = parts[0]
            recommendation = marker + parts[1].strip()
            break

    # Why this? Parse each section from the insight text
    section_keys = list(sections.keys())
    for i, key in enumerate(section_keys):
        if key in remaining:
            start = remaining.index(key) + len(key)
            end = len(remaining)
            for j in range(i + 1, len(section_keys)):
                if section_keys[j] in remaining:
                    end = remaining.index(section_keys[j])
                    break
            sections[key] = remaining[start:end].strip()

    # Why this? Different colours for different sections
    # helps stakeholders scan quickly
    if sections["1. Summary"]:
        st.subheader("📋 Summary")
        st.info(sections["1. Summary"])

    if sections["2. Key Findings"]:
        st.subheader("🔍 Key Findings")
        st.warning(sections["2. Key Findings"])

    if sections["3. Root Cause"]:
        st.subheader("🧠 Root Cause")
        with st.container(border=True):
            st.markdown(sections["3. Root Cause"])

    if recommendation:
        st.subheader("✅ Recommendation")
        st.success(recommendation)

# ─────────────────────────────────────────
# HELPER: DISPLAY FOLLOW-UP QUESTIONS
# Why this? Suggested questions guide stakeholders
# to dig deeper without needing to think of what to ask
# ─────────────────────────────────────────
def display_followup_questions(question: str):
    # Why this? Use the LLM to generate relevant follow-up
    # questions based on what the user just asked
    suggestions = [
        "Which product category contributes the most revenue?",
        "What is the monthly revenue trend?",
        "Which state has the highest number of orders?",
        "What is the most popular payment method?",
        "Which product category has the highest cancellation rate?"
    ]

    # Why this? Swap in more relevant suggestions based on keywords
    q_lower = question.lower()
    if "revenue" in q_lower or "sales" in q_lower:
        suggestions = [
            "Which state generates the most revenue?",
            "What is the monthly revenue trend in 2018?",
            "Which product category has the highest average order value?",
            "What percentage of revenue comes from each payment method?",
            "Which month had the highest total revenue?"
        ]
    elif "category" in q_lower or "product" in q_lower:
        suggestions = [
            "What is the total revenue for each product category?",
            "Which category has the most cancelled orders?",
            "What is the average order value per category?",
            "Which category has the most delivered orders?",
            "How many unique products exist per category?"
        ]
    elif "state" in q_lower or "region" in q_lower:
        suggestions = [
            "Which state has the most cancelled orders?",
            "What is the average order value per state?",
            "Which state has the highest revenue?",
            "How many customers are in each state?",
            "Which state has the fastest delivery time?"
        ]
    elif "payment" in q_lower:
        suggestions = [
            "What is the average payment value per payment type?",
            "Which payment method is used for highest value orders?",
            "How has payment method popularity changed over time?",
            "What percentage of orders use credit card?",
            "Which payment type has the most instalments?"
        ]

    st.subheader("💬 Suggested Follow-Up Questions")
    for s in suggestions:
        # Why this? Button for each suggestion so user can
        # click directly instead of retyping
        if st.button(f"➡️ {s}", key=s):
            st.session_state.followup = s
            st.rerun()

# ─────────────────────────────────────────
# SIDEBAR — ANALYSIS HISTORY
# Why this? Shows recent questions so users can
# track what they've already analysed
# ─────────────────────────────────────────
with st.sidebar:
    st.title("📚 Analysis History")
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-10:])):
            st.markdown(f"**{i+1}.** {item}")
    else:
        st.caption("No analyses yet. Ask your first question!")

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()

# ─────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────
st.title("🤖 AI E-Commerce Insights Agent")
st.markdown("Ask any business question about the Olist e-commerce dataset — get instant AI-powered insights.")
st.divider()

# ─────────────────────────────────────────
# QUESTION INPUT
# Why this? Check if a follow-up button was clicked
# and pre-fill the question input with it
# ─────────────────────────────────────────
default_question = st.session_state.get("followup", "")
if "followup" in st.session_state:
    del st.session_state.followup

question = st.text_input(
    label="💬 Ask a business question:",
    placeholder="e.g. What are the top 5 product categories by revenue?",
    value=default_question
)

with st.expander("💡 Not sure what to ask? Click here for examples"):
    st.markdown("""
    - What are the top 5 product categories by revenue?
    - Which state has the most customers?
    - What is the most popular payment method?
    - How many orders were delivered in 2018?
    - Which product category has the highest cancellation rate?
    - What is the average order value by product category?
    - What is the monthly revenue trend in 2018?
    """)

# ─────────────────────────────────────────
# ANALYSE BUTTON
# ─────────────────────────────────────────
if st.button("🔍 Analyse", type="primary"):
    if not question.strip():
        st.warning("Please type a question first!")
    else:
        with st.spinner("🤔 Agent is thinking..."):
            try:
                result = run_agent(question)
                logger.info(f"Agent returned result for: {question}")
            except Exception as e:
                logger.error(f"Agent failed: {e}")
                st.error(f"Something went wrong: {e}")
                st.stop()

        # Why this? Save to history after successful analysis
        st.session_state.history.append(question)

        df = result["dataframe"]

        # ── KPI CARDS ──
        st.divider()
        display_kpis(df)
        st.divider()

        # ── TWO COLUMN LAYOUT ──
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 Generated SQL Query")
            st.code(result["sql_query"], language="sql")

            st.subheader("📊 Data Summary")
            st.text(result["data_summary"])

            # Why this? Expandable raw data so it doesn't
            # clutter the main view but is available if needed
            if df is not None and not df.empty:
                with st.expander("🔎 View Raw Data"):
                    st.caption(f"Showing up to 20 rows — full shape: {df.shape[0]} rows × {df.shape[1]} columns")
                    st.dataframe(df.head(20), use_container_width=True)

        with col2:
            display_insights(result["insight"])

        # ── INTERACTIVE CHART (full width at bottom) ──
        st.divider()
        st.subheader("📈 Interactive Chart")
        if df is not None and not df.empty and "error" not in df.columns:
            display_chart(df)
        else:
            st.info("No chart available for this result.")

        # ── FOLLOW-UP QUESTIONS ──
        st.divider()
        display_followup_questions(question)

# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.divider()
st.caption("Built with Python · LangChain · Groq (Llama 3.1) · SQLite · Pandas · Plotly · Streamlit")