# mapper.py

from collections import defaultdict


# ============================================================
# ENTITY MAPPING
# ============================================================

def build_map(findings):

    """
    Convert detector output into
    an entity-based mapping.
    """

    mapping = defaultdict(list)

    if not findings:
        return {}

    for finding in findings:

        entity_type = finding.get(
            "type",
            "UNKNOWN"
        )

        mapping[entity_type].append(
            {
                "value": finding.get(
                    "value",
                    ""
                ),
                "page": finding.get(
                    "page",
                    None
                ),
                "start": finding.get(
                    "start",
                    None
                ),
                "end": finding.get(
                    "end",
                    None
                ),
                "method": finding.get(
                    "method",
                    "unknown"
                )
            }
        )

    return dict(mapping)


# ============================================================
# REDACTION TARGETS
# ============================================================

def build_redaction_targets(
    findings
):

    """
    Create a flat list of redaction targets.
    """

    targets = []

    if not findings:
        return targets

    for finding in findings:

        targets.append({
            "page": finding.get(
                "page"
            ),
            "type": finding.get(
                "type"
            ),
            "value": finding.get(
                "value"
            ),
            "start": finding.get(
                "start"
            ),
            "end": finding.get(
                "end"
            )
        })

    return targets


# ============================================================
# SUMMARY
# ============================================================

def map_summary(findings):

    mapping = build_map(
        findings
    )

    summary = {}

    for entity_type, values in mapping.items():

        summary[entity_type] = len(
            values
        )

    return summary


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    findings = [

        {
            "type": "EMAIL",
            "value": "test@example.com",
            "page": 1,
            "start": 10,
            "end": 26,
            "method": "regex"
        },

        {
            "type": "PERSON",
            "value": "Rahul Sharma",
            "page": 1,
            "start": 40,
            "end": 52,
            "method": "spacy"
        }
    ]

    mapping = build_map(
        findings
    )

    print(
        mapping
    )

    print(
        "\nSummary:"
    )

    print(
        map_summary(
            findings
        )
    )