"""ReportGenerator — orchestrates report rendering and file output."""

from datetime import datetime
from pathlib import Path

from loguru import logger

from src.collect.models import Article
from src.generate.html_renderer import render_html
from src.generate.markdown_renderer import render_markdown
from src.generate.report_context import build_report_context
from src.process.processor import ProcessResult


class ReportGenerator:
    """Generate daily intelligence report in Markdown and HTML formats."""

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialize with optional custom output directory.

        Args:
            output_dir: Custom output path. Defaults to <project_root>/reports.
        """
        self.output_dir = Path(output_dir) if output_dir else (
            Path(__file__).resolve().parents[2] / "reports"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ReportGenerator initialized (output: {self.output_dir})")

    def generate(self, result: ProcessResult) -> str:
        """Generate report from a ProcessResult and save files.

        Args:
            result: The result from NewsProcessor.process()

        Returns:
            The rendered HTML string (also used by the email sender).
        """
        logger.info("Generating report...")

        # Build rendering context
        ctx = build_report_context(result)

        # Render both formats
        md_content = render_markdown(ctx)
        html_content = render_html(ctx)

        # Determine filename prefix
        date_str = datetime.now().strftime("%Y_%m_%d")

        md_path = self.output_dir / f"report_{date_str}.md"
        html_path = self.output_dir / f"report_{date_str}.html"

        # Write files
        md_path.write_text(md_content, encoding="utf-8")
        logger.info(f"Markdown report saved: {md_path}")

        html_path.write_text(html_content, encoding="utf-8")
        logger.info(f"HTML report saved: {html_path}")

        return html_content
