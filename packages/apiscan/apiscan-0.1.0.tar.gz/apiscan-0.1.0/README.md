# APIScan

**A Linux-first, safe-by-default API security scanner for modern web APIs**

APIScan is a lightweight security assessment tool designed to identify common misconfigurations and information leaks in public APIs. Built with safety and practicality in mind, it performs non-invasive reconnaissance that mirrors real-world attacker techniques without exploiting vulnerabilities or modifying data.

Whether you're a developer hardening your API, a security engineer conducting assessments, or a learner exploring API security, APIScan provides fast, actionable insights into your API's security posture.

---

## Features

### Security Checks

APIScan performs comprehensive yet non-destructive analysis across multiple security dimensions:

- **TLS/HTTPS Enforcement**: Validates SSL/TLS configuration and checks for proper HTTPS usage
- **Protocol Downgrade Detection**: Identifies HTTP to HTTPS downgrade vulnerabilities
- **Security Headers**: Analyzes presence and configuration of critical security headers (HSTS, CSP, X-Frame-Options, etc.)
- **CORS Misconfiguration**: Detects overly permissive Cross-Origin Resource Sharing policies
- **Rate Limiting**: Tests for absence or weak rate limiting controls
- **Information Disclosure**: Identifies verbose error messages and sensitive data leaks
- **OpenAPI Discovery**: Automatically locates and parses Swagger/OpenAPI definitions

### Output Formats

APIScan generates reports in three complementary formats:

1. **Terminal Output**: Rich, colorized display for immediate feedback
2. **JSON Report**: Machine-readable format for integration with CI/CD pipelines and automation tools
3. **HTML Report**: Human-friendly format with visual severity indicators and detailed findings

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Linux (primary), macOS, or WSL on Windows
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/samuelselasi/apiscan
cd apiscan

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and APIScan
pip install -U pip
pip install -e .
```

---

## Usage

### Basic Scanning

Scan an API root endpoint:

```bash
apiscan https://api.github.com
```

### Scanning Specific Endpoints

Target specific paths for focused assessment:

```bash
apiscan https://api.github.com --paths / /rate_limit /users/octocat
```

### Performance Tuning

Adjust concurrency and timeout for faster scans or slower targets:

```bash
apiscan https://api.github.com \
  --paths / /users/octocat \
  --concurrency 15 \
  --timeout 10
```

### Generating Reports

#### Organized Output Directory

Keep all reports in a dedicated directory:

```bash
apiscan https://api.github.com \
  --paths / /rate_limit \
  --output-dir reports/
```

This generates:
- `reports/apiscan_report.json`
- `reports/apiscan_report.html`

#### Custom Report Names

Specify custom filenames for better organization:

```bash
apiscan https://api.github.com \
  --paths / \
  --output-dir reports/ \
  --json github_api.json \
  --report-html github_api.html
```

### OpenAPI/Swagger Discovery

APIScan can automatically discover and parse OpenAPI specifications:

```bash
# Auto-discover and scan up to 25 endpoints
apiscan https://petstore.swagger.io \
  --discover \
  --max-paths 25 \
  --output-dir reports/
```

#### Combining Discovery with Manual Paths

Mix automatic discovery with specific endpoints:

```bash
apiscan https://api.example.com \
  --discover \
  --paths / /health /metrics \
  --max-paths 30
