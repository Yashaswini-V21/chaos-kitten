# 🐱 Chaos Kitten Security Report

**Generated:** {{ generated_at }}  
**Target:** {{ target_url }}  
**Version:** {{ version }}

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Endpoints Tested** | {{ endpoints_tested }} |
| **Total Vulnerabilities** | {{ total_vulns }} |
| **🔴 Critical** | {{ critical_count }} |
| **🟠 High** | {{ high_count }} |
| **🟡 Medium** | {{ medium_count }} |
| **🟢 Low** | {{ low_count }} |
| **Time Taken** | {{ time_taken }} |

---

## 🚨 Vulnerabilities Found

{% for vuln in vulnerabilities %}
### {{ loop.index }}. {{ vuln.title }}

| Property | Value |
|----------|-------|
| **Severity** | {{ vuln.severity }} |
| **Endpoint** | `{{ vuln.method }} {{ vuln.endpoint }}` |
| **Category** | {{ vuln.category }} |

> {{ vuln.cat_message }}

**Description:**  
{{ vuln.description }}

**📋 Proof of Concept:**

```bash
{{ vuln.poc }}
```

**Response:**
```
{{ vuln.response_snippet }}
```

**🔧 Remediation:**

{{ vuln.remediation }}

---

{% endfor %}

## 📝 Testing Details

### Endpoints Tested

| Method | Endpoint | Status |
|--------|----------|--------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | `{{ endpoint.path }}` | {{ endpoint.status }} |
{% endfor %}

---

## ⚖️ Legal Notice

This report was generated using Chaos Kitten for authorized security testing purposes only. 
The testing was conducted with proper authorization from the system owner.

---

<p align="center">
  🐱 <strong>Chaos Kitten</strong><br>
  <em>"The adorable AI agent that knocks things off your API tables"</em>
</p>
