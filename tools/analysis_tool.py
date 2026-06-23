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

    # Why this? Filter out UUID columns for cleaner preview
    # UUID columns are long hex strings that clutter the display
    clean_df = df.copy()
    for col in clean_df.columns:
        sample = str(clean_df[col].iloc[0])
        is_uuid = len(sample) > 30 and all(
            c in "0123456789abcdef-" for c in sample.lower()
        )
        if is_uuid:
            clean_df = clean_df.drop(columns=[col])

    # Top rows preview without UUID columns
    summary_parts.append("\nTop 5 rows preview:")
    summary_parts.append(clean_df.head(5).to_string(index=False))

    return "\n".join(summary_parts)