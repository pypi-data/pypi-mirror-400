<div align="center">

# 🛡️ CHRONOS Security

### Unified Security Fusion Platform

[![PyPI version](https://badge.fury.io/py/chronos-security.svg)](https://badge.fury.io/py/chronos-security)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-141%20passing-brightgreen.svg)]()
[![Downloads](https://img.shields.io/pypi/dm/chronos-security.svg)](https://pypi.org/project/chronos-security/)

**All-in-one security CLI** for threat intelligence, vulnerability management, phishing detection, log analysis, and incident response.

[Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples)

</div>

---

## ⚡ Why CHRONOS?

- **🚀 Lightning Fast** - Single-letter shortcuts: `chronos s`, `chronos d .`, `chronos c CVE-2024-1234`
- **🔗 Unified Intelligence** - Integrates EPSS, NVD, CISA KEV, URLhaus, VirusTotal
- **🎯 Smart Prioritization** - ML-powered vulnerability scoring (CVSS + EPSS + KEV)
- **🤖 AI Anomaly Detection** - IsolationForest ML for log analysis
- **📊 Beautiful Reports** - HTML/Markdown/JSON with charts
- **🔐 Zero Config** - Works out-of-the-box, API keys optional
- **🧪 Battle-Tested** - 141 passing tests, production-ready

---

## 📦 Installation

```bash
pip install chronos-security
```

**Verify installation:**
```bash
chronos --version
chronos status
```

**Optional API Keys** (for enhanced features):
```bash
export CHRONOS_NVD_KEY="your-nvd-api-key"          # Higher rate limits
export CHRONOS_VIRUSTOTAL_KEY="your-vt-api-key"   # URL/file scanning
```

---

## ⚡ Quick Shortcuts (NEW in v1.1.0)

CHRONOS now supports **ultra-fast single-letter commands** for power users:

```bash
chronos s                      # Status check
chronos d .                    # Scan current directory
chronos c CVE-2024-1234        # CVE lookup
chronos u https://evil.com     # Check URL reputation
chronos v scan.json            # Import vulnerabilities
chronos p suspicious.eml       # Analyze phishing email
chronos l server.log           # Analyze logs
chronos r report.html          # Generate report
```

---

## 🚀 Quick Start

### 🔎 Threat Intelligence

```bash
# Look up CVE with EPSS score and KEV status
chronos intel cve CVE-2023-44487
chronos c CVE-2023-44487  # Shortcut

# Check URL reputation (URLhaus + VirusTotal)
chronos intel url https://suspicious-site.com
chronos u https://suspicious-site.com  # Shortcut

# List CISA KEV vulnerabilities
chronos intel kev --days 7

# Bulk CVE analysis
chronos intel bulk cves.txt --enrich
```

### 🔓 Vulnerability Management

```bash
# Import from scanner (auto-detects format)
chronos vuln import trivy-results.json
chronos vuln import grype-output.json
chronos vuln import sarif-report.json
chronos v scan.json  # Shortcut

# Prioritize by EPSS + KEV
chronos vuln prioritize scan.json --top 20

# Generate patching plan
chronos vuln plan scan.json --severity high
```

### 🎣 Phishing Detection

```bash
# Analyze single email
chronos phish analyze suspicious.eml
chronos p suspicious.eml  # Shortcut

# Batch process mailbox
chronos phish batch ./inbox/

# Check specific URL in email
chronos phish url https://phishing-link.com
```

### 📜 Log Analysis

```bash
# Analyze logs with ML anomaly detection
chronos logs analyze server.log --ml
chronos l server.log  # Shortcut

# Create baseline for normal behavior
chronos logs baseline access.log

# Analyze multiple log formats
chronos logs analyze /var/log/ --type auth
```

### 📊 Report Generation

```bash
# HTML report with charts
chronos report generate report.html
chronos r report.html  # Shortcut

# Management-friendly report
chronos report generate executive.html --audience management

# JSON export for automation
chronos report generate data.json --format json --days 30
```

### 🚨 Incident Response

```bash
# List available playbooks
chronos ir list

# Run playbook (dry-run by default)
chronos ir run malware_response --dry-run

# Execute real response
chronos ir run brute_force_response --execute --target 192.168.1.50
```

---

## 🛠️ Core Features

<table>
<tr>
<td width="50%">

### 🔬 Threat Intelligence
- ✅ **EPSS** - Exploit prediction scores
- ✅ **NVD** - CVE database queries
- ✅ **CISA KEV** - Known exploited vulns
- ✅ **URLhaus** - Malicious URL tracking
- ✅ **VirusTotal** - File/URL reputation
- ✅ **Priority Scoring** - ML-based ranking

</td>
<td width="50%">

### 🔓 Vulnerability Management
- ✅ **Multi-Format** - SARIF/Trivy/Grype/Bandit
- ✅ **Auto-Enrichment** - EPSS + KEV data
- ✅ **Smart Prioritization** - Risk-based sorting
- ✅ **Patching Plans** - Remediation guidance
- ✅ **Trending** - Historical vulnerability tracking

</td>
</tr>
<tr>
<td>

### 🎣 Phishing Detection
- ✅ **Email Analysis** - SPF/DKIM/DMARC
- ✅ **URL Scanning** - Real-time reputation
- ✅ **Impersonation** - Brand spoofing detection
- ✅ **Attachment Check** - Malware indicators
- ✅ **Batch Processing** - Analyze mailboxes

</td>
<td>

### 📜 Log Analysis
- ✅ **Multi-Format** - Syslog/JSON/CloudTrail
- ✅ **ML Anomalies** - IsolationForest detection
- ✅ **Baseline** - Normal behavior profiling
- ✅ **Pattern Matching** - Regex-based alerts
- ✅ **Time-Series** - Temporal analysis

</td>
</tr>
</table>

### 📊 Report Generation
- **HTML Reports** - Beautiful, interactive dashboards with charts
- **Markdown** - Developer-friendly documentation
- **JSON** - API/automation integration
- **Audiences** - Technical, Management, Audit templates
- **Scheduling** - Automated periodic reports

### 🚨 Incident Response
- **YAML Playbooks** - Codified response procedures
- **Dry-Run Mode** - Safe testing before execution
- **Built-in Playbooks** - Malware, phishing, brute force, data breach
- **Custom Playbooks** - Extend with your procedures
- **Action Logging** - Full audit trail

---

## � Examples

### Complete Workflow Example

```bash
# 1. Check CHRONOS status
chronos s

# 2. Scan your codebase for vulnerabilities
chronos d /path/to/project

# 3. Import scanner results and prioritize
chronos v trivy-scan.json

# 4. Look up critical CVEs
chronos c CVE-2024-1234

# 5. Check suspicious URLs from logs
chronos u https://suspicious-link.com

# 6. Analyze phishing emails
chronos p suspicious.eml

# 7. Analyze security logs
chronos l /var/log/auth.log

# 8. Generate executive report
chronos r security-report.html --audience management
```

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install CHRONOS
        run: pip install chronos-security
      
      - name: Scan for vulnerabilities
        run: chronos detect scan . --output json > scan.json
      
      - name: Import and prioritize
        run: chronos vuln import scan.json
      
      - name: Generate report
        run: chronos report generate report.html
      
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: report.html
```

### Security Operations Center (SOC)

```bash
# Morning security checks
chronos intel kev --days 1 > new-kev.txt
chronos logs analyze /var/log/nginx/ --ml > anomalies.json
chronos phish batch /var/mail/quarantine/

# Automated vulnerability tracking
chronos vuln import trivy-$(date +%Y%m%d).json
chronos vuln trending --days 30 > vuln-trends.csv

# Incident response
chronos ir run data_breach_response --execute --affected-users users.csv
```

---

## 🔧 Configuration

### Quick Config

```bash
# Initialize CHRONOS in your project
chronos init

# Check configuration
chronos config show

# Set API keys
chronos config set api.nvd_key YOUR_KEY
chronos config set api.virustotal_key YOUR_KEY
```

### Configuration File

Create `~/.chronos/config.toml`:

```toml
[api_keys]
nvd_key = "your-nvd-api-key"
virustotal_key = "your-vt-api-key"

[intel]
cache_ttl_hours = 24
auto_enrich = true

[vuln]
priority_threshold = 70
auto_kev_check = true

[logs]
ml_enabled = true
baseline_days = 7

[ir]
dry_run_default = true
notification_webhook = "https://your-slack-webhook"

[report]
default_format = "html"
include_charts = true
```

### Environment Variables

```bash
# API Keys (recommended for CI/CD)
export CHRONOS_NVD_KEY="your-nvd-api-key"
export CHRONOS_VIRUSTOTAL_KEY="your-vt-api-key"

# Database location
export CHRONOS_DB_PATH="/path/to/chronos.db"

# Configuration
export CHRONOS_CONFIG_PATH="/path/to/config.toml"
```

---

## 📚 Documentation

### Command Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| `chronos status` | `chronos s` | Check system status |
| `chronos detect scan` | `chronos d` | Scan for threats |
| `chronos analyze crypto` | `chronos a` | Analyze cryptography |
| `chronos intel cve` | `chronos c` | CVE lookup |
| `chronos intel url` | `chronos u` | URL reputation check |
| `chronos vuln import` | `chronos v` | Import vulnerabilities |
| `chronos phish analyze` | `chronos p` | Analyze phishing |
| `chronos logs analyze` | `chronos l` | Analyze logs |
| `chronos report generate` | `chronos r` | Generate reports |
| `chronos ir run` | - | Run IR playbook |

### Get Help

```bash
# General help
chronos --help

# Command-specific help
chronos intel --help
chronos vuln import --help

# Version info
chronos --version

# System diagnostics
chronos doctor
```

---

## 🎯 Use Cases

### For Security Engineers
- **Vulnerability Triage** - Prioritize patches using EPSS + KEV
- **Threat Hunting** - Correlate CVEs with exploit activity
- **Log Analysis** - Detect anomalies with ML
- **Incident Response** - Execute playbooks automatically

### For DevSecOps Teams
- **CI/CD Integration** - Scan every commit
- **Security Gates** - Block deployments on critical vulns
- **Automated Reporting** - Daily security summaries
- **Compliance** - Track vulnerability SLAs

### For SOC Analysts
- **Phishing Triage** - Analyze quarantined emails
- **URL Reputation** - Check suspicious links
- **Log Monitoring** - Real-time anomaly detection
- **Threat Intel** - Enrich alerts with CVE data

### For Security Managers
- **Executive Reports** - Management-friendly dashboards
- **Trend Analysis** - Track security posture over time
- **Risk Metrics** - Quantify vulnerability exposure
- **Compliance** - Generate audit reports

---

## 🚀 Performance

- **Fast Scans** - 10,000+ files/second
- **Efficient ML** - IsolationForest anomaly detection in <1 second
- **Cached Intel** - Local caching reduces API calls
- **Parallel Processing** - Multi-threaded scanning
- **Low Memory** - <100MB for typical workloads

---

## 🛡️ Security & Privacy

- ✅ **No Telemetry** - Zero data collection
- ✅ **Local Processing** - All analysis runs locally
- ✅ **Optional APIs** - Works without external services
- ✅ **Encrypted Secrets** - API keys stored securely
- ✅ **Audit Logs** - Full action history
- ✅ **Open Source** - Transparent, reviewable code

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md).

```bash
# Development setup
git clone https://github.com/yourusername/chronos-security
cd chronos-security
pip install -e ".[dev]"
pytest

# Run with local changes
python -m chronos.cli.main status
```

---

## 📊 Roadmap

- [ ] **v1.2** - Docker scanning support
- [ ] **v1.3** - Kubernetes security audits
- [ ] **v1.4** - Cloud security posture (AWS/Azure/GCP)
- [ ] **v1.5** - SBOM generation and analysis
- [ ] **v2.0** - Web dashboard UI
- [ ] **v2.1** - REST API server
- [ ] **v2.2** - Real-time monitoring

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FIRST** - EPSS data
- **NVD** - CVE database
- **CISA** - KEV catalog
- **URLhaus** - URL reputation
- **VirusTotal** - Malware intelligence

---

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/chronos-security/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/chronos-security/discussions)
- 📧 **Email**: team@chronos-security.io
- 📖 **Docs**: [Documentation](https://chronos-security.io/docs)

---

<div align="center">

**Made with ❤️ by the CHRONOS Security Team**

[⭐ Star us on GitHub](https://github.com/yourusername/chronos-security) | [📦 PyPI Package](https://pypi.org/project/chronos-security/)

</div>
