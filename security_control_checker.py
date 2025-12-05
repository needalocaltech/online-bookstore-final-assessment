"""
security_control_checker.py

Static analyser that scans your Flask project and checks whether
security controls mapped to ISO 27001 & NIST SP 800-53 are present
in the codebase.

Run from the project root:
    python security_control_checker.py
"""

import os
import re
import csv

TARGET_FILES = [
    "config.py",
    "__init__.py",
    os.path.join("services", "user_service.py"),
    os.path.join("routes", "auth.py"),
    os.path.join("routes", "admin.py"),
]

CONTROL_PATTERNS = {
    "ENV_SECRET_KEY (ISO A.10 / NIST SC-12)": r"SECRET_KEY\s*=\s*os\.environ",
    "SQLAlchemy Configured (ISO A.12 / NIST SC-28)": r"SQLALCHEMY_DATABASE_URI",
    "HttpOnly / SameSite Cookies (ISO A.9.4 / NIST SC-23)": r"SESSION_COOKIE_HTTPONLY|SESSION_COOKIE_SAMESITE",
    "CSRF Protection Enabled (ISO A.14 / NIST SC-5)": r"CSRFProtect",
    "Security Headers Added (ISO A.14 / NIST SC-18)": r"Content-Security-Policy",
    "bcrypt Password Hashing (ISO A.9 / NIST IA-5)": r"bcrypt\.hashpw",
    "Password Policy Enforcement (ISO A.9.2.4 / NIST IA-5)": r"_validate_password_policy",
    "Account Lockout Enabled (ISO A.9.4.4 / NIST AC-7)": r"MAX_FAILED_ATTEMPTS",
    "RBAC Admin Required (ISO A.9.1.2 / NIST AC-3)": r"admin_required",
    "Audit Logging (ISO A.12.4 / NIST AU-2)": r"logging\.getLogger|app\.logger",
}


def scan_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def check_controls():
    report = []
    print("\n=== Security Control Checker ===\n")

    for label, pattern in CONTROL_PATTERNS.items():
        matched = False

        for file_path in TARGET_FILES:
            text = scan_file(file_path)
            if text and re.search(pattern, text):
                matched = True
                report.append((label, "ENABLED", file_path))
                break

        if not matched:
            report.append((label, "MISSING", ""))

    print(f"{'CONTROL':60} {'STATUS':10} {'FILE'}")
    print("-" * 90)
    for ctrl, status, fpath in report:
        print(f"{ctrl:60} {status:10} {fpath}")

    with open("security_control_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Control", "Status", "File"])
        writer.writerows(report)

    print("\nReport saved to: security_control_report.csv\n")


if __name__ == "__main__":
    check_controls()
