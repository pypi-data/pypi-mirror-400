COMPLIANCE_MAPPING = {
    "open port": {
        "OWASP": ["A05:2021 – Security Misconfiguration"],
        "ISO27001": ["A.8.20 Network security"],
        "PCI-DSS": ["Req 1.2"]
    },
    "missing security headers": {
        "OWASP": ["A05:2021 – Security Misconfiguration"],
        "ISO27001": ["A.8.26 Application security"],
        "PCI-DSS": ["Req 6.5"]
    },
    "weak tls": {
        "OWASP": ["A02:2021 – Cryptographic Failures"],
        "ISO27001": ["A.8.24 Cryptography"],
        "PCI-DSS": ["Req 4.1"]
    }
}


def map_compliance(finding_text: str) -> dict:
    text = finding_text.lower()

    for key, mapping in COMPLIANCE_MAPPING.items():
        if key in text:
            return mapping

    return {}
