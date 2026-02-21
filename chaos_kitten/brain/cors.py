from typing import Dict, List

def analyze_cors(headers: Dict[str, str]) -> List[dict]:
    findings = []

    aco = headers.get("access-control-allow-origin", "")
    acc = headers.get("access-control-allow-credentials", "")
    acm = headers.get("access-control-allow-methods", "")

    # Wildcard origin
    if aco.strip() == "*":
        findings.append({
            "issue": "Wildcard ACAO",
            "severity": "high"
        })

    # Credential exposure
    if acc.lower() == "true" and aco:
        findings.append({
            "issue": "Credentialed CORS allowed",
            "severity": "critical"
        })

    # Methods exposed
    dangerous = ["PUT", "DELETE", "PATCH"]
    if any(m in acm.upper() for m in dangerous):
        findings.append({
            "issue": "Dangerous methods exposed via CORS",
            "severity": "medium"
        })

    return findings