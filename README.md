📦 DevSecOps Security Pipeline

This repository contains a complete DevSecOps CI/CD security pipeline for a Flask application.
The pipeline runs automated:

Unit tests

Static Application Security Testing (SAST)

Dependency scanning (SCA)

Docker image vulnerability scanning

Dynamic Application Security Testing (DAST)

Email notifications for HIGH/CRITICAL vulnerabilities

🏗️ Pipeline Architecture
flowchart LR
    A[Push Code] --> B[Unit Tests]
    B --> C[Bandit SAST]
    B --> D[pip-audit SCA]
    C --> E[Build Docker Image]
    D --> E
    E --> F[Trivy Image Scan]
    E --> G[Run App Container]
    G --> H[OWASP ZAP DAST]
    F --> I[Security Summary]
    H --> I
    I --> J{High/Critical Findings?}
    J -->|YES| K[Send Email Alert]
    J -->|NO| L[Pipeline Passes]

🛠️ Technologies Used

Flask (Python)

pytest

Bandit

pip-audit

Docker

Trivy

OWASP ZAP

GitHub Actions

SMTP Email Alerts

📁 Repository Structure
devsecops-pipeline/
│
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   └── tests/
│
├── Dockerfile
├── docker-compose.yml
├── zap-config.yaml
│
└── .github/workflows/ci-security.yml

▶️ Running the Application Locally

Install dependencies:

pip install -r app/requirements.txt


Run app:

python app/app.py


App will be available at:

http://localhost:5000

💥 Testing Vulnerabilities

This project includes an intentionally vulnerable Flask version for pipeline testing.

You can introduce vulnerabilities such as:

SQL Injection
db.execute("SELECT * FROM users WHERE username LIKE '%" + q + "%'")

XSS
return f"<h1>Hello {request.args.get('name')}</h1>"


Push changes → pipeline will detect them.

📧 Configuring Email Alerts

Create these GitHub secrets:

Secret	Description
MAIL_USERNAME	Gmail address
MAIL_PASSWORD	Gmail App Password
MAIL_TO	Destination email

Create Gmail App Password here:
https://myaccount.google.com/apppasswords

🧪 Pipeline Stages

1. build-test-sast

Runs unit tests

Bandit SAST

pip-audit dependency scan

Uploads reports

2. trivy-scan

Builds Docker image

Trivy scans OS + package vulnerabilities

3. zap-dast

Runs app container

OWASP ZAP automated DAST

Uploads HTML report

4. analyze-security

Aggregates Bandit, pip-audit, Trivy, ZAP results

Generates security-summary.txt

5. notify-security

Sends email only if HIGH/CRITICAL issues exist

