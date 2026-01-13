"""
CHRONOS Report Generator
========================

Generate security reports in multiple formats with charts and
customizable templates for different audiences.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import html
import base64
import io

from chronos.core.database import (
    Finding,
    FindingCategory,
    Severity,
    get_db,
)
from chronos.core.settings import get_settings
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class ReportFormat(str, Enum):
    """Report output formats."""
    HTML = "html"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"  # Requires weasyprint


class ReportAudience(str, Enum):
    """Target audience for report."""
    TECHNICAL = "technical"  # Full details for security team
    MANAGEMENT = "management"  # Executive summary
    AUDIT = "audit"  # Compliance-focused


@dataclass
class ReportSection:
    """Report section content."""
    title: str
    content: str
    severity: Optional[Severity] = None
    chart_data: Optional[Dict[str, Any]] = None


@dataclass
class ReportData:
    """Data for report generation."""
    title: str
    generated_at: datetime = field(default_factory=datetime.now)
    time_period: str = ""
    
    # Summary metrics
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    
    # Detailed findings
    findings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Breakdown by category
    by_category: Dict[str, int] = field(default_factory=dict)
    
    # Trends
    trends: Dict[str, List[int]] = field(default_factory=dict)
    
    # Top issues
    top_cves: List[Dict[str, Any]] = field(default_factory=list)
    top_hosts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "generated_at": self.generated_at.isoformat(),
            "time_period": self.time_period,
            "summary": {
                "total": self.total_findings,
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
            },
            "by_category": self.by_category,
            "top_cves": self.top_cves,
            "top_hosts": self.top_hosts,
            "recommendations": self.recommendations,
            "findings": self.findings,
        }


# =============================================================================
# Chart Generator
# =============================================================================

class ChartGenerator:
    """Generate charts using matplotlib."""
    
    def __init__(self):
        self._has_matplotlib = False
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            self._has_matplotlib = True
            self._plt = plt
        except ImportError:
            logger.warning("matplotlib not available, charts will be disabled")
    
    def severity_pie_chart(self, data: ReportData) -> Optional[str]:
        """Generate severity distribution pie chart as base64 PNG."""
        if not self._has_matplotlib:
            return None
        
        labels = []
        sizes = []
        colors = []
        
        severity_data = [
            ("Critical", data.critical_count, "#dc3545"),
            ("High", data.high_count, "#fd7e14"),
            ("Medium", data.medium_count, "#ffc107"),
            ("Low", data.low_count, "#28a745"),
            ("Info", data.info_count, "#17a2b8"),
        ]
        
        for label, count, color in severity_data:
            if count > 0:
                labels.append(f"{label} ({count})")
                sizes.append(count)
                colors.append(color)
        
        if not sizes:
            return None
        
        fig, ax = self._plt.subplots(figsize=(8, 6))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        ax.set_title('Findings by Severity')
        
        return self._fig_to_base64(fig)
    
    def category_bar_chart(self, data: ReportData) -> Optional[str]:
        """Generate category distribution bar chart as base64 PNG."""
        if not self._has_matplotlib:
            return None
        
        if not data.by_category:
            return None
        
        categories = list(data.by_category.keys())
        counts = list(data.by_category.values())
        
        fig, ax = self._plt.subplots(figsize=(10, 6))
        bars = ax.barh(categories, counts, color='#3498db')
        ax.set_xlabel('Count')
        ax.set_title('Findings by Category')
        
        # Add value labels
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                   str(count), va='center')
        
        self._plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def trend_line_chart(self, trends: Dict[str, List[int]], labels: List[str]) -> Optional[str]:
        """Generate trend line chart as base64 PNG."""
        if not self._has_matplotlib:
            return None
        
        if not trends:
            return None
        
        fig, ax = self._plt.subplots(figsize=(10, 6))
        
        colors = {'critical': '#dc3545', 'high': '#fd7e14', 'medium': '#ffc107'}
        
        for severity, counts in trends.items():
            if any(counts):
                ax.plot(labels, counts, marker='o', label=severity.title(),
                       color=colors.get(severity, '#3498db'))
        
        ax.set_xlabel('Time Period')
        ax.set_ylabel('Count')
        ax.set_title('Finding Trends Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self._plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 PNG string."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_data = base64.b64encode(buf.read()).decode('utf-8')
        self._plt.close(fig)
        return img_data


# =============================================================================
# Report Templates
# =============================================================================

class ReportTemplates:
    """HTML report templates."""
    
    BASE_CSS = """
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        h3 { color: #7f8c8d; }
        .summary-box { display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }
        .stat-card { background: #f8f9fa; border-radius: 8px; padding: 20px; min-width: 150px; 
                     text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2.5em; font-weight: bold; }
        .stat-label { color: #6c757d; font-size: 0.9em; }
        .critical { color: #dc3545; }
        .high { color: #fd7e14; }
        .medium { color: #ffc107; }
        .low { color: #28a745; }
        .info { color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .severity-badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: 500; }
        .severity-critical { background: #f8d7da; color: #721c24; }
        .severity-high { background: #ffe5d0; color: #8a4a1c; }
        .severity-medium { background: #fff3cd; color: #856404; }
        .severity-low { background: #d4edda; color: #155724; }
        .severity-info { background: #d1ecf1; color: #0c5460; }
        .recommendation { background: #e7f3ff; border-left: 4px solid #3498db; padding: 15px; margin: 10px 0; }
        .chart-container { text-align: center; margin: 20px 0; }
        .chart-container img { max-width: 100%; height: auto; }
        .finding-details { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .meta { color: #6c757d; font-size: 0.9em; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #6c757d; font-size: 0.9em; }
        @media print { .no-print { display: none; } }
    </style>
    """
    
    @classmethod
    def technical_html(cls, data: ReportData, charts: Dict[str, str]) -> str:
        """Generate technical report HTML."""
        findings_html = cls._render_findings_table(data.findings, detailed=True)
        recommendations_html = cls._render_recommendations(data.recommendations)
        
        severity_chart = ""
        if charts.get("severity"):
            severity_chart = f'<div class="chart-container"><img src="data:image/png;base64,{charts["severity"]}" alt="Severity Distribution"></div>'
        
        category_chart = ""
        if charts.get("category"):
            category_chart = f'<div class="chart-container"><img src="data:image/png;base64,{charts["category"]}" alt="Category Distribution"></div>'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(data.title)}</title>
    {cls.BASE_CSS}
</head>
<body>
    <h1>{html.escape(data.title)}</h1>
    <p class="meta">Generated: {data.generated_at.strftime('%Y-%m-%d %H:%M:%S')} | Period: {html.escape(data.time_period)}</p>
    
    <h2>Executive Summary</h2>
    <div class="summary-box">
        <div class="stat-card">
            <div class="stat-value">{data.total_findings}</div>
            <div class="stat-label">Total Findings</div>
        </div>
        <div class="stat-card">
            <div class="stat-value critical">{data.critical_count}</div>
            <div class="stat-label">Critical</div>
        </div>
        <div class="stat-card">
            <div class="stat-value high">{data.high_count}</div>
            <div class="stat-label">High</div>
        </div>
        <div class="stat-card">
            <div class="stat-value medium">{data.medium_count}</div>
            <div class="stat-label">Medium</div>
        </div>
        <div class="stat-card">
            <div class="stat-value low">{data.low_count}</div>
            <div class="stat-label">Low</div>
        </div>
    </div>
    
    <h2>Distribution Analysis</h2>
    <div style="display: flex; flex-wrap: wrap; gap: 20px;">
        <div style="flex: 1; min-width: 300px;">
            {severity_chart}
        </div>
        <div style="flex: 1; min-width: 300px;">
            {category_chart}
        </div>
    </div>
    
    {cls._render_top_cves(data.top_cves)}
    
    <h2>Recommendations</h2>
    {recommendations_html}
    
    <h2>Detailed Findings</h2>
    {findings_html}
    
    <div class="footer">
        <p>Report generated by CHRONOS Security Platform</p>
    </div>
</body>
</html>"""
    
    @classmethod
    def management_html(cls, data: ReportData, charts: Dict[str, str]) -> str:
        """Generate executive/management report HTML."""
        severity_chart = ""
        if charts.get("severity"):
            severity_chart = f'<div class="chart-container"><img src="data:image/png;base64,{charts["severity"]}" alt="Severity Distribution"></div>'
        
        # Risk score calculation
        risk_score = min(100, (data.critical_count * 40 + data.high_count * 20 + 
                               data.medium_count * 5 + data.low_count * 1))
        risk_color = "#dc3545" if risk_score >= 70 else "#fd7e14" if risk_score >= 40 else "#28a745"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(data.title)} - Executive Summary</title>
    {cls.BASE_CSS}
</head>
<body>
    <h1>{html.escape(data.title)}</h1>
    <p class="meta">Executive Summary | Generated: {data.generated_at.strftime('%Y-%m-%d')}</p>
    
    <h2>Security Risk Overview</h2>
    <div class="summary-box">
        <div class="stat-card" style="min-width: 200px;">
            <div class="stat-value" style="color: {risk_color};">{risk_score}</div>
            <div class="stat-label">Risk Score (0-100)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{data.total_findings}</div>
            <div class="stat-label">Security Issues Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-value critical">{data.critical_count + data.high_count}</div>
            <div class="stat-label">Urgent Items</div>
        </div>
    </div>
    
    <h2>Key Findings</h2>
    {severity_chart}
    
    <h3>Critical Issues Requiring Immediate Attention</h3>
    {cls._render_critical_summary(data.findings)}
    
    <h2>Recommended Actions</h2>
    {cls._render_recommendations(data.recommendations[:5])}
    
    <div class="footer">
        <p>This is an executive summary. For technical details, please refer to the full technical report.</p>
    </div>
</body>
</html>"""
    
    @classmethod
    def audit_html(cls, data: ReportData, charts: Dict[str, str]) -> str:
        """Generate audit/compliance report HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(data.title)} - Audit Report</title>
    {cls.BASE_CSS}
</head>
<body>
    <h1>{html.escape(data.title)}</h1>
    <p class="meta">Audit Report | Generated: {data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Audit Summary</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Report Period</td><td>{html.escape(data.time_period)}</td></tr>
        <tr><td>Total Findings</td><td>{data.total_findings}</td></tr>
        <tr><td>Critical Findings</td><td>{data.critical_count}</td></tr>
        <tr><td>High Findings</td><td>{data.high_count}</td></tr>
        <tr><td>Medium Findings</td><td>{data.medium_count}</td></tr>
        <tr><td>Low Findings</td><td>{data.low_count}</td></tr>
        <tr><td>Informational</td><td>{data.info_count}</td></tr>
    </table>
    
    <h2>Findings by Category</h2>
    <table>
        <tr><th>Category</th><th>Count</th><th>Percentage</th></tr>
        {''.join(f'<tr><td>{html.escape(cat)}</td><td>{count}</td><td>{count/max(data.total_findings,1)*100:.1f}%</td></tr>' for cat, count in data.by_category.items())}
    </table>
    
    <h2>Complete Findings List</h2>
    {cls._render_findings_table(data.findings, detailed=True)}
    
    <h2>Remediation Recommendations</h2>
    {cls._render_recommendations(data.recommendations)}
    
    <div class="footer">
        <p>This report is intended for audit and compliance purposes.</p>
        <p>Report ID: {data.generated_at.strftime('%Y%m%d%H%M%S')}</p>
    </div>
</body>
</html>"""
    
    @classmethod
    def _render_findings_table(cls, findings: List[Dict], detailed: bool = False) -> str:
        """Render findings as HTML table."""
        if not findings:
            return "<p>No findings to display.</p>"
        
        rows = []
        for f in findings[:100]:  # Limit to 100 for readability
            severity = f.get("severity", "info")
            severity_class = f"severity-{severity}"
            
            title = html.escape(f.get("title", "Unknown")[:100])
            category = html.escape(f.get("category", "Unknown"))
            score = f.get("score", 0)
            
            row = f"""<tr>
                <td><span class="severity-badge {severity_class}">{severity.upper()}</span></td>
                <td>{title}</td>
                <td>{category}</td>
                <td>{score:.1f}</td>
            </tr>"""
            
            if detailed:
                details = f.get("details", {})
                if isinstance(details, dict):
                    detail_str = ", ".join(f"{k}: {v}" for k, v in list(details.items())[:3])
                else:
                    detail_str = str(details)[:200]
                row = f"""<tr>
                    <td><span class="severity-badge {severity_class}">{severity.upper()}</span></td>
                    <td>
                        <strong>{title}</strong>
                        <div class="meta">{html.escape(detail_str)}</div>
                    </td>
                    <td>{category}</td>
                    <td>{score:.1f}</td>
                </tr>"""
            
            rows.append(row)
        
        return f"""<table>
            <thead><tr><th>Severity</th><th>Finding</th><th>Category</th><th>Score</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
        </table>"""
    
    @classmethod
    def _render_recommendations(cls, recommendations: List[str]) -> str:
        """Render recommendations."""
        if not recommendations:
            return "<p>No specific recommendations at this time.</p>"
        
        return "".join(
            f'<div class="recommendation"><strong>{i+1}.</strong> {html.escape(rec)}</div>'
            for i, rec in enumerate(recommendations)
        )
    
    @classmethod
    def _render_top_cves(cls, top_cves: List[Dict]) -> str:
        """Render top CVEs section."""
        if not top_cves:
            return ""
        
        rows = "".join(
            f'<tr><td><a href="https://nvd.nist.gov/vuln/detail/{html.escape(cve["cve_id"])}">{html.escape(cve["cve_id"])}</a></td><td>{cve.get("count", 1)}</td><td>{cve.get("max_score", 0):.1f}</td></tr>'
            for cve in top_cves[:10]
        )
        
        return f"""<h2>Top Vulnerabilities (CVEs)</h2>
        <table>
            <thead><tr><th>CVE ID</th><th>Occurrences</th><th>Max Score</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>"""
    
    @classmethod
    def _render_critical_summary(cls, findings: List[Dict]) -> str:
        """Render summary of critical and high findings."""
        critical_findings = [f for f in findings if f.get("severity") in ("critical", "high")][:5]
        
        if not critical_findings:
            return "<p>No critical or high severity issues found.</p>"
        
        items = "".join(
            f'<li><strong>{html.escape(f.get("title", "Unknown")[:80])}</strong></li>'
            for f in critical_findings
        )
        
        return f"<ul>{items}</ul>"


# =============================================================================
# Report Generator
# =============================================================================

class ReportGenerator:
    """
    Generate security reports from findings data.
    
    Features:
    - Multiple output formats (HTML, Markdown, JSON, PDF)
    - Audience-specific templates (technical, management, audit)
    - Charts and visualizations
    - Custom recommendations
    """
    
    def __init__(self):
        self._db = get_db()
        self._settings = get_settings()
        self._charts = ChartGenerator()
    
    def collect_data(
        self,
        title: str = "Security Assessment Report",
        time_period: str = "Last 7 days",
        since: Optional[datetime] = None,
    ) -> ReportData:
        """
        Collect data from database for report.
        
        Args:
            title: Report title
            time_period: Description of time period
            since: Start datetime for findings
        
        Returns:
            ReportData with collected information
        """
        # Get findings from database
        db_findings = self._db.query_findings(since=since, limit=1000)
        
        # Convert to dict format
        findings = [f.to_dict() for f in db_findings]
        
        # Count by severity
        severity_counts = {
            "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0
        }
        for f in findings:
            sev = f.get("severity", "info")
            if sev in severity_counts:
                severity_counts[sev] += 1
        
        # Count by category
        by_category = {}
        for f in findings:
            cat = f.get("category", "unknown")
            by_category[cat] = by_category.get(cat, 0) + 1
        
        # Get summary from database
        summary = self._db.get_findings_summary(since=since)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(findings, severity_counts)
        
        return ReportData(
            title=title,
            time_period=time_period,
            total_findings=len(findings),
            critical_count=severity_counts["critical"],
            high_count=severity_counts["high"],
            medium_count=severity_counts["medium"],
            low_count=severity_counts["low"],
            info_count=severity_counts["info"],
            findings=findings,
            by_category=by_category,
            top_cves=summary.get("top_cves", []),
            recommendations=recommendations,
        )
    
    def generate(
        self,
        data: ReportData,
        format: ReportFormat = ReportFormat.HTML,
        audience: ReportAudience = ReportAudience.TECHNICAL,
        output_path: Optional[Path] = None,
    ) -> str:
        """
        Generate report in specified format.
        
        Args:
            data: Report data
            format: Output format
            audience: Target audience
            output_path: Path to save report (optional)
        
        Returns:
            Report content as string
        """
        # Generate charts
        charts = {}
        if self._settings.report.include_charts:
            charts["severity"] = self._charts.severity_pie_chart(data)
            charts["category"] = self._charts.category_bar_chart(data)
        
        # Generate report based on format
        if format == ReportFormat.JSON:
            content = json.dumps(data.to_dict(), indent=2)
        elif format == ReportFormat.MARKDOWN:
            content = self._generate_markdown(data, audience)
        elif format == ReportFormat.HTML:
            content = self._generate_html(data, audience, charts)
        else:
            content = self._generate_html(data, audience, charts)
        
        # Save if output path specified
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")
            logger.info(f"Report saved to {output_path}")
        
        return content
    
    def _generate_html(
        self,
        data: ReportData,
        audience: ReportAudience,
        charts: Dict[str, str],
    ) -> str:
        """Generate HTML report."""
        if audience == ReportAudience.MANAGEMENT:
            return ReportTemplates.management_html(data, charts)
        elif audience == ReportAudience.AUDIT:
            return ReportTemplates.audit_html(data, charts)
        else:
            return ReportTemplates.technical_html(data, charts)
    
    def _generate_markdown(
        self,
        data: ReportData,
        audience: ReportAudience,
    ) -> str:
        """Generate Markdown report."""
        lines = [
            f"# {data.title}",
            f"",
            f"**Generated:** {data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Period:** {data.time_period}",
            f"",
            "## Summary",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Findings | {data.total_findings} |",
            f"| Critical | {data.critical_count} |",
            f"| High | {data.high_count} |",
            f"| Medium | {data.medium_count} |",
            f"| Low | {data.low_count} |",
            f"| Info | {data.info_count} |",
            f"",
        ]
        
        if data.by_category:
            lines.extend([
                "## Findings by Category",
                "",
                "| Category | Count |",
                "|----------|-------|",
            ])
            for cat, count in sorted(data.by_category.items(), key=lambda x: -x[1]):
                lines.append(f"| {cat} | {count} |")
            lines.append("")
        
        if data.recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for i, rec in enumerate(data.recommendations, 1):
                lines.append(f"{i}. {rec}")
            lines.append("")
        
        if audience == ReportAudience.TECHNICAL and data.findings:
            lines.extend([
                "## Detailed Findings",
                "",
                "| Severity | Title | Category | Score |",
                "|----------|-------|----------|-------|",
            ])
            for f in data.findings[:50]:
                lines.append(
                    f"| {f.get('severity', 'info').upper()} | "
                    f"{f.get('title', 'Unknown')[:60]} | "
                    f"{f.get('category', 'unknown')} | "
                    f"{f.get('score', 0):.1f} |"
                )
            lines.append("")
        
        lines.extend([
            "---",
            "*Report generated by CHRONOS Security Platform*",
        ])
        
        return "\n".join(lines)
    
    def _generate_recommendations(
        self,
        findings: List[Dict],
        severity_counts: Dict[str, int],
    ) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        if severity_counts.get("critical", 0) > 0:
            recommendations.append(
                "Address all critical severity findings immediately. These represent "
                "significant security risks that could lead to system compromise."
            )
        
        if severity_counts.get("high", 0) > 3:
            recommendations.append(
                f"Prioritize remediation of {severity_counts['high']} high severity findings "
                "within the next sprint cycle."
            )
        
        # Category-specific recommendations
        categories = set(f.get("category") for f in findings)
        
        if "vulnerability" in categories:
            recommendations.append(
                "Implement a vulnerability management program with regular scanning "
                "and prioritized patching based on EPSS and KEV status."
            )
        
        if "phishing" in categories:
            recommendations.append(
                "Enhance email security controls and conduct security awareness training "
                "for employees on phishing recognition."
            )
        
        if "crypto_weakness" in categories:
            recommendations.append(
                "Begin planning migration from deprecated cryptographic algorithms "
                "to quantum-resistant alternatives."
            )
        
        if "secret_exposure" in categories:
            recommendations.append(
                "Implement secrets management solution and scan repositories for "
                "accidentally committed credentials."
            )
        
        if "anomaly" in categories:
            recommendations.append(
                "Review detected anomalies and strengthen monitoring. Consider "
                "implementing SIEM correlation rules for early detection."
            )
        
        if self._settings.report.include_recommendations:
            recommendations.append(
                "Schedule regular security assessments and maintain continuous "
                "monitoring of critical systems."
            )
        
        return recommendations[:10]  # Limit to 10 recommendations
