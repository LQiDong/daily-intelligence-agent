"""Email sending module — placeholder."""

from loguru import logger


class EmailSender:
    """Send daily report via SMTP."""

    def __init__(self) -> None:
        logger.info("EmailSender initialized")

    def send(self, report: str) -> None:
        """Send the generated report to configured recipients."""
        logger.info("Sending email...")
        # TODO: implement SMTP sending
