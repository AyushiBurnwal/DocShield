# extract.py

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pdfplumber


# ============================================================
# RESULT OBJECT
# ============================================================

@dataclass
class ExtractionResult:
    filename: str
    primary_table: pd.DataFrame
    text_by_page: list[str]
    tables_by_page: list[list[pd.DataFrame]]


# ============================================================
# CURRENCY / NUMBER CLEANING
# ============================================================

def clean_currency(value):
    """
    Convert currency/numeric-looking values into numbers.

    Examples:
        "$1,250.50"      -> 1250.50
        "₹1,250.50"      -> 1250.50
        "€500"           -> 500.0
        "1,200 USD"      -> 1200.0
        "(500.00)"       -> -500.0

    Values that are not numeric remain unchanged.
    """

    if value is None:
        return value

    if pd.isna(value):
        return value

    # Already numeric
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()

    if text == "":
        return value

    # Remove common currency symbols
    cleaned = re.sub(
        r"[$₹€£¥]",
        "",
        text
    )

    # Remove currency codes
    cleaned = re.sub(
        r"\b(USD|INR|EUR|GBP|JPY|AUD|CAD)\b",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = cleaned.strip()

    # Handle accounting negative values
    negative = False

    if cleaned.startswith("(") and cleaned.endswith(")"):
        negative = True
        cleaned = cleaned[1:-1]

    # Remove commas
    cleaned = cleaned.replace(",", "")

    # Remove spaces
    cleaned = cleaned.replace(" ", "")

    # Check if it is a number
    if re.fullmatch(r"-?\d+(\.\d+)?", cleaned):
        try:
            number = float(cleaned)

            if negative:
                number = -number

            return number

        except ValueError:
            pass

    return value


# ============================================================
# COLUMN CLEANING
# ============================================================

def clean_column_name(column):
    """
    Clean a PDF table column name without assuming
    any specific business/domain column.
    """

    column = str(column).strip()

    # Replace newlines/tabs
    column = re.sub(r"[\r\n\t]+", " ", column)

    # Remove repeated spaces
    column = re.sub(r"\s+", " ", column)

    return column


def clean_dataframe(df):
    """
    Generic dataframe cleaning.

    Works with any columns.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    df.columns = [
        clean_column_name(col)
        for col in df.columns
    ]

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = df.dropna(how="all")

    # --------------------------------------------------------
    # Clean string cells
    # --------------------------------------------------------

    for column in df.columns:

        df[column] = df[column].apply(
            lambda value:
            re.sub(
                r"\s+",
                " ",
                str(value).strip()
            )
            if isinstance(value, str)
            else value
        )

    # --------------------------------------------------------
    # Convert numeric-looking columns automatically
    # --------------------------------------------------------

    for column in df.columns:

        original = df[column]

        converted = original.apply(clean_currency)

        # Calculate how many values became numeric
        numeric_count = converted.apply(
            lambda x: isinstance(x, (int, float))
            and not isinstance(x, bool)
        ).sum()

        non_empty_count = original.notna().sum()

        if non_empty_count > 0:

            numeric_ratio = numeric_count / non_empty_count

            # Convert column if majority of values are numeric
            if numeric_ratio >= 0.6:

                df[column] = pd.to_numeric(
                    converted,
                    errors="coerce"
                )

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    df = df.reset_index(drop=True)

    return df


# ============================================================
# TABLE EXTRACTION
# ============================================================

def extract_page_tables(page):
    """
    Extract all tables from one PDF page.
    """

    tables = []

    try:
        extracted_tables = page.extract_tables()

        if not extracted_tables:
            return tables

        for table in extracted_tables:

            if not table:
                continue

            # Remove completely empty rows
            table = [
                row for row in table
                if row and any(
                    cell is not None and str(cell).strip() != ""
                    for cell in row
                )
            ]

            if not table:
                continue

            # First row as header
            header = table[0]

            # Remaining rows
            rows = table[1:]

            # Make sure every row has same number of columns
            column_count = len(header)

            cleaned_rows = []

            for row in rows:

                row = list(row)

                if len(row) < column_count:
                    row += [None] * (
                        column_count - len(row)
                    )

                elif len(row) > column_count:
                    row = row[:column_count]

                cleaned_rows.append(row)

            try:

                df = pd.DataFrame(
                    cleaned_rows,
                    columns=header
                )

                df = clean_dataframe(df)

                if not df.empty:
                    tables.append(df)

            except Exception:
                continue

    except Exception:
        pass

    return tables


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_page_text(page):
    """
    Extract normal text from a PDF page.
    """

    try:

        text = page.extract_text()

        if text is None:
            return ""

        return text.strip()

    except Exception:
        return ""


# ============================================================
# SELECT PRIMARY TABLE
# ============================================================

def select_primary_table(tables):
    """
    Select the largest useful table.

    This does NOT assume any particular PDF type.
    """

    if not tables:
        return pd.DataFrame()

    # Choose table with most cells
    return max(
        tables,
        key=lambda df: df.shape[0] * df.shape[1]
    ).copy()


# ============================================================
# MAIN EXTRACTION FUNCTION
# ============================================================

def extract(pdf_path):
    """
    Generic PDF extraction.

    Input:
        pdf_path -> path to any PDF

    Returns:
        ExtractionResult
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Input file must be a PDF."
        )

    all_tables = []
    tables_by_page = []
    text_by_page = []

    # --------------------------------------------------------
    # Open PDF
    # --------------------------------------------------------

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            # -----------------------------------------------
            # Extract text
            # -----------------------------------------------

            text = extract_page_text(page)

            text_by_page.append(text)

            # -----------------------------------------------
            # Extract tables
            # -----------------------------------------------

            page_tables = extract_page_tables(page)

            tables_by_page.append(page_tables)

            all_tables.extend(page_tables)

    # --------------------------------------------------------
    # Select primary table
    # --------------------------------------------------------

    primary_table = select_primary_table(
        all_tables
    )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return ExtractionResult(
        filename=pdf_path.name,
        primary_table=primary_table,
        text_by_page=text_by_page,
        tables_by_page=tables_by_page
    )


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    pdf_file = input(
        "Enter PDF path: "
    ).strip()

    try:

        result = extract(pdf_file)

        print("\n================================")
        print("PDF:", result.filename)
        print("================================")

        print(
            "\nPages:",
            len(result.text_by_page)
        )

        print(
            "Tables found:",
            sum(
                len(page_tables)
                for page_tables
                in result.tables_by_page
            )
        )

        # ----------------------------------------------------
        # Show extracted text
        # ----------------------------------------------------

        print("\n========== TEXT ==========\n")

        for i, text in enumerate(
            result.text_by_page,
            start=1
        ):

            print(f"--- Page {i} ---")

            print(
                text[:1000]
            )

        # ----------------------------------------------------
        # Show primary table
        # ----------------------------------------------------

        print(
            "\n========== PRIMARY TABLE ==========\n"
        )

        if result.primary_table.empty:

            print(
                "No table detected."
            )

        else:

            print(
                result.primary_table
            )

            print(
                "\nColumns:"
            )

            print(
                result.primary_table.columns.tolist()
            )

    except Exception as e:

        print(
            "\nExtraction failed:"
        )

        print(e)