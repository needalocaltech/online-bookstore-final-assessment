"""
security_control_checker.py

Static analyser that scans your Flask project and checks whether
security controls mapped to ISO 27001 & NIST SP 800-53 are present
in the codebase.

Run:
    python security_control_checker.py
"""

import os
import re

# Files to analyse
TARGET_FILES = [
    "bookstore/__init__.py",
    "bookstore/config.py",
    "bookstore/services/user_service.py",
    "bookstore/routes/auth.py",
    "bookstore/routes/admin.py",
]

# Controls to detect (regex patterns)
CONTROL_PATTERNS = {
    "ENV_SECRET_KEY (ISO A.10 / NIST SC-12)": r"SECRET_KEY\s*=\s*os\.environ",
    "CSRF Protection Enabled (ISO A.14 / NIST SC-5)": r"CSRFProtect",
    "Security Headers Added (ISO A.14 / NIST SC-18)": r"Content-Security-Policy",
    "HttpOnly / Secure Cookies (ISO A.9.4 / NIST SC-23)": r"SESSION_COOKIE_HTTPONLY|SESSION_COOKIE_SECURE",
    "Password Policy Enforcement (ISO A.9.2.4 / NIST IA-5)": r"def _validate_password_policy",
    "bcrypt Password Hashing (ISO A.9 / NIST IA-5)": r"bcrypt",
    "Account Lockout Enabled (ISO A.9.4.4 / NIST AC-7)": r"MAX_FAILED_ATTEMPTS",
    "RBAC Admin Required (ISO A.9.1.2 / NIST AC-3)": r"admin_required",
    "Audit Logging (ISO A.12.4 / NIST AU-2)": r"logger\.info|logger\.warning",
}

def scan_file(path):
    """Return file text or None if unreadable."""
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

    # Print report
    print(f"{'CONTROL':60} {'STATUS':10} {'FILE'}")
    print("-" * 90)
    for ctrl, status, fpath in report:
        print(f"{ctrl:60} {status:10} {fpath}")
    
    # Save CSV
    import csv
    with open("security_control_report.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Control", "Status", "File"])
        writer.writerows(report)

    print("\nReport saved to: security_control_report.csv\n")


if __name__ == "__main__":
    check_controls()
