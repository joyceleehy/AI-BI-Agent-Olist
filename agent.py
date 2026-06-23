import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tools.sql_tool import run_sql_query
from tools.analysis_tool import analyze_dataframe

load_dotenv()

# Why this? Loads your Groq API key from .env so we never hardcode secrets
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Why this? This is the LLM we'll use for both SQL generation and insight writing
llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0  # Why 0? We want consistent, factual answers not creative ones
)

# Why this? We load the system prompt from a file so it's easy to edit later
def load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
    with open(prompt_path, "r") as f:
        return f.read()

# Why this? First LLM job — turn the user's question into a SQL query
def generate_sql(question: str, table_info: str) -> str:
    prompt = f"""You are a SQL expert. Given this database schema:
{table_info}

Write a single SQLite SELECT query to answer this question:
{question}

Rules:
- Return ONLY the raw SQL query, nothing else
- No markdown, no backticks, no explanation
- Only use tables that exist in the schema above
- NEVER select product_id, customer_id, or order_id in results
  unless the user explicitly asks for IDs
- Always use human readable columns like category names, state names, dates
- When asked about top products always group by product_category_name_english
  not by product_id
"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()

# Why this? Second LLM job — turn the data summary into a business insight
def generate_insight(question: str, data_summary: str) -> str:
    system_prompt = load_system_prompt()
    prompt = f"""The user asked: {question}

Here is the data analysis result:
{data_summary}

Please provide a structured business insight based on this data."""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    return response.content.strip()

# Why this? This is the main function that runs the full pipeline end to end
def run_agent(question: str) -> dict:

    # Why this? Schema description tells the LLM exactly what
    # tables and columns exist so it writes correct SQL
    table_info = """
Tables available:
- orders (order_id, customer_id, order_status, order_purchase_timestamp)
- customers (customer_id, customer_city, customer_state)
- order_items (order_id, product_id, price, freight_value)
- payments (order_id, payment_type, payment_value)
- products (product_id, product_category_name)
- category_translation (product_category_name, product_category_name_english)

Key rules:
- Revenue = SUM(order_items.price)
- Only count orders where order_status = 'delivered'
- For categories always join products to category_translation
- Dates are TEXT, use strftime('%Y-%m', order_purchase_timestamp) for month grouping
- IMPORTANT: This dataset contains data from 2016 to 2018 ONLY
- When the user asks about 'last month', 'recent', or 'latest', use 2018-08
- When the user asks about 'this year', interpret it as 2018
- Never query dates beyond 2018 as there is no data
- NEVER select product_id, customer_id, or order_id in results
  unless the user explicitly asks for IDs
- Always use human readable columns like category names, state names, dates
- When asked about 'top products' always group by product_category_name_english
  not by product_id
"""

    # Step 1: Generate SQL from the question
    sql_query = generate_sql(question, table_info)

    # Step 2: Run the SQL query
    df = run_sql_query(sql_query)

    # Step 3: Analyse the dataframe into a text summary
    data_summary = analyze_dataframe(df)

    # Step 4: Generate business insight
    insight = generate_insight(question, data_summary)

    return {
        "question": question,
        "sql_query": sql_query,
        "data_summary": data_summary,
        "insight": insight,
        "dataframe": df
    }