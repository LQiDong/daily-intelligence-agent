"""Tests for the EmailSender class."""

from unittest.mock import patch, MagicMock

from src.send.sender import EmailSender


class TestEmailSender:
    """EmailSender unit tests."""

    def test_send_skipped_no_credentials(self):
        """Send is skipped when SMTP credentials are missing."""
        with patch("src.send.sender.get_settings") as mock_settings:
            settings = MagicMock()
            settings.smtp_user = ""
            settings.smtp_password = ""
            settings.email_to = "test@test.com"
            mock_settings.return_value = settings

            sender = EmailSender()
            with patch("src.send.sender.send_email") as mock_send:
                sender.send("<html></html>")
                mock_send.assert_not_called()

    def test_send_skipped_no_recipient(self):
        """Send is skipped when EMAIL_TO is missing."""
        with patch("src.send.sender.get_settings") as mock_settings:
            settings = MagicMock()
            settings.smtp_user = "user@test.com"
            settings.smtp_password = "pass"
            settings.email_to = ""
            mock_settings.return_value = settings

            sender = EmailSender()
            with patch("src.send.sender.send_email") as mock_send:
                sender.send("<html></html>")
                mock_send.assert_not_called()

    def test_send_with_credentials(self):
        """Send is called when all credentials are present."""
        with patch("src.send.sender.get_settings") as mock_settings:
            settings = MagicMock()
            settings.smtp_host = "smtp.test.com"
            settings.smtp_port = 587
            settings.smtp_user = "user@test.com"
            settings.smtp_password = "secret"
            settings.email_from = ""
            settings.email_to = "to@test.com"
            settings.smtp_retry_count = 3
            settings.smtp_retry_delay = 5
            settings.smtp_use_ssl = False
            mock_settings.return_value = settings

            sender = EmailSender()
            with patch("src.send.sender.send_email") as mock_send:
                sender.send("<h1>Report</h1>")
                mock_send.assert_called_once_with(
                    smtp_host="smtp.test.com",
                    smtp_port=587,
                    smtp_user="user@test.com",
                    smtp_password="secret",
                    email_from="user@test.com",
                    email_to="to@test.com",
                    subject=mock_send.call_args[1]["subject"],
                    html_body="<h1>Report</h1>",
                    retry_count=3,
                    retry_delay=5,
                    use_tls=True,
                )

    def test_subject_format(self):
        """Subject follows the required format."""
        with patch("src.send.sender.get_settings") as mock_settings:
            settings = MagicMock()
            settings.smtp_user = "user@test.com"
            settings.smtp_password = "pass"
            settings.email_from = ""
            settings.email_to = "to@test.com"
            settings.smtp_retry_count = 3
            settings.smtp_retry_delay = 5
            settings.smtp_use_ssl = False
            mock_settings.return_value = settings

            sender = EmailSender()
            with patch("src.send.sender.send_email") as mock_send:
                sender.send("<html></html>")
                subject = mock_send.call_args[1]["subject"]
                assert "每日智能情报简报" in subject
                assert "｜" in subject
                assert "科技·金融·AI" in subject

    def test_send_exception_raised(self):
        """Exception from send_email is re-raised."""
        with patch("src.send.sender.get_settings") as mock_settings:
            settings = MagicMock()
            settings.smtp_user = "user@test.com"
            settings.smtp_password = "pass"
            settings.email_from = ""
            settings.email_to = "to@test.com"
            settings.smtp_retry_count = 3
            settings.smtp_retry_delay = 5
            settings.smtp_use_ssl = False
            mock_settings.return_value = settings

            sender = EmailSender()
            with patch("src.send.sender.send_email", side_effect=Exception("SMTP error")):
                import pytest

                with pytest.raises(Exception, match="SMTP error"):
                    sender.send("<html></html>")
