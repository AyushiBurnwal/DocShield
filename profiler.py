# profiler.py

import pandas as pd


def profile_dataframe(df):
    """
    Create a generic profile of an extracted DataFrame.

    Works with any PDF/table structure.
    """

    if df is None or df.empty:
        return {
            "rows": 0,
            "columns": 0,
            "column_names": [],
            "numeric_columns": [],
            "text_columns": [],
            "date_columns": [],
            "missing_values": {},
            "duplicate_rows": 0,
            "data_types": {},
            "summary": pd.DataFrame()
        }

    df = df.copy()

    # -------------------------------------------------------
    # Basic information
    # -------------------------------------------------------

    rows = len(df)
    columns = len(df.columns)

    column_names = df.columns.tolist()

    # -------------------------------------------------------
    # Detect column types
    # -------------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns.tolist()

    # -------------------------------------------------------
    # Detect date-like columns
    # -------------------------------------------------------

    date_columns = []

    for column in df.columns:

        if pd.api.types.is_datetime64_any_dtype(
            df[column]
        ):
            date_columns.append(column)
            continue

        if df[column].dtype == "object":

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_ratio = converted.notna().mean()

            if valid_ratio >= 0.7:
                date_columns.append(column)

    # -------------------------------------------------------
    # Missing values
    # -------------------------------------------------------

    missing_values = (
        df.isna()
        .sum()
        .to_dict()
    )

    # -------------------------------------------------------
    # Duplicate rows
    # -------------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    # -------------------------------------------------------
    # Data types
    # -------------------------------------------------------

    data_types = {
        column: str(df[column].dtype)
        for column in df.columns
    }

    # -------------------------------------------------------
    # Numeric summary
    # -------------------------------------------------------

    try:
        summary = df.describe(
            include="all"
        ).transpose()
    except Exception:
        summary = pd.DataFrame()

    # -------------------------------------------------------
    # Return profile
    # -------------------------------------------------------

    return {
        "rows": rows,
        "columns": columns,
        "column_names": column_names,
        "numeric_columns": numeric_columns,
        "text_columns": text_columns,
        "date_columns": date_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "data_types": data_types,
        "summary": summary
    }


def print_profile(profile):
    """
    Print profile information in a readable format.
    """

    print("\n========== DATA PROFILE ==========")

    print(
        "Rows:",
        profile["rows"]
    )

    print(
        "Columns:",
        profile["columns"]
    )

    print(
        "Column Names:",
        profile["column_names"]
    )

    print(
        "Numeric Columns:",
        profile["numeric_columns"]
    )

    print(
        "Text Columns:",
        profile["text_columns"]
    )

    print(
        "Date Columns:",
        profile["date_columns"]
    )

    print(
        "Duplicate Rows:",
        profile["duplicate_rows"]
    )

    print("\nMissing Values:")

    for column, count in profile[
        "missing_values"
    ].items():

        print(
            f"  {column}: {count}"
        )

    print("\nData Types:")

    for column, dtype in profile[
        "data_types"
    ].items():

        print(
            f"  {column}: {dtype}"
        )


if __name__ == "__main__":

    # Simple test
    data = {
        "Name": ["John", "Alice", "Bob"],
        "Age": [25, 30, 28],
        "Salary": [40000, 50000, 45000]
    }

    df = pd.DataFrame(data)

    profile = profile_dataframe(df)

    print_profile(profile)