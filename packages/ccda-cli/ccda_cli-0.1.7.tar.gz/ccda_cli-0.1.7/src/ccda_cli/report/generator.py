"""Report generation for analysis results.

Supports Markdown, HTML, and JSON output formats.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class ReportGenerator:
    """Generates reports from analysis results."""

    def __init__(self, data: dict[str, Any]):
        """Initialize with analysis data.

        Args:
            data: Analysis result dictionary (unified.json format)
        """
        self.data = data

    @classmethod
    def from_file(cls, path: Path) -> "ReportGenerator":
        """Load from a unified.json file."""
        with open(path) as f:
            data = json.load(f)
        return cls(data)

    def generate(self, format: str = "markdown") -> str:
        """Generate report in specified format.

        Args:
            format: Output format (json, markdown, html)

        Returns:
            Report content as string
        """
        if format == "json":
            return json.dumps(self.data, indent=2)
        elif format == "markdown":
            return self._generate_markdown()
        elif format == "html":
            return self._generate_html()
        else:
            raise ValueError(f"Unknown format: {format}")

    def save(self, path: Path, format: str | None = None) -> None:
        """Save report to file.

        Args:
            path: Output file path
            format: Output format (inferred from extension if not provided)
        """
        if format is None:
            suffix = path.suffix.lower()
            format = {
                ".json": "json",
                ".md": "markdown",
                ".html": "html",
                ".htm": "html",
            }.get(suffix, "markdown")

        content = self.generate(format)
        with open(path, "w") as f:
            f.write(content)

    def _generate_markdown(self) -> str:
        """Generate Markdown report."""
        lines = []
        summary = self.data.get("summary", {})
        purl = self.data.get("purl", "Unknown")

        # Header
        package_name = summary.get("package_name") or purl
        version = summary.get("version") or ""
        lines.append(f"# Analysis Report: {package_name}")
        if version:
            lines.append(f"**Version:** {version}")
        lines.append("")
        lines.append(f"**Analyzed:** {self.data.get('analyzed_at', 'Unknown')}")
        lines.append(f"**PURL:** `{purl}`")
        lines.append("")

        # Summary section
        lines.append("## Summary")
        lines.append("")

        health_grade = summary.get("health_grade")
        burnout_risk = summary.get("burnout_risk")

        if health_grade:
            lines.append(f"- **Health Grade:** {health_grade}")
        if burnout_risk:
            lines.append(f"- **Burnout Risk:** {burnout_risk}")

        github_url = summary.get("github_url")
        if github_url:
            lines.append(f"- **Repository:** [{github_url}]({github_url})")

        license_info = summary.get("license")
        if license_info:
            lines.append(f"- **License:** {license_info}")

        has_binaries = summary.get("has_binaries", False)
        lines.append(f"- **Contains Binaries:** {'Yes ⚠️' if has_binaries else 'No'}")
        lines.append("")

        # Key Metrics
        key_metrics = summary.get("key_metrics", {})
        if key_metrics:
            lines.append("## Key Metrics")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            for key, value in key_metrics.items():
                display_key = key.replace("_", " ").title()
                lines.append(f"| {display_key} | {value} |")
            lines.append("")

        # Health Score Details
        health_data = self.data.get("health_score", {})
        if health_data:
            lines.append("## Health Score")
            lines.append("")
            score = health_data.get("health_score", 0)
            grade = health_data.get("grade", "?")
            lines.append(f"**Score:** {score}/100 (Grade: {grade})")
            lines.append("")

            # Category breakdown
            categories = health_data.get("categories", {})
            if categories:
                lines.append("### Category Breakdown")
                lines.append("")
                lines.append("| Category | Score | Max | Weight |")
                lines.append("|----------|-------|-----|--------|")
                for name, cat in categories.items():
                    display_name = name.replace("_", " ").title()
                    lines.append(
                        f"| {display_name} | {cat.get('score', 0)} | {cat.get('max', 0)} | {cat.get('weight', 0)} |"
                    )
                lines.append("")

            # Risk factors
            risk_factors = health_data.get("risk_factors", [])
            if risk_factors:
                lines.append("### Risk Factors")
                lines.append("")
                for rf in risk_factors:
                    severity = rf.get("severity", "info")
                    message = rf.get("message", "")
                    emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(
                        severity, "ℹ️"
                    )
                    lines.append(f"- {emoji} **{severity.upper()}:** {message}")
                lines.append("")

            # Recommendations
            recommendations = health_data.get("recommendations", [])
            if recommendations:
                lines.append("### Recommendations")
                lines.append("")
                for rec in recommendations:
                    lines.append(f"- {rec}")
                lines.append("")

        # Burnout Score Details
        burnout_data = self.data.get("burnout_score", {})
        if burnout_data:
            lines.append("## Burnout Risk Assessment")
            lines.append("")
            score = burnout_data.get("burnout_score", 0)
            risk_level = burnout_data.get("risk_level", "unknown")
            lines.append(f"**Score:** {score}/100 (Risk Level: {risk_level})")
            lines.append("")

            components = burnout_data.get("components", {})
            if components:
                lines.append("### Component Breakdown")
                lines.append("")
                lines.append("| Component | Score | Status |")
                lines.append("|-----------|-------|--------|")
                for name, comp in components.items():
                    display_name = name.replace("_", " ").title()
                    status = comp.get("status", "unknown")
                    lines.append(f"| {display_name} | {comp.get('score', 0)} | {status} |")
                lines.append("")

        # Git Metrics
        git_data = self.data.get("git_metrics", {})
        if git_data:
            lines.append("## Git Metrics")
            lines.append("")

            time_windows = git_data.get("time_windows", {})
            for window_name, window in time_windows.items():
                if window:
                    display_name = window_name.replace("_", " ").replace("days", "Days")
                    lines.append(f"### {display_name}")
                    lines.append("")
                    lines.append(f"- **Total Commits:** {window.get('total_commits', 0)}")
                    lines.append(f"- **Unique Contributors:** {window.get('unique_contributors', 0)}")
                    lines.append(f"- **Bus Factor:** {window.get('bus_factor', 0)}")
                    lines.append(f"- **Pony Factor:** {window.get('pony_factor', 0)}")
                    lines.append(f"- **Elephant Factor:** {window.get('elephant_factor', 0)}")
                    lines.append("")

        # GitHub Metrics
        github_data = self.data.get("github_metrics", {})
        if github_data:
            lines.append("## GitHub Metrics")
            lines.append("")

            repo = github_data.get("repository", {})
            if repo:
                lines.append(f"- **Stars:** {repo.get('stars', 0)}")
                lines.append(f"- **Forks:** {repo.get('forks', 0)}")
                lines.append(f"- **Watchers:** {repo.get('watchers', 0)}")
                lines.append("")

            issues = github_data.get("issues", {})
            if issues:
                lines.append("### Issues")
                lines.append("")
                lines.append(f"- **Open:** {issues.get('open_count', 0)}")
                lines.append(f"- **Closed (30d):** {issues.get('closed_30d', 0)}")
                lines.append(f"- **Unresponded Rate (7d):** {issues.get('unresponded_rate_7d', 0):.1f}%")
                lines.append("")

            prs = github_data.get("pull_requests", {})
            if prs:
                lines.append("### Pull Requests")
                lines.append("")
                lines.append(f"- **Open:** {prs.get('open_count', 0)}")
                lines.append(f"- **Merged (30d):** {prs.get('merged_30d', 0)}")
                lines.append(f"- **Avg Merge Time:** {prs.get('avg_merge_hours', 0):.1f} hours")
                lines.append("")

        # Tarball Scan
        tarball_data = self.data.get("tarball_scan", {})
        if tarball_data:
            lines.append("## Tarball Scan")
            lines.append("")

            # License files
            license_files = tarball_data.get("license_files", [])
            if license_files:
                lines.append("### Detected License Files")
                lines.append("")
                for lf in license_files:
                    path = lf.get("path", "")
                    spdx = lf.get("spdx_id") or "Unknown"
                    conf = lf.get("confidence", 0)
                    lines.append(f"- `{path}` - {spdx} ({conf}% confidence)")
                lines.append("")

            # Binaries
            binaries = tarball_data.get("binaries", {})
            if binaries.get("found"):
                lines.append("### Binary Files ⚠️")
                lines.append("")
                binary_files = binaries.get("files", [])
                for bf in binary_files[:10]:  # Limit display
                    lines.append(f"- `{bf.get('path')}` ({bf.get('file_type')})")
                if len(binary_files) > 10:
                    lines.append(f"- ... and {len(binary_files) - 10} more")
                lines.append("")

            # Stats
            lines.append("### Scan Statistics")
            lines.append("")
            lines.append(f"- **Total Files:** {tarball_data.get('file_count', 0)}")
            size_kb = tarball_data.get("total_size_bytes", 0) / 1024
            lines.append(f"- **Total Size:** {size_kb:.1f} KB")
            lines.append(f"- **Scan Method:** {tarball_data.get('scan_method', 'basic')}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Generated by ccda-cli v{self.data.get('analysis_version', '1.0.0')}*")

        return "\n".join(lines)

    def _generate_html(self) -> str:
        """Generate HTML report."""
        summary = self.data.get("summary", {})
        purl = self.data.get("purl", "Unknown")
        package_name = summary.get("package_name") or purl
        version = summary.get("version") or ""

        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Report: {package_name}</title>
    <style>
        :root {{
            --primary: #2563eb;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-700: #374151;
            --gray-900: #111827;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-900);
            background: var(--gray-50);
            padding: 2rem;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            padding: 2rem;
        }}
        h1 {{ color: var(--gray-900); margin-bottom: 0.5rem; }}
        h2 {{ color: var(--gray-700); margin: 2rem 0 1rem; border-bottom: 2px solid var(--gray-200); padding-bottom: 0.5rem; }}
        h3 {{ color: var(--gray-700); margin: 1.5rem 0 0.75rem; }}
        .meta {{ color: var(--gray-700); font-size: 0.9rem; margin-bottom: 1.5rem; }}
        .meta code {{ background: var(--gray-100); padding: 0.2rem 0.4rem; border-radius: 3px; }}
        .score-box {{
            display: inline-flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }}
        .score-box.health {{ background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); }}
        .score-box.burnout {{ background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); }}
        .score-value {{ font-size: 2rem; font-weight: bold; }}
        .score-label {{ font-size: 0.9rem; color: var(--gray-700); }}
        .grade {{
            display: inline-block;
            width: 2rem;
            height: 2rem;
            text-align: center;
            line-height: 2rem;
            border-radius: 50%;
            font-weight: bold;
            color: white;
        }}
        .grade-A {{ background: var(--success); }}
        .grade-B {{ background: #22c55e; }}
        .grade-C {{ background: var(--warning); }}
        .grade-D {{ background: #f59e0b; }}
        .grade-F {{ background: var(--danger); }}
        table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; }}
        th, td {{ text-align: left; padding: 0.75rem; border-bottom: 1px solid var(--gray-200); }}
        th {{ background: var(--gray-50); font-weight: 600; }}
        .risk-critical {{ color: var(--danger); }}
        .risk-high {{ color: #ea580c; }}
        .risk-medium {{ color: var(--warning); }}
        .risk-low {{ color: var(--primary); }}
        ul {{ margin: 0.5rem 0; padding-left: 1.5rem; }}
        li {{ margin: 0.25rem 0; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        footer {{ margin-top: 2rem; padding-top: 1rem; border-top: 1px solid var(--gray-200); color: var(--gray-700); font-size: 0.85rem; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{package_name}</h1>
        <div class="meta">
            <p><strong>Version:</strong> {version or 'N/A'}</p>
            <p><strong>PURL:</strong> <code>{purl}</code></p>
            <p><strong>Analyzed:</strong> {self.data.get('analyzed_at', 'Unknown')}</p>
        </div>
"""

        # Scores section
        health_data = self.data.get("health_score", {})
        burnout_data = self.data.get("burnout_score", {})

        if health_data or burnout_data:
            html += "<h2>Scores</h2>\n<div>\n"
            if health_data:
                score = health_data.get("health_score", 0)
                grade = health_data.get("grade", "?")
                html += f"""
                <div class="score-box health">
                    <div>
                        <div class="score-value">{score}</div>
                        <div class="score-label">Health Score</div>
                    </div>
                    <span class="grade grade-{grade}">{grade}</span>
                </div>
"""
            if burnout_data:
                score = burnout_data.get("burnout_score", 0)
                risk = burnout_data.get("risk_level", "unknown")
                html += f"""
                <div class="score-box burnout">
                    <div>
                        <div class="score-value">{score}</div>
                        <div class="score-label">Burnout Risk ({risk})</div>
                    </div>
                </div>
"""
            html += "</div>\n"

        # Key Metrics
        key_metrics = summary.get("key_metrics", {})
        if key_metrics:
            html += "<h2>Key Metrics</h2>\n<table>\n<tr><th>Metric</th><th>Value</th></tr>\n"
            for key, value in key_metrics.items():
                display_key = key.replace("_", " ").title()
                html += f"<tr><td>{display_key}</td><td>{value}</td></tr>\n"
            html += "</table>\n"

        # Risk factors
        risk_factors = health_data.get("risk_factors", [])
        if risk_factors:
            html += "<h2>Risk Factors</h2>\n<ul>\n"
            for rf in risk_factors:
                severity = rf.get("severity", "info")
                message = rf.get("message", "")
                html += f'<li class="risk-{severity}"><strong>{severity.upper()}:</strong> {message}</li>\n'
            html += "</ul>\n"

        # Recommendations
        recommendations = health_data.get("recommendations", [])
        if recommendations:
            html += "<h2>Recommendations</h2>\n<ul>\n"
            for rec in recommendations:
                html += f"<li>{rec}</li>\n"
            html += "</ul>\n"

        # Tarball scan warnings
        tarball_data = self.data.get("tarball_scan", {})
        binaries = tarball_data.get("binaries", {})
        if binaries.get("found"):
            html += '<h2>⚠️ Binary Files Detected</h2>\n'
            html += "<p>This package contains binary files that should be reviewed:</p>\n<ul>\n"
            for bf in binaries.get("files", [])[:10]:
                html += f"<li><code>{bf.get('path')}</code> - {bf.get('file_type')}</li>\n"
            html += "</ul>\n"

        # Footer
        html += f"""
        <footer>
            Generated by ccda-cli v{self.data.get('analysis_version', '1.0.0')}
        </footer>
    </div>
</body>
</html>
"""
        return html
