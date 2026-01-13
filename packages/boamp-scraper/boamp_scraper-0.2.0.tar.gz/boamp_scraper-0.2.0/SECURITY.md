# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: contact@algora.fr

You should receive a response within 48 hours. If for some reason you do not, please follow up via email to ensure we received your original message.

Please include the following information in your report:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

## Preferred Languages

We prefer all communications to be in English or French.

## Policy

We follow the principle of [Coordinated Vulnerability Disclosure](https://vuls.cert.org/confluence/display/CVD).

## Security Updates

Security updates will be released as soon as possible after a vulnerability is confirmed and a fix is available.

Updates will be announced via:
- GitHub Security Advisories
- GitHub Releases
- CHANGELOG.md

## Best Practices for Users

To use BOAMP Scraper securely:

1. **Keep dependencies updated**: Regularly update all dependencies
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Use environment variables**: Never hardcode credentials
   ```python
   # ✅ Good
   from dotenv import load_dotenv
   load_dotenv()
   api_key = os.getenv("API_KEY")
   
   # ❌ Bad
   api_key = "sk-abc123..."
   ```

3. **Validate input**: Always validate user input when using the scraper in your application

4. **Use latest version**: Always use the latest stable version
   ```bash
   pip install --upgrade boamp-scraper
   ```

5. **Review code**: Before using in production, review the source code

## Acknowledgments

We thank the security researchers and users who report vulnerabilities to the BOAMP Scraper community.

## Contact

For any security concerns, please email: contact@algora.fr

