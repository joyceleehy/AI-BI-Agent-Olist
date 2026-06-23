import pandas as pd

def analyze_dataframe(df: pd.DataFrame) -> str:
    """
    Takes a DataFrame and returns a plain text summary
    of the key stats — to be passed to the LLM.
    """
    if df.empty:
        return "No data returned from query."

    if "error" in df.columns:
        return f"SQL Error: {df['error'][0]}"

    summary_parts = []

    # Basic shape
    summary_parts.append(f"Data returned: {len(df)} rows, {len(df.columns)} columns.")
    summary_parts.append(f"Columns: {', '.join(df.columns.tolist())}")

    # Numeric column summaries
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    for col in numeric_cols:
        total = df[col].sum()
        average = df[col].mean()
        summary_parts.append(
            f"{col}: total = {total:,.2f}, average = {average:,.2f}"
        )

    # Top rows preview
    summary_parts.append("\nTop 5 rows preview:")
    summary_parts.append(df.head(5).to_string(index=False))

    return "\n".join(summary_parts)