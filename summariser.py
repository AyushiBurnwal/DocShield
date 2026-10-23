# summariser.py

import json
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

DEFAULT_MODEL = "phi3"


# ============================================================
# DATA PREPARATION
# ============================================================

def dataframe_to_text(df, max_rows=30):

    if df is None or df.empty:
        return "No structured table data was extracted."

    sample = df.head(max_rows)

    return sample.to_string(
        index=False
    )


# ============================================================
# LOCAL SUMMARY
# ============================================================

def create_basic_summary(df, profile=None):

    if df is None or df.empty:

        return (
            "No structured table was detected. "
            "The document may contain text without tables."
        )

    rows = len(df)
    columns = len(df.columns)

    column_names = ", ".join(
        str(column)
        for column in df.columns
    )

    summary = (
        f"The document contains {rows} rows "
        f"and {columns} columns. "
        f"The extracted columns are: "
        f"{column_names}."
    )

    if profile:

        numeric = profile.get(
            "numeric_columns",
            []
        )

        if numeric:

            summary += (
                f" Numeric fields identified: "
                f"{', '.join(numeric)}."
            )

        missing = profile.get(
            "missing_values",
            {}
        )

        missing_count = sum(
            missing.values()
        )

        if missing_count > 0:

            summary += (
                f" The extracted data contains "
                f"{missing_count} missing values."
            )

    return summary


# ============================================================
# OLLAMA
# ============================================================

def ollama_available():

    try:

        response = requests.get(
            "http://localhost:11434/api/tags",
            timeout=3
        )

        return response.status_code == 200

    except Exception:

        return False


def generate_ollama_summary(
    df,
    profile=None,
    model=DEFAULT_MODEL
):

    if df is None or df.empty:

        return create_basic_summary(
            df,
            profile
        )

    if not ollama_available():

        return create_basic_summary(
            df,
            profile
        )

    data_text = dataframe_to_text(
        df,
        max_rows=30
    )

    prompt = f"""
You are an AI document analysis assistant.

Analyze the following extracted PDF table.

Do not assume the document is about income, expenses,
sales, banking, or any specific business domain.

Identify only what can reasonably be inferred from
the supplied data.

Provide:

1. Document/data overview
2. Important observations
3. Numeric trends or notable values
4. Missing-data observations
5. Potential data-quality issues

Keep the response concise and professional.

Extracted data:

{data_text}
"""

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        return result.get(
            "response",
            create_basic_summary(
                df,
                profile
            )
        )

    except Exception:

        return create_basic_summary(
            df,
            profile
        )


# ============================================================
# MAIN FUNCTION
# ============================================================

def summarise(
    df,
    profile=None,
    use_ai=True,
    model=DEFAULT_MODEL
):

    if use_ai:

        return generate_ollama_summary(
            df,
            profile,
            model
        )

    return create_basic_summary(
        df,
        profile
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import pandas as pd

    df = pd.DataFrame({
        "Product": [
            "Laptop",
            "Phone",
            "Tablet"
        ],
        "Quantity": [
            10,
            20,
            15
        ],
        "Revenue": [
            50000,
            60000,
            30000
        ]
    })

    print(
        summarise(df)
    )