```

---

## Understanding Results

### Severity Levels

APIScan classifies findings into four severity categories:

| Severity | Description | Examples |
|----------|-------------|----------|
| **Info** | Informational findings with minimal risk | Server version disclosure, API documentation exposure |
| **Low** | Minor issues requiring attention | Missing non-critical security headers |
| **Medium** | Significant misconfigurations | Weak CORS policies, verbose error messages |
| **High** | Critical security issues | Missing HTTPS enforcement, exposed sensitive data |

### Finding Details

Each security finding includes:

- **Description**: Clear explanation of the issue
- **Affected Path**: Specific endpoint where the issue was detected
- **Evidence**: Supporting data such as headers, status codes, or response snippets
- **Severity**: Risk classification to help prioritize remediation

### Risk Scoring

APIScan computes an overall risk score based on:
- Number of findings per severity level
- Aggregate impact across all endpoints
- Configuration weaknesses that compound risk

This score helps you prioritize which APIs need immediate attention.

---

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | Base URL of the target API (required) | - |
| `--paths` | Space-separated list of paths to scan | `/` |
| `--discover` | Attempt OpenAPI/Swagger discovery | `false` |
| `--max-paths` | Maximum number of paths to scan from discovery | `50` |
| `--concurrency` | Number of concurrent requests | `10` |
| `--timeout` | Request timeout in seconds | `5` |
| `--output-dir` | Directory to store output files | Current directory |
| `--json` | Custom filename for JSON report | `apiscan_report.json` |
| `--report-html` | Custom filename for HTML report | `apiscan_report.html` |

### Examples

```bash
# Maximum safety scan with slow concurrency
apiscan https://api.example.com --concurrency 3 --timeout 15

# Aggressive discovery scan
apiscan https://api.example.com --discover --max-paths 100 --concurrency 20

# Quiet scan with only file output
apiscan https://api.example.com --output-dir ./scans --json results.json
```

---

## Safety and Ethics

### What APIScan Does NOT Do

APIScan is explicitly designed to be **safe by default**:

- No brute force attacks
- No exploitation of discovered vulnerabilities
- No payload injection (SQL, XSS, etc.)
- No data modification or deletion
- No authentication bypass attempts

### What APIScan Does

APIScan only performs **standard HTTP reconnaissance**:

- Sends normal HTTP/HTTPS requests
- Analyzes publicly accessible responses
- Examines HTTP headers and status codes
- Parses publicly exposed API documentation

### Legal and Ethical Use

**IMPORTANT**: Only scan systems you own or have explicit authorization to test.

Unauthorized security testing may violate:
- Computer fraud laws (e.g., CFAA in the US)
- Terms of service agreements
- Data protection regulations

Always obtain written permission before scanning third-party APIs.

---

## Roadmap

### Upcoming Features

- [ ] **Authentication Support**: Handle API keys, OAuth, JWT tokens
- [ ] **OpenAPI Deep Analysis**: Schema validation and endpoint coverage testing
- [ ] **Enhanced Severity Scoring**: ML-based risk assessment
- [ ] **PDF Report Export**: Professional reports for stakeholders
- [ ] **CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins plugins
- [ ] **PyPI Release**: Simple `pip install apiscan` installation
- [ ] **Rate Limit Intelligence**: Adaptive throttling based on API responses
- [ ] **GraphQL Support**: Schema introspection and query analysis
- [ ] **WebSocket Testing**: Real-time protocol security checks

### Community Contributions

Contributions are welcome! See `CONTRIBUTING.md` for guidelines.

---

## Troubleshooting

### Common Issues

**Issue**: `Connection timeout` errors

**Solution**: Increase timeout value: `--timeout 15`

---

**Issue**: Rate limited by target API

**Solution**: Reduce concurrency: `--concurrency 3`

---

**Issue**: Permission denied when writing reports

**Solution**: Check directory permissions or specify writable `--output-dir`

---

## Examples

### GitHub API Scan

```bash
apiscan https://api.github.com \
  --paths / /rate_limit /users/octocat \
  --output-dir ./github_scan
```

### Swagger Petstore Full Discovery

```bash
apiscan https://petstore.swagger.io \
  --discover \
  --max-paths 50 \
  --concurrency 10 \
  --output-dir ./petstore_results
```

### Production API Health Check

```bash
apiscan https://api.production.example.com \
  --paths /health /ready /metrics \
  --timeout 10 \
  --json prod_health.json
```

---

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

---

## Acknowledgments

Built with security and simplicity in mind. Special thanks to the open-source security community for inspiration and guidance.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/samuelselasi/apiscan/issues)
- **Discussions**: [GitHub Discussions](https://github.com/samuelselasi/apiscan/discussions)
- **Email**: samelsekasi@gmail.com

---
