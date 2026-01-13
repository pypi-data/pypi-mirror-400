"""
CHRONOS CLI - Report Generation Commands
========================================

Generate security reports in various formats.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from chronos.cli.utils import error_handler

console = Console()
app = typer.Typer(help="📊 Security report generation")


@app.command("generate")
def report_generate(
    output: Path = typer.Argument(..., help="Output file path"),
    report_format: str = typer.Option(
        "html", "--format", "-f",
        help="Output format: html, markdown, json"
    ),
    audience: str = typer.Option(
        "technical", "--audience", "-a",
        help="Target audience: technical, management, audit"
    ),
    title: str = typer.Option(
        "CHRONOS Security Report", "--title", "-t",
        help="Report title"
    ),
    include_charts: bool = typer.Option(True, "--charts/--no-charts", help="Include charts (HTML only)"),
    days: int = typer.Option(7, "--days", "-d", help="Include data from last N days"),
) -> None:
    """
    📝 Generate a comprehensive security report.
    
    Aggregates findings from all CHRONOS modules:
    - Vulnerability scan results
    - Phishing detections
    - Log anomalies
    - Incident response actions
    """
    with error_handler(console):
        from chronos.core.reports import ReportGenerator, ReportFormat, ReportAudience
        from chronos.core.database import get_db
        from datetime import datetime, timedelta
        
        db = get_db()
        generator = ReportGenerator()
        
        # Map format/audience strings to enums
        format_map = {
            "html": ReportFormat.HTML,
            "markdown": ReportFormat.MARKDOWN,
            "md": ReportFormat.MARKDOWN,
            "json": ReportFormat.JSON,
        }
        
        audience_map = {
            "technical": ReportAudience.TECHNICAL,
            "tech": ReportAudience.TECHNICAL,
            "management": ReportAudience.MANAGEMENT,
            "exec": ReportAudience.MANAGEMENT,
            "audit": ReportAudience.AUDIT,
            "compliance": ReportAudience.AUDIT,
        }
        
        fmt = format_map.get(report_format.lower())
        if not fmt:
            console.print(f"[red]Unknown format: {report_format}[/red]")
            console.print("Valid formats: html, markdown, json")
            raise typer.Exit(1)
        
        aud = audience_map.get(audience.lower())
        if not aud:
            console.print(f"[red]Unknown audience: {audience}[/red]")
            console.print("Valid audiences: technical, management, audit")
            raise typer.Exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Gathering data...", total=None)
            
            # Gather data from database
            cutoff = datetime.now() - timedelta(days=days)
            
            findings = db.get_findings(limit=1000)
            events = db.get_events(limit=500)
            actions = db.get_actions(limit=200)
            
            progress.update(task, description="Generating report...")
            
            # Generate report
            report_content = generator.generate(
                title=title,
                findings=findings,
                events=events,
                actions=actions,
                format=fmt,
                audience=aud,
                include_charts=include_charts and fmt == ReportFormat.HTML,
            )
            
            progress.remove_task(task)
        
        # Write output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report_content)
        
        console.print(Panel(
            f"[green]✓ Report generated successfully[/green]\n\n"
            f"[bold]Output:[/bold] {output.absolute()}\n"
            f"[bold]Format:[/bold] {fmt.value.upper()}\n"
            f"[bold]Audience:[/bold] {aud.value.title()}\n"
            f"[bold]Data Range:[/bold] Last {days} days\n\n"
            f"[bold]Content:[/bold]\n"
            f"  • Findings: {len(findings)}\n"
            f"  • Events: {len(events)}\n"
            f"  • Actions: {len(actions)}",
            title="Report Generated",
            border_style="green",
        ))


@app.command("summary")
def report_summary(
    days: int = typer.Option(7, "--days", "-d", help="Summary for last N days"),
) -> None:
    """
    📋 Show a quick security summary.
    """
    with error_handler(console):
        from chronos.core.database import get_db, Severity
        from datetime import datetime, timedelta
        
        db = get_db()
        cutoff = datetime.now() - timedelta(days=days)
        
        # Gather stats
        findings = db.get_findings(limit=10000)
        events = db.get_events(limit=5000)
        actions = db.get_actions(limit=1000)
        
        # Severity breakdown
        sev_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
        }
        for f in findings:
            if f.severity.value in sev_counts:
                sev_counts[f.severity.value] += 1
        
        # Event types
        from collections import Counter
        event_types = Counter(e.event_type.value for e in events)
        
        # Action status
        action_status = Counter(a.status.value for a in actions)
        
        # Display summary
        console.print(Panel(
            f"[bold]Period:[/bold] Last {days} days\n"
            f"[bold]Generated:[/bold] {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"[bold]Findings ({len(findings)} total):[/bold]\n"
            f"  [red]Critical: {sev_counts['CRITICAL']}[/red]\n"
            f"  [orange1]High: {sev_counts['HIGH']}[/orange1]\n"
            f"  [yellow]Medium: {sev_counts['MEDIUM']}[/yellow]\n"
            f"  [green]Low: {sev_counts['LOW']}[/green]\n\n"
            f"[bold]Events:[/bold] {len(events)}\n"
            f"[bold]IR Actions:[/bold] {len(actions)}",
            title="Security Summary",
            border_style="blue",
        ))
        
        if event_types:
            table = Table(title="Event Types")
            table.add_column("Type", style="cyan")
            table.add_column("Count", justify="right")
            
            for event_type, count in event_types.most_common(10):
                table.add_row(event_type, str(count))
            
            console.print(table)


@app.command("export")
def report_export(
    output: Path = typer.Argument(..., help="Output file path"),
    data_type: str = typer.Option(
        "findings", "--type", "-t",
        help="Data type: findings, events, actions, all"
    ),
    format: str = typer.Option("csv", "--format", "-f", help="Export format: csv, json"),
) -> None:
    """
    💾 Export raw security data.
    """
    with error_handler(console):
        from chronos.core.database import get_db
        import csv
        import json
        
        db = get_db()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Exporting data...", total=None)
            
            data = {}
            
            if data_type in ("findings", "all"):
                data["findings"] = db.get_findings(limit=100000)
            
            if data_type in ("events", "all"):
                data["events"] = db.get_events(limit=100000)
            
            if data_type in ("actions", "all"):
                data["actions"] = db.get_actions(limit=100000)
        
        output.parent.mkdir(parents=True, exist_ok=True)
        
        if format.lower() == "json":
            # Export as JSON
            export_data = {}
            for key, items in data.items():
                export_data[key] = [
                    {
                        "id": i.id,
                        "type": getattr(i, "finding_type", getattr(i, "event_type", getattr(i, "action_name", ""))),
                        "severity": getattr(i, "severity", None),
                        "title": getattr(i, "title", getattr(i, "description", "")),
                        "source": getattr(i, "source", ""),
                        "created_at": i.created_at.isoformat() if i.created_at else None,
                        "details": getattr(i, "details", {}),
                    }
                    for i in items
                ]
            
            output.write_text(json.dumps(export_data, indent=2, default=str))
            
        else:
            # Export as CSV
            rows_written = 0
            
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "ID", "Severity", "Title", "Source", "Created At"])
                
                for data_key, items in data.items():
                    for item in items:
                        writer.writerow([
                            data_key,
                            item.id,
                            getattr(item, "severity", "").value if hasattr(getattr(item, "severity", ""), "value") else "",
                            getattr(item, "title", getattr(item, "description", ""))[:100],
                            getattr(item, "source", ""),
                            item.created_at.isoformat() if item.created_at else "",
                        ])
                        rows_written += 1
        
        total_records = sum(len(items) for items in data.values())
        
        console.print(Panel(
            f"[green]✓ Data exported successfully[/green]\n\n"
            f"[bold]Output:[/bold] {output.absolute()}\n"
            f"[bold]Format:[/bold] {format.upper()}\n"
            f"[bold]Records:[/bold] {total_records}",
            title="Export Complete",
            border_style="green",
        ))


@app.command("templates")
def report_templates() -> None:
    """
    📑 List available report templates.
    """
    templates = [
        ("Executive Summary", "management", "High-level overview for leadership"),
        ("Technical Assessment", "technical", "Detailed findings for security teams"),
        ("Compliance Audit", "audit", "Evidence-based report for auditors"),
        ("Vulnerability Report", "technical", "CVE-focused vulnerability analysis"),
        ("Incident Report", "technical", "Post-incident analysis and timeline"),
    ]
    
    table = Table(title="Available Report Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Audience", style="yellow")
    table.add_column("Description")
    
    for name, audience, desc in templates:
        table.add_row(name, audience, desc)
    
    console.print(table)
    
    console.print("\n[dim]Generate with: chronos report generate output.html --audience <audience>[/dim]")
