# 🤖 AI E-Commerce Insights Agent

An AI-powered business intelligence agent that transforms natural language questions into data-driven insights using SQL, Python, and LLM reasoning.

> **"Why did sales drop last month?"** — just ask, and the agent answers.

---

## 🎯 What It Does

Instead of manually writing SQL queries and analysing spreadsheets, stakeholders can simply type a business question in plain English and receive:

- ✅ Auto-generated SQL query
- ✅ Data pulled live from the database
- ✅ AI-written business insight (Summary → Key Findings → Root Cause → Recommendation)
- ✅ Interactive visualisation

---

## 🖥️ Demo

![App Screenshot](screenshots/demo.png)

**Example questions you can ask:**
- *"What are the top 5 product categories by revenue?"*
- *"Which state has the most customers?"*
- *"What is the most popular payment method?"*
- *"What is the monthly revenue trend in 2018?"*
- *"Which product category has the highest cancellation rate?"*

---

## 🏗️ Architecture

```
User Question (Natural Language)
        ↓
Streamlit UI (app.py)
        ↓
AI Agent (agent.py)
        ↓
┌─────────────────────────────┐
│  LLM #1: Generate SQL       │  ← Groq (Llama 3.1)
│  SQLite: Run Query          │  ← Olist Database
│  Pandas: Analyse Results    │  ← Data Summary
│  LLM #2: Generate Insight   │  ← Groq (Llama 3.1)
└─────────────────────────────┘
        ↓
Structured Output:
Summary · Key Findings · Root Cause · Recommendation
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.x |
| AI / LLM | Groq API (Llama 3.1 8B) |
| Agent Framework | LangChain |
| Database | SQLite (Olist Dataset) |
| Data Analysis | Pandas |
| Visualisation | Plotly |
| UI | Streamlit |

---

## 📁 Project Structure

```
ai-bi-agent-olist/
│
├── app.py                  # Streamlit UI
├── agent.py                # AI agent pipeline
│
├── tools/
│   ├── sql_tool.py         # SQL query execution
│   └── analysis_tool.py    # Pandas data analysis
│
├── prompts/
│   └── system_prompt.txt   # LLM behaviour rules
│
├── utils/
│   └── db.py               # Database connection
│
├── database/
│   └── olist.db            # SQLite database (not tracked in Git)
│
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/joyceleehy/AI-BI-Agent-Olist.git
cd AI-BI-Agent-Olist
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your API key
Create a `.env` file in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free API key at [console.groq.com](https://console.groq.com)

### 4. Add the database
Download the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place `olist.db` in the `database/` folder.

### 5. Run the app
```bash
streamlit run app.py
```

---

## 💡 Key Features

- **Natural Language to SQL** — LLM automatically writes SQL from plain English
- **Real Data** — queries live against Olist e-commerce database (100k+ orders)
- **Structured Insights** — every answer follows Summary → Key Findings → Root Cause → Recommendation
- **Smart Visualisation** — auto-selects bar, line, or pie chart based on data shape
- **Analysis History** — sidebar tracks previous questions in the session

---

## 📊 Dataset

[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k orders from 2016–2018 across Brazil.

| Table | Description |
|---|---|
| orders | Order status and timestamps |
| customers | Customer location data |
| order_items | Products and prices per order |
| payments | Payment method and value |
| products | Product details and category |
| category_translation | Portuguese → English category names |

---

## 🙋 About

Built by **Joyce Lee** — Data & BI Analyst with 10 years of experience in HR Analytics and Business Intelligence.

This project demonstrates:
- AI agent architecture
- Natural language to SQL pipeline
- LLM prompt engineering
- End-to-end data pipeline thinking

📎 [LinkedIn](https://www.linkedin.com/in/joyceleehy) · 📂 [GitHub](https://github.com/joyceleehy)