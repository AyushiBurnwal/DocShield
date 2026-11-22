
from collections import defaultdict


# ============================================================
# ENTITY MAPPING
# ============================================================

def build_map(findings):

    mapping = defaultdict(list)

    if not findings:
        return {}

    for finding in findings:

        entity_type = finding.get("type", "UNKNOWN")
        category = finding.get("category", "OTHER")

        mapping[entity_type].append({
            "category": category,
            "value": finding.get("value", ""),
            "page": finding.get("page"),
            "start": finding.get("start"),
            "end": finding.get("end"),
            "method": finding.get("method", "unknown")
        })

    return dict(mapping)


# ============================================================
# CATEGORY MAPPING
# ============================================================

def build_category_map(findings):

    mapping = defaultdict(list)

    if not findings:
        return {}

    for finding in findings:

        category = finding.get("category", "OTHER")

        mapping[category].append({
            "type": finding.get("type", "UNKNOWN"),
            "value": finding.get("value", ""),
            "page": finding.get("page"),
            "start": finding.get("start"),
            "end": finding.get("end"),
            "method": finding.get("method", "unknown")
        })

    return dict(mapping)


# ============================================================
# REDACTION TARGETS
# ============================================================

def build_redaction_targets(findings):

    targets = []

    if not findings:
        return targets

    for finding in findings:

        targets.append({
            "page": finding.get("page"),
            "type": finding.get("type"),
            "category": finding.get("category", "OTHER"),
            "value": finding.get("value"),
            "start": finding.get("start"),
            "end": finding.get("end"),
            "method": finding.get("method", "unknown")
        })

    return targets


# ============================================================
# ENTITY SUMMARY
# ============================================================

def map_summary(findings):

    mapping = build_map(findings)

    return {
        entity_type: len(values)
        for entity_type, values in mapping.items()
    }


# ============================================================
# CATEGORY SUMMARY
# ============================================================

def category_summary(findings):

    mapping = build_category_map(findings)

    return {
        category: len(values)
        for category, values in mapping.items()
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    findings = [
        {
            "type": "EMAIL",
            "category": "CONTACT",
            "value": "test@example.com",
            "page": 1,
            "start": 10,
            "end": 26,
            "method": "regex"
        },
        {
            "type": "PAN",
            "category": "IDENTITY",
            "value": "ABCDE1234F",
            "page": 1,
            "start": 40,
            "end": 50,
            "method": "regex"
        }
    ]

    print("Entity mapping:")
    print(build_map(findings))

    print("\nCategory mapping:")
    print(build_category_map(findings))

    print("\nEntity summary:")
    print(map_summary(findings))

    print("\nCategory summary:")
    print(category_summary(findings))
