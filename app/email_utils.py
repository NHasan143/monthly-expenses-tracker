# email_utils.py
# Centralises all outgoing email logic for the application so that auth.py
# stays clean and focused purely on request handling.
#
# Functions:
#   - generate_reset_token(email)  : Creates a signed, expiring token.
#   - verify_reset_token(token)    : Validates a token, returns email or None.
#   - send_welcome_email(user)     : Sends branded welcome email on registration.
#   - send_password_reset_email(user, reset_url) : Sends password reset email.

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import current_app
from flask_mail import Message
from . import mail

# Token expiry — 1 hour in seconds
TOKEN_MAX_AGE = 3600


# ── Token Helpers ─────────────────────────────────────────────────────────────

def generate_reset_token(email: str) -> str:
    """
    Generate a signed, URL-safe token embedding the given email address.
    Uses the app secret key so it cannot be forged without it.
    """
    s = URLSafeTimedSerializer(current_app.secret_key)
    return s.dumps(email, salt='password-reset-salt')


def verify_reset_token(token: str) -> str | None:
    """
    Validate a password-reset token and return the embedded email address.
    Returns None if expired or tampered with.
    """
    s = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=TOKEN_MAX_AGE)
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    return email


# ── Email Helpers ─────────────────────────────────────────────────────────────

def _base_html(header_subtitle, body_content):
    """
    Shared HTML email shell used by both welcome and reset emails.
    Keeps the two senders DRY — only the inner content differs.
    """
    return (
        "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'/>"
        "<meta name='viewport' content='width=device-width,initial-scale=1.0'/>"
        "</head>"
        "<body style='margin:0;padding:0;background:#0d1117;"
        "font-family:Arial,sans-serif;'>"
        "<table width='100%' cellpadding='0' cellspacing='0'"
        " style='background:#0d1117;padding:40px 20px;'>"
        "<tr><td align='center'>"
        "<table width='560' cellpadding='0' cellspacing='0'"
        " style='background:#161b22;border:1px solid #30363d;"
        "border-radius:12px;overflow:hidden;max-width:560px;'>"
        "<tr><td style='padding:32px 40px 24px;"
        "border-bottom:1px solid #30363d;text-align:center;'>"
        "<p style='margin:0 0 8px;font-size:22px;font-weight:800;"
        "color:#e6edf3;'>💰 Budget Tracker</p>"
        "<p style='margin:0;font-size:13px;color:#8b949e;'>"
        + header_subtitle +
        "</p></td></tr>"
        "<tr><td style='padding:32px 40px;'>"
        + body_content +
        "</td></tr>"
        "<tr><td style='padding:20px 40px;"
        "border-top:1px solid #30363d;text-align:center;'>"
        "<p style='margin:0;font-size:12px;color:#8b949e;'>"
        "© 2026 Monthly Expense Tracker - Created with ❤️ by "
        "<a href='https://github.com/NHasan143'"
        " style='color:#3bdf91;text-decoration:none;'>Naymul Hasan</a>"
        "</p></td></tr>"
        "</table></td></tr></table>"
        "</body></html>"
    )


# ── Email Senders ─────────────────────────────────────────────────────────────

