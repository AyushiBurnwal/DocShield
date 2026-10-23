# detector.py

import re

try:
    import spacy
except ImportError:
    spacy = None


# ============================================================
# REGEX PATTERNS
# ============================================================

PATTERNS = {

    "EMAIL": re.compile(
        r"\b[A-Za-z0-9._%+-]+@"
        r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    ),

    "PHONE": re.compile(
        r"(?<!\d)"
        r"(?:\+91[\s-]?)?"
        r"[6-9]\d{9}"
        r"(?!\d)"
    ),

    "AADHAAR": re.compile(
        r"(?<!\d)"
        r"\d{4}[\s-]\d{4}[\s-]\d{4}"
        r"(?!\d)"
    ),

    "PAN": re.compile(
        r"\b[A-Z]{5}\d{4}[A-Z]\b"
    ),

    "IP_ADDRESS": re.compile(
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
    ),

    "URL": re.compile(
        r"https?://[^\s]+"
    ),

    "CREDIT_CARD": re.compile(
        r"\b(?:\d{4}[\s-]?){3}\d{4}\b"
    )
}


# ============================================================
# SPAcy MODEL
# ============================================================

_nlp = None


def load_spacy_model():

    global _nlp

    if _nlp is not None:
        return _nlp

    if spacy is None:
        return None

    models = [
        "en_core_web_sm"
    ]

    for model in models:

        try:

            _nlp = spacy.load(
                model
            )

            return _nlp

        except Exception:
            continue

    return None


# ============================================================
# REGEX DETECTION
# ============================================================

def detect_regex(text):

    findings = []

    if not text:
        return findings

    for entity_type, pattern in PATTERNS.items():

        for match in pattern.finditer(text):

            findings.append({
                "type": entity_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "method": "regex"
            })

    return findings


# ============================================================
# spaCy DETECTION
# ============================================================

def detect_spacy(text):

    findings = []

    if not text:
        return findings

    nlp = load_spacy_model()

    if nlp is None:
        return findings

    try:

        doc = nlp(text)

        allowed_entities = {
            "PERSON",
            "ORG",
            "GPE",
            "LOC"
        }

        for entity in doc.ents:

            if entity.label_ in allowed_entities:

                findings.append({
                    "type": entity.label_,
                    "value": entity.text,
                    "start": entity.start_char,
                    "end": entity.end_char,
                    "method": "spacy"
                })

    except Exception:
        pass

    return findings


# ============================================================
# REMOVE DUPLICATES
# ============================================================

def remove_duplicate_findings(findings):

    unique = []

    seen = set()

    for finding in findings:

        key = (
            finding["type"],
            finding["value"],
            finding["start"],
            finding["end"]
        )

        if key not in seen:

            seen.add(key)

            unique.append(
                finding
            )

    return unique


# ============================================================
# MAIN TEXT DETECTOR
# ============================================================

def detect_text(text):

    if not text:

        return []

    findings = []

    findings.extend(
        detect_regex(text)
    )

    findings.extend(
        detect_spacy(text)
    )

    findings = remove_duplicate_findings(
        findings
    )

    findings.sort(
        key=lambda x: x["start"]
    )

    return findings


# ============================================================
# DETECT PDF RESULT
# ============================================================

def detect(extraction_result):

    """
    Detect sensitive information from
    extract.py's ExtractionResult.
    """

    all_findings = []

    if extraction_result is None:
        return []

    for page_number, text in enumerate(
        extraction_result.text_by_page,
        start=1
    ):

        page_findings = detect_text(
            text
        )

        for finding in page_findings:

            finding["page"] = page_number

            all_findings.append(
                finding
            )

    return all_findings


# ============================================================
# SUMMARY
# ============================================================

def detection_summary(findings):

    summary = {}

    for finding in findings:

        entity_type = finding["type"]

        summary[entity_type] = (
            summary.get(
                entity_type,
                0
            ) + 1
        )

    return summary


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    text = """
    Customer: Rahul Sharma
    Email: rahul@example.com
    Phone: +919876543210
    PAN: ABCDE1234F
    """

    findings = detect_text(text)

    for finding in findings:

        print(
            finding
        )

    print(
        "\nSummary:"
    )

    print(
        detection_summary(
            findings
        )
    )