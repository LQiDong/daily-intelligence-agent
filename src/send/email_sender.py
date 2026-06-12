"""Low-level SMTP email sender with retry support.

This module handles the actual SMTP connection, authentication, and message sending.
It does NOT read configuration — the caller passes all parameters explicitly
so that testing can inject any values without mocking the config module.
"""

import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Callable

from loguru import logger


def send_email(
    *,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    email_from: str,
    email_to: str | list[str],
    subject: str,
    html_body: str,
    retry_count: int = 3,
    retry_delay: int = 5,
    use_tls: bool = True,
) -> None:
    """Send an HTML email via SMTP with configurable retry.

    Args:
        smtp_host: SMTP server hostname.
        smtp_port: SMTP server port.
        smtp_user: SMTP username (usually the email address).
        smtp_password: SMTP password or app password.
        email_from: From address.
        email_to: Recipient address(es). Single string or list.
        subject: Email subject line.
        html_body: HTML email body.
        retry_count: Max retry attempts (default 3).
        retry_delay: Seconds between retries (default 5).
        use_tls: Whether to use STARTTLS (default True).

    Raises:
        smtplib.SMTPException: If all retry attempts fail.
    """
    recipients = [email_to] if isinstance(email_to, str) else email_to
    to_addrs = ", ".join(recipients) if isinstance(email_to, list) else email_to

    # Build message
    msg = MIMEMultipart("alternative")
    msg["From"] = email_from
    msg["To"] = to_addrs
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    # Log safely — NEVER log password
    _log_send_attempt(smtp_host, smtp_port, smtp_user, to_addrs, subject, retry_count)

    last_exception: Exception | None = None

    for attempt in range(1, retry_count + 1):
        try:
            _do_send(smtp_host, smtp_port, smtp_user, smtp_password, recipients, msg, use_tls)
            logger.info(f"Email sent successfully to {to_addrs}")
            return
        except (smtplib.SMTPException, OSError, TimeoutError) as exc:
            last_exception = exc
            if attempt < retry_count:
                logger.warning(
                    f"Email send attempt {attempt}/{retry_count} failed: {exc}. "
                    f"Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(
                    f"Email send failed after {retry_count} attempts: {exc}"
                )

    # All retries exhausted
    if last_exception:
        raise last_exception


def _do_send(
    host: str,
    port: int,
    user: str,
    password: str,
    recipients: list[str],
    msg: MIMEMultipart,
    use_tls: bool,
) -> None:
    """Establish SMTP connection, authenticate, and send."""
    with smtplib.SMTP(host, port, timeout=30) as server:
        if use_tls:
            server.starttls()
        if user:
            server.login(user, password)
        server.sendmail(msg["From"], recipients, msg.as_string())


def _log_send_attempt(
    host: str, port: int, user: str, to_addrs: str, subject: str, retry_count: int
) -> None:
    """Log email details safely — NEVER include password or API keys in logs."""
    # Mask the username partially for privacy
    masked_user = _mask_email(user) if "@" in user else user
    logger.info(
        f"Preparing to send email: "
        f"host={host}:{port}, "
        f"user={masked_user}, "
        f"to={to_addrs}, "
        f"subject='{subject}', "
        f"max_retries={retry_count}"
    )


def _mask_email(email: str) -> str:
    """Partially mask an email address for safe logging.

    'alice@gmail.com' → 'ali***@gmail.com'
    Strings without '@' are returned as-is.
    """
    if "@" not in email:
        return email
    local, at, domain = email.partition("@")
    if len(local) <= 3:
        masked_local = local[0] + "***"
    else:
        masked_local = local[:3] + "***"
    return f"{masked_local}{at}{domain}"
