# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Please report security concerns via email to **security@axelliant.com**. Include:

1. A description of the vulnerability and its potential impact.
2. Steps to reproduce (proof of concept if possible).
3. Affected version(s).

We will acknowledge your report within **48 hours** and aim to provide an initial assessment within **5 business days**.

## Disclosure Policy

- We follow [coordinated disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure).
- After a fix is released, we will credit reporters (unless anonymity is requested).

## Security Best Practices for Deployers

- **Never commit secrets.** Use `.env` files (excluded by `.gitignore`) or a secrets manager.
- Run the API behind a reverse proxy (nginx, Caddy) with TLS in production.
- Restrict database access to the API service network — do not expose PostgreSQL publicly.
- Rotate `POSTGRES_PASSWORD` regularly and use strong, unique values.
- Pin Docker image tags to specific versions in production.
- Keep dependencies updated — run `pip audit` or use Dependabot.

## Contact

- Security issues: [security@axelliant.com](mailto:security@axelliant.com)
- General enquiries: [info@axelliant.com](mailto:info@axelliant.com)
- Website: [axelliant.com](https://axelliant.com)