def send_welcome_email(user) -> None:
    """
    Send a branded HTML welcome email to a newly registered user.
    Errors are caught silently so a mail failure never crashes registration.
    """
    body_content = (
        "<p style='margin:0 0 16px;font-size:20px;font-weight:700;"
        "color:#e6edf3;'>Welcome aboard, " + user.username + "! 🎉</p>"
        "<p style='margin:0 0 16px;font-size:15px;color:#8b949e;line-height:1.7;'>"
        "Your Budget Tracker account is all set. You can now log your income, "
        "track expenses by category, visualise your spending, and export "
        "summaries to CSV — all in one place.</p>"
        "<table cellpadding='0' cellspacing='0' width='100%'"
        " style='margin:24px 0;background:#1c2333;border:1px solid #30363d;"
        "border-radius:8px;overflow:hidden;'>"
        "<tr><td style='padding:14px 20px;border-bottom:1px solid #30363d;'>"
        "<span style='color:#3bdf91;font-weight:600;'>📊</span>"
        "<span style='color:#e6edf3;font-size:14px;margin-left:10px;'>"
        "Live dashboard with spending breakdown</span></td></tr>"
        "<tr><td style='padding:14px 20px;border-bottom:1px solid #30363d;'>"
        "<span style='color:#3bdf91;font-weight:600;'>🗂️</span>"
        "<span style='color:#e6edf3;font-size:14px;margin-left:10px;'>"
        "Category-based expense tracking</span></td></tr>"
        "<tr><td style='padding:14px 20px;border-bottom:1px solid #30363d;'>"
        "<span style='color:#3bdf91;font-weight:600;'>💰</span>"
        "<span style='color:#e6edf3;font-size:14px;margin-left:10px;'>"
        "Savings rate calculation</span></td></tr>"
        "<tr><td style='padding:14px 20px;'>"
        "<span style='color:#3bdf91;font-weight:600;'>📥</span>"
        "<span style='color:#e6edf3;font-size:14px;margin-left:10px;'>"
        "Export your data to CSV anytime</span></td></tr>"
        "</table>"
        "<p style='margin:24px 0 0;font-size:13px;color:#8b949e;line-height:1.6;'>"
        "If you didn't create this account, you can safely ignore this email.</p>"
    )

    html_body = _base_html("Personal Finance Dashboard", body_content)

    text_body = (
        "Welcome to Monthly Expense Tracker, " + user.username + "!\n\n"
        "Your account is ready. Start tracking your expenses and taking "
        "control of your finances.\n\n"
        "If you didn't create this account, please ignore this email.\n\n"
        "— The Monthly Expense Tracker Team"
    )

    msg = Message(
        subject="Welcome to Monthly Expense Tracker 💰",
        recipients=[user.email],
        body=text_body,
        html=html_body,
    )

    try:
        mail.send(msg)
    except BaseException as exc:
        # Log but never let a mail failure crash registration
        current_app.logger.error(
            "[email] Failed to send welcome email to " + user.email + ": " + str(exc)
        )


def send_password_reset_email(user, reset_url: str) -> None:
    """
    Send a password-reset email with a one-time expiring link.
    Errors are caught silently so a mail failure never blocks the user flow.
    """
    body_content = (
        "<p style='margin:0 0 16px;font-size:20px;font-weight:700;"
        "color:#e6edf3;'>Reset your password</p>"
        "<p style='margin:0 0 16px;font-size:15px;color:#8b949e;line-height:1.7;'>"
        "Hi <strong style='color:#e6edf3;'>" + user.username + "</strong>, "
        "we received a request to reset your Budget Tracker password. "
        "Click the button below to choose a new password.</p>"
        "<table cellpadding='0' cellspacing='0' width='100%'"
        " style='margin:20px 0;background:rgba(248,81,73,0.08);"
        "border:1px solid rgba(248,81,73,0.25);border-radius:8px;'>"
        "<tr><td style='padding:14px 18px;'>"
        "<p style='margin:0;font-size:13px;color:#f85149;'>"
        "⏱ This link expires in <strong>1 hour</strong>. "
        "If you didn't request a reset, you can safely ignore this email — "
        "your password will not change.</p>"
        "</td></tr></table>"
        "<table cellpadding='0' cellspacing='0' style='margin:28px 0 8px;'>"
        "<tr><td style='background:#3bdf91;border-radius:8px;'>"
        "<a href='" + reset_url + "'"
        " style='display:inline-block;padding:12px 28px;color:#0d1117;"
        "font-weight:700;font-size:15px;text-decoration:none;"
        "border-radius:8px;'>Reset My Password →</a>"
        "</td></tr></table>"
        "<p style='margin:20px 0 0;font-size:12px;color:#8b949e;line-height:1.6;'>"
        "Button not working? Copy and paste this link into your browser:<br/>"
        "<a href='" + reset_url + "'"
        " style='color:#3bdf91;word-break:break-all;'>" + reset_url + "</a></p>"
    )

    html_body = _base_html("Password Reset Request", body_content)

    text_body = (
        "Hi " + user.username + ",\n\n"
        "We received a request to reset your Budget Tracker password.\n\n"
        "Reset link (expires in 1 hour):\n" + reset_url + "\n\n"
        "If you didn't request this, ignore this email — "
        "your password won't change.\n\n"
        "— The Budget Tracker Team"
    )

    msg = Message(
        subject="Reset your Budget Tracker password",
        recipients=[user.email],
        body=text_body,
        html=html_body,
    )

    try:
        mail.send(msg)
    except BaseException as exc:
        # Log but never let a mail failure block the user flow
        current_app.logger.error(
            "[email] Failed to send reset email to " + user.email + ": " + str(exc)
        )