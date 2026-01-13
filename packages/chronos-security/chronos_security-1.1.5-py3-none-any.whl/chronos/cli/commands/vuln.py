"""
CHRONOS CLI - Vulnerability Management Commands
===============================================

Import, prioritize, and manage vulnerability findings.
"""

from pathlib import Path
from typing import Optional
import asyncio

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from chronos.cli.utils import error_handler

console = Console()
app = typer.Typer(help="🔓 Vulnerability management and prioritization")


@app.command("import")
def vuln_import(
    source: Path = typer.Argument(..., help="Path to vulnerability report file", exists=True),
    source_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Source type: sarif, trivy, grype, bandit (auto-detected if not specified)"
    ),
    enrich: bool = typer.Option(True, "--enrich/--no-enrich", help="Enrich with threat intel"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    📥 Import vulnerabilities from scanner output.
    
    Supports SARIF, Trivy JSON, Grype JSON, and Bandit JSON formats.
    Automatically enriches with EPSS scores and CISA KEV status.
    """
    with error_handler(console):
        from chronos.core.vuln import VulnerabilityManager
        
        manager = VulnerabilityManager()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Importing vulnerabilities...", total=None)
            vulns = manager.import_from_file(source, source_type)
            progress.remove_task(task)
            
            if enrich and vulns:
                task = progress.add_task("Enriching with threat intel...", total=None)
                vulns = asyncio.run(manager.enrich_vulnerabilities(vulns))
                progress.remove_task(task)
        
        if json_output:
            import json
            console.print(json.dumps([v.to_dict() for v in vulns], indent=2))
            return
        
        if not vulns:
            console.print("[yellow]No vulnerabilities found in import file[/yellow]")
            return
        
        # Sort by priority
        vulns.sort(key=lambda v: v.priority_score, reverse=True)
        
        # Summary stats
        critical = sum(1 for v in vulns if v.severity.upper() == "CRITICAL")
        high = sum(1 for v in vulns if v.severity.upper() == "HIGH")
        medium = sum(1 for v in vulns if v.severity.upper() == "MEDIUM")
        low = sum(1 for v in vulns if v.severity.upper() in ("LOW", "INFO"))
        kev_count = sum(1 for v in vulns if v.in_kev)
        
        console.print(Panel(
            f"[bold]Imported:[/bold] {len(vulns)} vulnerabilities\n\n"
            f"[red]Critical: {critical}[/red] | "
            f"[orange1]High: {high}[/orange1] | "
            f"[yellow]Medium: {medium}[/yellow] | "
            f"[green]Low: {low}[/green]\n\n"
            f"[bold red]CISA KEV:[/bold red] {kev_count} actively exploited",
            title=f"Import Summary - {source.name}",
            border_style="blue",
        ))
        
        # Top priority table
        table = Table(title="Top Priority Vulnerabilities")
        table.add_column("CVE", style="cyan")
        table.add_column("Severity", justify="center")
        table.add_column("CVSS", justify="right")
        table.add_column("EPSS", justify="right")
        table.add_column("KEV", justify="center")
        table.add_column("Priority", justify="right", style="bold")
        table.add_column("Package", style="dim")
        
        severity_styles = {
            "CRITICAL": "[red]CRIT[/red]",
            "HIGH": "[orange1]HIGH[/orange1]",
            "MEDIUM": "[yellow]MED[/yellow]",
            "LOW": "[green]LOW[/green]",
        }
        
        for vuln in vulns[:15]:
            epss_str = f"{vuln.epss_score:.1%}" if vuln.epss_score else "-"
            kev_str = "[red]⚡[/red]" if vuln.in_kev else ""
            sev_display = severity_styles.get(vuln.severity.upper(), vuln.severity)
            
            table.add_row(
                vuln.cve_id or vuln.id[:15],
                sev_display,
                f"{vuln.cvss_score:.1f}" if vuln.cvss_score else "-",
                epss_str,
                kev_str,
                f"{vuln.priority_score:.0f}",
                vuln.package[:20] if vuln.package else "-",
            )
        
        console.print(table)
        
        if len(vulns) > 15:
            console.print(f"\n[dim]... and {len(vulns) - 15} more vulnerabilities[/dim]")


@app.command("list")
def vuln_list(
    severity: Optional[str] = typer.Option(
        None, "--severity", "-s",
        help="Filter by severity: critical, high, medium, low"
    ),
    kev_only: bool = typer.Option(False, "--kev", "-k", help="Show only CISA KEV entries"),
    limit: int = typer.Option(50, "--limit", "-l", help="Maximum results to show"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    📋 List stored vulnerability findings.
    """
    with error_handler(console):
        from chronos.core.database import get_db, Severity
        
        db = get_db()
        
        # Query findings
        severity_enum = None
        if severity:
            severity_enum = Severity(severity.upper())
        
        findings = db.get_findings(
            severity=severity_enum,
            limit=limit,
        )
        
        # Filter KEV if requested
        if kev_only:
            findings = [f for f in findings if f.details.get("in_kev")]
        
        if json_output:
            import json
            output = [
                {
                    "id": f.id,
                    "type": f.finding_type.value,
                    "severity": f.severity.value,
                    "title": f.title,
                    "source": f.source,
                    "details": f.details,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
                for f in findings
            ]
            console.print(json.dumps(output, indent=2))
            return
        
        if not findings:
            console.print("[yellow]No vulnerability findings stored[/yellow]")
            console.print("[dim]Import findings with: chronos vuln import <file>[/dim]")
            return
        
        table = Table(title=f"Vulnerability Findings ({len(findings)} shown)")
        table.add_column("ID", style="dim")
        table.add_column("CVE", style="cyan")
        table.add_column("Severity")
        table.add_column("Title", max_width=40)
        table.add_column("Source", style="dim")
        
        severity_styles = {
            "CRITICAL": "[red]CRIT[/red]",
            "HIGH": "[orange1]HIGH[/orange1]",
            "MEDIUM": "[yellow]MED[/yellow]",
            "LOW": "[green]LOW[/green]",
        }
        
        for f in findings:
            cve = f.details.get("cve_id", "-")
            sev_display = severity_styles.get(f.severity.value, f.severity.value)
            
            table.add_row(
                str(f.id)[:8],
                cve,
                sev_display,
                f.title[:40],
                f.source[:20],
            )
        
        console.print(table)


@app.command("prioritize")
def vuln_prioritize(
    source: Path = typer.Argument(..., help="Path to vulnerability report", exists=True),
    top: int = typer.Option(10, "--top", "-t", help="Show top N priorities"),
    export: Optional[Path] = typer.Option(None, "--export", "-e", help="Export to CSV"),
) -> None:
    """
    🎯 Prioritize vulnerabilities using EPSS, CVSS, and KEV data.
    
    Uses the formula:
    Priority = CVSS * 10 + (EPSS * 30) + KEV * 50 + Ransomware * 20
    """
    with error_handler(console):
        from chronos.core.vuln import VulnerabilityManager
        
        manager = VulnerabilityManager()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Importing and enriching...", total=None)
            vulns = manager.import_from_file(source)
            vulns = asyncio.run(manager.enrich_vulnerabilities(vulns))
            progress.remove_task(task)
        
        if not vulns:
            console.print("[yellow]No vulnerabilities to prioritize[/yellow]")
            return
        
        # Sort by priority
        vulns.sort(key=lambda v: v.priority_score, reverse=True)
        
        # Export if requested
        if export:
            import csv
            with open(export, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "CVE", "Severity", "CVSS", "EPSS", "EPSS Percentile",
                    "In KEV", "Ransomware", "Priority Score", "Package", "Path"
                ])
                for v in vulns:
                    writer.writerow([
                        v.cve_id or v.id,
                        v.severity,
                        v.cvss_score or "",
                        v.epss_score or "",
                        v.epss_percentile or "",
                        v.in_kev,
                        v.ransomware_campaign,
                        v.priority_score,
                        v.package or "",
                        v.file_path or "",
                    ])
            console.print(f"[green]✓ Exported to {export}[/green]")
        
        # Display top priorities
        console.print(Panel(
            "[bold]Priority Scoring Formula:[/bold]\n"
            "  Base: CVSS × 10\n"
            "  + EPSS boost: score × 30\n"
            "  + CISA KEV: +50 points\n"
            "  + Ransomware: +20 points\n\n"
            "[dim]Higher score = more urgent to fix[/dim]",
            title="Prioritization Method",
            border_style="blue",
        ))
        
        table = Table(title=f"Top {top} Priority Vulnerabilities")
        table.add_column("Rank", style="bold", justify="right")
        table.add_column("CVE", style="cyan")
        table.add_column("Severity")
        table.add_column("CVSS", justify="right")
        table.add_column("EPSS %ile", justify="right")
        table.add_column("Flags")
        table.add_column("Score", justify="right", style="bold magenta")
        
        for i, vuln in enumerate(vulns[:top], 1):
            severity_styles = {
                "CRITICAL": "[red]CRIT[/red]",
                "HIGH": "[orange1]HIGH[/orange1]",
                "MEDIUM": "[yellow]MED[/yellow]",
                "LOW": "[green]LOW[/green]",
            }
            
            flags = []
            if vuln.in_kev:
                flags.append("[red]KEV[/red]")
            if vuln.ransomware_campaign:
                flags.append("[red]🔐[/red]")
            if vuln.epss_score and vuln.epss_score > 0.5:
                flags.append("[yellow]EPSS⬆[/yellow]")
            
            percentile = f"{(vuln.epss_percentile or 0) * 100:.0f}%" if vuln.epss_percentile else "-"
            
            table.add_row(
                f"#{i}",
                vuln.cve_id or vuln.id[:12],
                severity_styles.get(vuln.severity.upper(), vuln.severity),
                f"{vuln.cvss_score:.1f}" if vuln.cvss_score else "-",
                percentile,
                " ".join(flags) if flags else "-",
                f"{vuln.priority_score:.0f}",
            )
        
        console.print(table)
        
        # Action recommendations
        kev_vulns = [v for v in vulns if v.in_kev]
        if kev_vulns:
            console.print(Panel(
                f"[bold red]⚠ {len(kev_vulns)} CISA KEV vulnerabilities detected[/bold red]\n\n"
                "These are actively exploited and should be patched immediately.\n"
                "CISA mandates federal agencies patch within the due date.",
                title="Urgent Action Required",
                border_style="red",
            ))


@app.command("enrich")
def vuln_enrich(
    cve_id: str = typer.Argument(..., help="CVE ID to enrich"),
) -> None:
    """
    🔬 Enrich a single CVE with threat intelligence.
    """
    with error_handler(console):
        from chronos.core.intel import ThreatIntelAggregator
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Fetching threat intelligence...", total=None)
            
            aggregator = ThreatIntelAggregator()
            enriched = asyncio.run(aggregator.enrich_cve(cve_id))
        
        # Display enriched data
        panel_parts = [
            f"[bold]CVE:[/bold] {enriched.cve_id}",
            f"[bold]Severity:[/bold] {enriched.severity} (CVSS: {enriched.cvss_score})",
            f"[bold]CVSS Vector:[/bold] {enriched.cvss_vector or 'N/A'}",
            "",
            f"[bold]Description:[/bold]",
            enriched.description[:400] + ("..." if len(enriched.description) > 400 else ""),
        ]
        
        if enriched.epss_score:
            percentile = (enriched.epss_score.percentile or 0) * 100
            panel_parts.extend([
                "",
                f"[bold]EPSS Analysis:[/bold]",
                f"  Probability: {enriched.epss_score.score:.2%}",
                f"  Percentile: Top {100-percentile:.0f}% most likely to be exploited",
            ])
        
        if enriched.kev_entry:
            panel_parts.extend([
                "",
                f"[bold red]⚠ CISA Known Exploited Vulnerability[/bold red]",
                f"  Added: {enriched.kev_entry.date_added}",
                f"  Due Date: {enriched.kev_entry.due_date}",
                f"  Ransomware Use: {'Yes ⚡' if enriched.kev_entry.ransomware_use else 'Unknown'}",
            ])
        
        if enriched.references:
            panel_parts.extend([
                "",
                f"[bold]References:[/bold] {len(enriched.references)} links",
            ])
        
        panel_parts.extend([
            "",
            f"[bold magenta]Priority Score: {enriched.priority_score:.0f}/100[/bold magenta]",
        ])
        
        console.print(Panel(
            "\n".join(panel_parts),
            title=f"[bold]{cve_id} - Enriched Analysis[/bold]",
            border_style="blue",
        ))
