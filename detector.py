
import re

# --------------------------------------------------
# 1. DPDP CATEGORY MAPPING
# --------------------------------------------------

CATEGORY_MAP = {
    "EMAIL": "CONTACT",
    "PHONE": "CONTACT",
    "ADDRESS": "CONTACT",

    "AADHAAR": "IDENTITY",
    "PAN": "IDENTITY",
    "PASSPORT": "IDENTITY",
    "VOTER_ID": "IDENTITY",

    "BANK_ACCOUNT": "FINANCIAL",
    "IFSC": "FINANCIAL",
    "CREDIT_CARD": "FINANCIAL",
    "UPI_ID": "FINANCIAL",

    "DOB": "PERSONAL",
    "AGE": "PERSONAL",
    "PERSON": "PERSONAL",
    "FAMILY_DETAILS": "PERSONAL",

    "EMPLOYEE_ID": "EMPLOYMENT",
    "SALARY": "EMPLOYMENT",

    "HEALTH_INFO": "HEALTH",
    "BIOMETRIC": "BIOMETRICS",
    "LOCATION": "LOCATION",

    "PASSWORD": "AUTHENTICATION",
    "OTP": "AUTHENTICATION",
    "ACCESS_TOKEN": "AUTHENTICATION",

    "CHILD_NAME": "CHILDREN",
    "SCHOOL": "CHILDREN",

    "IP_ADDRESS": "LOCATION",
    "URL": "OTHER"
}


# --------------------------------------------------
# 2. REGULAR EXPRESSION PATTERNS
# --------------------------------------------------

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

    # Indian passport format: one letter followed by seven digits
    "PASSPORT": re.compile(
        r"\b[A-PR-WYa-pr-wy][0-9]{7}\b"
    ),

    # Indian voter ID / EPIC-like format
    "VOTER_ID": re.compile(
        r"\b[A-Z]{3}[0-9]{7}\b"
    ),

    "IFSC": re.compile(
        r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
    ),

    "UPI_ID": re.compile(
        r"\b[a-zA-Z0-9._-]+@[a-zA-Z]{2,}\b"
    ),

    "IP_ADDRESS": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),

    "URL": re.compile(
        r"https?://[^\s]+"
    )
}


# --------------------------------------------------
# 3. CONTEXT-BASED PATTERNS
# --------------------------------------------------

CONTEXT_PATTERNS = {

    "BANK_ACCOUNT": re.compile(
        r"\b(?:account\s*(?:number|no\.?)|bank\s*account)"
        r"\s*[:#-]?\s*(\d{9,18})\b",
        re.IGNORECASE
    ),

    "DOB": re.compile(
        r"\b(?:DOB|date\s*of\s*birth|birth\s*date)"
        r"\s*[:#-]?\s*"
        r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        re.IGNORECASE
    ),

    "AGE": re.compile(
        r"\b(?:age)\s*[:#-]?\s*(\d{1,3})\b",
        re.IGNORECASE
    ),

    "EMPLOYEE_ID": re.compile(
        r"\b(?:employee\s*id|emp\s*id|staff\s*id)"
        r"\s*[:#-]?\s*([A-Z0-9-]{3,20})\b",
        re.IGNORECASE
    ),

    "SALARY": re.compile(
        r"\b(?:salary|annual\s*income|monthly\s*income|CTC)"
        r"\s*[:#-]?\s*((?:INR|Rs\.?|₹)?\s*[\d,]+(?:\.\d{1,2})?)",
        re.IGNORECASE
    ),

    "PASSWORD": re.compile(
        r"\b(?:password|passwd|pwd)"
        r"\s*[:=]\s*(\S+)",
        re.IGNORECASE
    ),

    "OTP": re.compile(
        r"\b(?:OTP|one.time.password)"
        r"\s*[:#-]?\s*(\d{4,8})\b",
        re.IGNORECASE
    ),

    "ACCESS_TOKEN": re.compile(
        r"\b(?:access.token|api.key|secret.key)"
        r"\s*[:=]\s*([A-Za-z0-9._-]{8,})",
        re.IGNORECASE
    )
}


# --------------------------------------------------
# 4. FINDING CREATION
# --------------------------------------------------

def make_finding(entity_type, value, page_number,
                 start, end, method):

    return {
        "type": entity_type,
        "category": CATEGORY_MAP.get(entity_type, "OTHER"),
        "value": value,
        "page": page_number,
        "start": start,
        "end": end,
        "method": method
    }


