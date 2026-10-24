import re
PATTERNS = {

    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "PHONE": re.compile(
        r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)"
    ),

    "AADHAAR": re.compile(
        r"(?<!\d)\d{4}[-\s]\d{4}[-\s]\d{4}(?!\d)"
    ),

    "PAN": re.compile(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    ),

    "IP_ADDRESS": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),

    "URL": re.compile(
        r"https?://[^\s]+"
    ),

    "CREDIT_CARD": re.compile(
        r"\b(?:\d[ -]*?){13,19}\b"
    )
}
def detect_text(text, page_number):

    findings = []

    if not text:
        return findings

    for entity_type, pattern in PATTERNS.items():

        for match in pattern.finditer(text):

            findings.append({
                "type": entity_type,
                "value": match.group(),
                "page": page_number,
                "start": match.start(),
                "end": match.end(),
                "method": "regex"
            })

    return findings
def detect_names_from_table(result):

    findings = []

    df = result.primary_table

    if df is None or df.empty:
        return findings

    for column in df.columns:

        column_name = str(column).lower()
        if (
            "name" not in column_name
            and "person" not in column_name
            and "employee" not in column_name
            and "customer" not in column_name
            and "rep" not in column_name
        ):
            continue

        for value in df[column].dropna():

            value = str(value).strip()

            if not value:
                continue

            findings.append({
                "type": "PERSON",
                "value": value,
                "page": 1,
                "start": None,
                "end": None,
                "method": "table_column"
            })

    return findings
def detect(extraction_result):

    findings = []
    for page_number, text in enumerate(
        extraction_result.text_by_page,
        start=1
    ):

        findings.extend(
            detect_text(
                text,
                page_number
            )
        )
    findings.extend(
        detect_names_from_table(
            extraction_result
        )
    )
    unique_findings = []
    seen = set()

    for finding in findings:

        key = (
            finding.get("type"),
            finding.get("value"),
            finding.get("page")
        )

        if key not in seen:

            seen.add(key)
            unique_findings.append(
                finding
            )

    return unique_findings
def detection_summary(findings):

    if not findings:
        return {
            "total_findings": 0,
            "message": "No sensitive information detected."
        }

    summary = {}

    for finding in findings:

        entity_type = finding.get(
            "type",
            "UNKNOWN"
        )

        summary[entity_type] = (
            summary.get(entity_type, 0) + 1
        )

    return {
        "total_findings": len(findings),
        "by_type": summary
    }
if __name__ == "__main__":

    test_text = """
    Contact John at john@example.com
    or call 9876543210.
    """

    print(
        detect_text(
            test_text,
            1
        )
    )
