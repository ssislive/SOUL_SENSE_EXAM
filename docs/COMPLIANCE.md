# Open-Source Compliance Checklist

## 1. Licensing
- [x] **License File**: Ensure `LICENSE` or `LICENSE.txt` exists in the root directory.
- [x] **License Type**: Verify the license is OSI-approved (e.g., MIT, Apache 2.0, GPL).
- [x] **Header Comments**: (Optional) Include license headers in source files if required by the license.

## 2. Documentation
- [x] **README.md**:
  - [x] Project description and purpose.
  - [x] Installation instructions.
  - [x] Usage guide.
  - [x] Contribution guidelines (link to `CONTRIBUTING.md` or section).
- [x] **CODE_OF_CONDUCT.md**: Define expected behavior for contributors.
- [x] **CONTRIBUTING.md**: Guidelines for submitting issues and pull requests.
- [x] **CHANGELOG.md**: Track version history and changes.

## 3. Code Quality & Standards
- [x] **Coding Style**: Adhere to language-specific standards (e.g., PEP 8 for Python).
- [x] **Linting/Formatting**: Use tools like `flake8`, `black`, or `pylint`.
- [x] **Comments**: meaningful comments and docstrings.
- [x] **No Secrets**: Ensure no API keys, passwords, or tokens are committed.

## 4. Testing & CI/CD
- [x] **Test Suite**: Include unit and integration tests.
- [x] **CI Configuration**: Set up GitHub Actions or similar for automated testing.
- [x] **Coverage**: Monitor test coverage.

## 5. Security & Privacy
- [x] **Dependency Check**: regularly check for vulnerable dependencies (`safety`, `dependabot`).
- [x] **Data Handling**: Ensure no PII is logged or exposed unintentionally.
- [x] **Security Policy**: (Optional) `SECURITY.md` for reporting vulnerabilities.

## 6. Community & Governance
- [x] **Issue Templates**: specific templates for bugs and features.
- [x] **PR Templates**: checklist for pull requests.
- [x] **Governance Model**: (Optional) Define how decisions are made.
