from __future__ import annotations

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from opendpp.core.report import ConformanceReport


def render_report_html(report: ConformanceReport, template_path: Optional[str] = None) -> str:
    base_dir = Path(__file__).parent
    if template_path:
        loader = FileSystemLoader(Path(template_path).parent)
        template_name = Path(template_path).name
    else:
        loader = FileSystemLoader(base_dir / "templates")
        template_name = "report.html.j2"

    env = Environment(loader=loader, autoescape=select_autoescape(["html"]))
    template = env.get_template(template_name)
    return template.render(report=report)
