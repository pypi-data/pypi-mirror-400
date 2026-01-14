"""Slack notification integration."""

import json
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

from datacheck.exceptions import DataCheckError
from datacheck.results import ValidationSummary


class SlackNotifier:
    """Send validation results to Slack via webhooks.

    Example:
        >>> notifier = SlackNotifier("https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
        >>> notifier.send_summary(summary, title="Production Data Validation")
    """

    def __init__(self, webhook_url: str) -> None:
        """Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL

        Raises:
            ValueError: If webhook URL is empty
        """
        if not webhook_url or not webhook_url.strip():
            raise ValueError("Slack webhook URL cannot be empty")
        self.webhook_url = webhook_url.strip()

    def send_summary(
        self, summary: ValidationSummary, title: str | None = None, mention_on_failure: bool = False
    ) -> None:
        """Send validation summary to Slack.

        Args:
            summary: ValidationSummary object
            title: Optional custom title for the message
            mention_on_failure: If True, mention @channel on failures

        Raises:
            DataCheckError: If sending notification fails
        """
        try:
            message = self._format_message(summary, title, mention_on_failure)
            self._send_to_slack(message)
        except Exception as e:
            raise DataCheckError(f"Failed to send Slack notification: {e}") from e

    def _format_message(
        self, summary: ValidationSummary, title: str | None, mention_on_failure: bool
    ) -> dict:
        """Format validation summary as Slack message.

        Args:
            summary: ValidationSummary object
            title: Optional custom title
            mention_on_failure: Whether to mention @channel on failure

        Returns:
            Slack message payload
        """
        # Determine status emoji and color
        if summary.all_passed:
            status_emoji = ":white_check_mark:"
            color = "#10b981"  # Green
            status_text = "PASSED"
        else:
            status_emoji = ":x:"
            color = "#ef4444"  # Red
            status_text = "FAILED"

        # Add mention if requested and validation failed
        mention = ""
        if mention_on_failure and not summary.all_passed:
            mention = "<!channel> "

        # Build header text
        header_title = title or "DataCheck Validation Report"
        header_text = f"{mention}*{header_title}*"

        # Build summary fields
        [
            {"title": "Status", "value": f"{status_emoji} {status_text}", "short": True},
            {"title": "Total Checks", "value": str(summary.total_rules), "short": True},
            {"title": "Passed", "value": str(summary.passed_rules), "short": True},
            {"title": "Failed", "value": str(summary.failed_rules), "short": True},
        ]

        # Add failed rule details if any
        failed_rules_text = ""
        if not summary.all_passed:
            failed_rules = [r for r in summary.results if not r.passed]
            failed_rules_text = "\n*Failed Rules:*\n"
            for rule in failed_rules[:5]:  # Show first 5 failed rules
                failed_rules_text += (
                    f"• `{rule.rule_name}` on column `{rule.column}`: "
                    f"{rule.failed_rows}/{rule.total_rows} rows failed\n"
                )
            if len(failed_rules) > 5:
                failed_rules_text += f"_...and {len(failed_rules) - 5} more_\n"

        # Build message attachment
        blocks: list[dict[str, Any]] = [
            {"type": "header", "text": {"type": "plain_text", "text": header_title}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"{status_emoji} *{status_text}*"}},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Checks:*\n{summary.total_rules}"},
                    {"type": "mrkdwn", "text": f"*Passed:*\n{summary.passed_rules}"},
                    {"type": "mrkdwn", "text": f"*Failed:*\n{summary.failed_rules}"},
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n{round((summary.passed_rules / summary.total_rules * 100) if summary.total_rules > 0 else 0, 1)}%",
                    },
                ],
            },
        ]

        # Add failed rules section if applicable
        if failed_rules_text:
            blocks.append(
                {"type": "section", "text": {"type": "mrkdwn", "text": failed_rules_text}}
            )

        attachment = {
            "color": color,
            "blocks": blocks,
        }

        return {"text": header_text, "attachments": [attachment]}

    def _send_to_slack(self, message: dict) -> None:
        """Send message to Slack webhook.

        Args:
            message: Slack message payload

        Raises:
            DataCheckError: If request fails
        """
        try:
            data = json.dumps(message).encode("utf-8")
            req = request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with request.urlopen(req, timeout=10) as response:
                if response.status != 200:
                    raise DataCheckError(
                        f"Slack webhook returned status {response.status}: {response.read().decode()}"
                    )

        except HTTPError as e:
            raise DataCheckError(f"Slack webhook HTTP error {e.code}: {e.reason}") from e
        except URLError as e:
            raise DataCheckError(f"Slack webhook URL error: {e.reason}") from e
        except Exception as e:
            raise DataCheckError(f"Failed to send Slack message: {e}") from e


__all__ = ["SlackNotifier"]
