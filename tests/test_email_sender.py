"""Tests for the low-level send_email function with mocked smtplib."""

from unittest.mock import patch, MagicMock

import pytest
import smtplib

from src.send.email_sender import send_email, _mask_email


class TestSendEmail:
    """send_email() unit tests."""

    MINIMAL_KWARGS = {
        "smtp_host": "smtp.test.com",
        "smtp_port": 587,
        "smtp_user": "user@test.com",
        "smtp_password": "secret123",
        "email_from": "from@test.com",
        "email_to": "to@test.com",
        "subject": "Test Subject",
        "html_body": "<h1>Hello</h1>",
    }

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_send_success(self, mock_smtp):
        """Successful send calls SMTP methods correctly."""
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        send_email(**self.MINIMAL_KWARGS)

        mock_smtp.assert_called_once_with("smtp.test.com", 587, timeout=30)
        mock_instance.starttls.assert_called_once()
        mock_instance.login.assert_called_once_with("user@test.com", "secret123")
        mock_instance.sendmail.assert_called_once()

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_send_no_auth(self, mock_smtp):
        """When smtp_user is empty, no login is called."""
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        kwargs = dict(self.MINIMAL_KWARGS)
        kwargs["smtp_user"] = ""
        kwargs["smtp_password"] = ""
        send_email(**kwargs)

        mock_instance.login.assert_not_called()
        mock_instance.sendmail.assert_called_once()

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_send_no_tls(self, mock_smtp):
        """When use_tls=False, starttls is not called."""
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        kwargs = dict(self.MINIMAL_KWARGS)
        kwargs["use_tls"] = False
        send_email(**kwargs)

        mock_instance.starttls.assert_not_called()
        mock_instance.sendmail.assert_called_once()

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_retry_on_failure(self, mock_smtp):
        """Failed send retries."""
        mock_instance = MagicMock()
        mock_instance.sendmail.side_effect = smtplib.SMTPException("Temporary failure")
        mock_smtp.return_value.__enter__.return_value = mock_instance

        with pytest.raises(smtplib.SMTPException):
            send_email(**self.MINIMAL_KWARGS, retry_count=3, retry_delay=0)

        # Should have attempted 3 times
        assert mock_instance.sendmail.call_count == 3

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_retry_then_succeeds(self, mock_smtp):
        """Send fails twice, succeeds on third attempt."""
        mock_instance = MagicMock()
        mock_instance.sendmail.side_effect = [
            smtplib.SMTPException("Fail 1"),
            smtplib.SMTPException("Fail 2"),
            None,  # success on 3rd
        ]
        mock_smtp.return_value.__enter__.return_value = mock_instance

        send_email(**self.MINIMAL_KWARGS, retry_count=3, retry_delay=0)

        assert mock_instance.sendmail.call_count == 3

    @patch("src.send.email_sender.smtplib.SMTP")
    def test_success_on_first_try(self, mock_smtp):
        """No retries needed on success."""
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        send_email(**self.MINIMAL_KWARGS, retry_count=5, retry_delay=0)

        mock_instance.sendmail.assert_called_once()

    def test_recipients_list(self):
        """email_to as list works correctly."""
        with patch("src.send.email_sender.smtplib.SMTP") as mock_smtp:
            mock_instance = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_instance

            kwargs = dict(self.MINIMAL_KWARGS)
            kwargs["email_to"] = ["a@test.com", "b@test.com"]
            send_email(**kwargs)

            # Verify sendmail was called with correct recipients
            call_args = mock_instance.sendmail.call_args[0]
            assert call_args[0] == "from@test.com"
            assert call_args[1] == ["a@test.com", "b@test.com"]


class TestMaskEmail:
    """Email masking utility tests."""

    def test_mask_typical_email(self):
        """Typical email is masked correctly."""
        assert _mask_email("alice@gmail.com") == "ali***@gmail.com"

    def test_mask_short_local(self):
        """Short local part is masked correctly."""
        assert _mask_email("ab@test.com") == "a***@test.com"

    def test_mask_no_at_sign(self):
        """String without @ is returned as-is."""
        assert _mask_email("notanemail") == "notanemail"