# --------------------------------------------------
# 5. CREDIT CARD VALIDATION
# --------------------------------------------------

def is_valid_card_number(value):

    digits = re.sub(r"[\s-]", "", value)

    if not digits.isdigit() or not 13 <= len(digits) <= 19:
        return False

    total = 0
    reverse_digits = digits[::-1]

    for index, digit in enumerate(reverse_digits):
        number = int(digit)

        if index % 2 == 1:
            number *= 2

            if number > 9:
                number -= 9

        total += number

    return total % 10 == 0


# --------------------------------------------------
# 6. TEXT DETECTION
# --------------------------------------------------

def detect_text(text, page_number):

    findings = []

    if not text:
        return findings

    # Standard patterns
    for entity_type, pattern in PATTERNS.items():

        for match in pattern.finditer(text):

            value = match.group()

            # UPI IDs overlap with email-like strings.
            # Keep the more specific UPI classification.
            if entity_type == "EMAIL" and re.fullmatch(
                r"[a-zA-Z0-9._-]+@[a-zA-Z]+", value
            ):
                continue

            findings.append(
                make_finding(
                    entity_type,
                    value,
                    page_number,
                    match.start(),
                    match.end(),
                    "regex"
                )
            )

    # Credit card numbers with Luhn validation
    card_pattern = re.compile(
        r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)"
    )

    for match in card_pattern.finditer(text):

        value = match.group()

        if is_valid_card_number(value):

            findings.append(
                make_finding(
                    "CREDIT_CARD",
                    value,
                    page_number,
                    match.start(),
                    match.end(),
                    "regex_luhn"
                )
            )

    # Context-based patterns
    for entity_type, pattern in CONTEXT_PATTERNS.items():

        for match in pattern.finditer(text):

            value = match.group(1)

            # Capture only the sensitive value, not its label.
            start = match.start(1)
            end = match.end(1)

            findings.append(
                make_finding(
                    entity_type,
                    value,
                    page_number,
                    start,
                    end,
                    "context_regex"
                )
            )

    return findings


# --------------------------------------------------
# 7. TABLE NAME DETECTION
# --------------------------------------------------

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

            findings.append(
                make_finding(
                    "PERSON",
                    value,
                    1,
                    None,
                    None,
                    "table_column"
                )
            )

    return findings


# --------------------------------------------------
# 8. MAIN DETECTION FUNCTION
# --------------------------------------------------

def detect(extraction_result):

    findings = []

    for page_number, text in enumerate(
        extraction_result.text_by_page,
        start=1
    ):

        findings.extend(
            detect_text(text, page_number)
        )

    findings.extend(
        detect_names_from_table(extraction_result)
    )

    unique_findings = []
    seen = set()

    for finding in findings:

        key = (
            finding.get("type"),
            finding.get("value"),
            finding.get("page"),
            finding.get("start"),
            finding.get("end")
        )

        if key not in seen:

            seen.add(key)
            unique_findings.append(finding)

    return unique_findings


# --------------------------------------------------
# 9. DETECTION SUMMARY
# --------------------------------------------------

def detection_summary(findings):

    if not findings:
        return {
            "total_findings": 0,
            "message": "No sensitive information detected."
        }

    summary = {}
    category_summary = {}

    for finding in findings:

        entity_type = finding.get("type", "UNKNOWN")
        category = finding.get("category", "OTHER")

        summary[entity_type] = (
            summary.get(entity_type, 0) + 1
        )

        category_summary[category] = (
            category_summary.get(category, 0) + 1
        )

    return {
        "total_findings": len(findings),
        "by_type": summary,
        "by_category": category_summary
    }


# --------------------------------------------------
# 10. BASIC TEST
# --------------------------------------------------

if __name__ == "__main__":

    test_text = """
    Contact John at john@example.com
    or call 9876543210.

    PAN: ABCDE1234F
    Aadhaar: 1234 5678 9012
    IFSC: SBIN0001234
    UPI: ayushi@okaxis
    DOB: 12/05/2002
    Employee ID: EMP12345
    OTP: 123456
    """

    results = detect_text(test_text, 1)

    for item in results:
        print(item)

    print("\nSummary:")
    print(detection_summary(results))
