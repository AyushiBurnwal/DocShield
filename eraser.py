from pathlib import Path

import fitz


# ============================================================
# REDACT PDF
# ============================================================

def redact_pdf(
    input_pdf,
    output_pdf,
    findings
):

    """
    Redact detected sensitive values from a PDF.

    Parameters
    ----------
    input_pdf:
        Original PDF path.

    output_pdf:
        Output/redacted PDF path.

    findings:
        List returned by detector.detect().
    """

    input_pdf = Path(
        str(input_pdf)
        .strip()
        .strip('"')
        .strip("'")
    )

    output_pdf = Path(
        str(output_pdf)
        .strip()
        .strip('"')
        .strip("'")
    )

    if not input_pdf.exists():

        raise FileNotFoundError(
            f"Input PDF not found: {input_pdf}"
        )

    if not findings:

        # No sensitive data detected.
        # Save a copy so the pipeline still works.
        document = fitz.open(
            str(input_pdf)
        )

        document.save(
            str(output_pdf)
        )

        document.close()

        return str(output_pdf)

    # --------------------------------------------------------
    # Open PDF
    # --------------------------------------------------------

    document = fitz.open(
        str(input_pdf)
    )

    # --------------------------------------------------------
    # Process findings
    # --------------------------------------------------------

    for finding in findings:

        page_number = finding.get(
            "page"
        )

        value = finding.get(
            "value"
        )

        if not value:
            continue

        if page_number is None:
            continue

        # detector uses page numbers starting at 1
        page_index = page_number - 1

        if page_index < 0:
            continue

        if page_index >= len(document):
            continue

        page = document[
            page_index
        ]

        # ----------------------------------------------------
        # Search exact detected value
        # ----------------------------------------------------

        try:

            rectangles = page.search_for(
                str(value)
            )

        except Exception:

            rectangles = []

        # ----------------------------------------------------
        # Add redaction areas
        # ----------------------------------------------------

        for rectangle in rectangles:

            page.add_redact_annot(
                rectangle,
                fill=(0, 0, 0)
            )

    # --------------------------------------------------------
    # Apply redactions
    # --------------------------------------------------------

    for page in document:

        page.apply_redactions()

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    document.save(
        str(output_pdf)
    )

    document.close()

    return str(output_pdf)


# ============================================================
# SIMPLE REDACTION FUNCTION
# ============================================================

def erase(
    input_pdf,
    output_pdf,
    findings
):

    """
    Alias for redact_pdf().
    """

    return redact_pdf(
        input_pdf,
        output_pdf,
        findings
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "eraser.py loaded successfully."
    )
