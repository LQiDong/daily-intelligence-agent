"""EmailSender — orchestrates daily report delivery via SMTP."""

from datetime import datetime

from loguru import logger

from src.config import get_settings
from src.send.email_sender import send_email


class EmailSender:
    """Send the daily intelligence report as an HTML email."""

    def __init__(self) -> None:
        self.settings = get_settings()
        logger.info("EmailSender initialized")

    def send(self, html_body: str) -> None:
        """Send the daily report email.

        If SMTP credentials are not configured, a warning is logged and
        sending is skipped — this allows the pipeline to run fully during
        development without email infrastructure.

        Args:
            html_body: The rendered HTML report string.
        """
        s = self.settings

        # Validate required config
        if not s.smtp_user or not s.smtp_password:
            logger.warning(
                "SMTP credentials not configured (SMTP_USER/SMTP_PASSWORD). "
                "Email sending skipped. Set these in .env to enable."
            )
            return

        if not s.email_to:
            logger.warning("EMAIL_TO not configured. Email sending skipped.")
            return

        # Build subject line
        date_str = datetime.now().strftime("%Y-%m-%d")
        subject = f"每日智能情报简报｜{date_str}｜科技·金融·AI"

        try:
            send_email(
                smtp_host=s.smtp_host,
                smtp_port=s.smtp_port,
                smtp_user=s.smtp_user,
                smtp_password=s.smtp_password,
                email_from=s.email_from or s.smtp_user,
                email_to=s.email_to,
                subject=subject,
                html_body=html_body,
                retry_count=s.smtp_retry_count,
                retry_delay=s.smtp_retry_delay,
                use_tls=not s.smtp_use_ssl,
            )
        except Exception as exc:
            logger.error(f"Failed to send daily report email: {exc}")
            raise
