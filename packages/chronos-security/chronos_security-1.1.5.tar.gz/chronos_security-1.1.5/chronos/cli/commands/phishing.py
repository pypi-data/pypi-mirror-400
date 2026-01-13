"""
CHRONOS CLI - Phishing Analysis Commands
========================================

Analyze emails for phishing indicators.
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
app = typer.Typer(help="🎣 Phishing detection and analysis")


@app.command("analyze")
def phish_analyze(
    source: Path = typer.Argument(..., help="Email file (.eml) or mailbox (.mbox)", exists=True),
    check_urls: bool = typer.Option(True, "--check-urls/--skip-urls", help="Check URL reputation"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔍 Analyze email(s) for phishing indicators.
    
    Checks:
    - SPF, DKIM, DMARC authentication
    - Sender impersonation patterns
    - Suspicious URLs (URLhaus, VirusTotal)
    - Attachment analysis
    - Urgency language detection
    """
    with error_handler(console):
        from chronos.core.phishing import PhishingAnalyzer
        
        analyzer = PhishingAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing emails...", total=None)
            
            if source.suffix.lower() == ".mbox":
                results = asyncio.run(analyzer.analyze_mbox(source, check_urls=check_urls))
            else:
                result = asyncio.run(analyzer.analyze_file(source, check_urls=check_urls))
                results = [result] if result else []
            
            progress.remove_task(task)
        
        if json_output:
            import json
            output = [r.to_dict() for r in results]
            console.print(json.dumps(output, indent=2))
            return
        
        if not results:
            console.print("[yellow]No emails analyzed[/yellow]")
            return
        
        # Summary for multiple emails
        if len(results) > 1:
            phishing_count = sum(1 for r in results if r.is_phishing)
            suspicious_count = sum(1 for r in results if r.confidence_score >= 0.5 and not r.is_phishing)
            
            console.print(Panel(
                f"[bold]Analyzed:[/bold] {len(results)} emails\n\n"
                f"[red]Phishing Detected: {phishing_count}[/red]\n"
                f"[yellow]Suspicious: {suspicious_count}[/yellow]\n"
                f"[green]Clean: {len(results) - phishing_count - suspicious_count}[/green]",
                title="Analysis Summary",
                border_style="blue",
            ))
        
        # Display each result
        for result in results:
            _display_phishing_result(result)


def _display_phishing_result(result) -> None:
    """Display a single phishing analysis result."""
    if result.is_phishing:
        status = "[bold red]⚠ PHISHING DETECTED[/bold red]"
        border = "red"
    elif result.confidence_score >= 0.5:
        status = "[bold yellow]⚡ SUSPICIOUS[/bold yellow]"
        border = "yellow"
    else:
        status = "[bold green]✓ LIKELY CLEAN[/bold green]"
        border = "green"
    
    # Build indicator list
    indicators_text = ""
    if result.indicators:
        indicator_lines = []
        for ind in sorted(result.indicators, key=lambda x: x.severity, reverse=True):
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(ind.severity, "⚪")
            indicator_lines.append(f"  {sev_icon} [{ind.category}] {ind.description}")
        indicators_text = "\n".join(indicator_lines[:10])
        if len(result.indicators) > 10:
            indicators_text += f"\n  ... and {len(result.indicators) - 10} more"
    
    # URL analysis
    url_text = ""
    if result.url_analyses:
        malicious_urls = [u for u in result.url_analyses if u.is_malicious]
        if malicious_urls:
            url_text = f"\n\n[bold red]Malicious URLs ({len(malicious_urls)}):[/bold red]"
            for url in malicious_urls[:5]:
                url_text += f"\n  • {url.url[:60]}..."
    
    panel_content = (
        f"{status}\n"
        f"[bold]Confidence:[/bold] {result.confidence_score:.0%}\n\n"
        f"[bold]Subject:[/bold] {result.subject or '(no subject)'}\n"
        f"[bold]From:[/bold] {result.sender or 'Unknown'}\n"
        f"[bold]Date:[/bold] {result.headers.date if result.headers else 'Unknown'}\n\n"
        f"[bold]Indicators ({len(result.indicators)}):[/bold]\n"
        f"{indicators_text or '  None detected'}"
        f"{url_text}"
    )
    
    console.print(Panel(
        panel_content,
        title=f"Email Analysis",
        border_style=border,
    ))


@app.command("headers")
def phish_headers(
    email_file: Path = typer.Argument(..., help="Email file (.eml)", exists=True),
) -> None:
    """
    📋 Display email headers with authentication status.
    """
    with error_handler(console):
        from chronos.core.phishing import EmailParser
        
        parser = EmailParser()
        headers = parser.parse_file(email_file)
        
        if not headers:
            console.print("[yellow]Could not parse email headers[/yellow]")
            return
        
        # Authentication status
        auth_results = []
        for auth_type in ["spf", "dkim", "dmarc"]:
            value = getattr(headers, auth_type, None)
            if value == "pass":
                auth_results.append(f"[green]{auth_type.upper()}: ✓ Pass[/green]")
            elif value == "fail":
                auth_results.append(f"[red]{auth_type.upper()}: ✗ Fail[/red]")
            elif value == "none":
                auth_results.append(f"[yellow]{auth_type.upper()}: - None[/yellow]")
            else:
                auth_results.append(f"[dim]{auth_type.upper()}: ? Unknown[/dim]")
        
        table = Table(title="Email Headers")
        table.add_column("Header", style="cyan")
        table.add_column("Value")
        
        table.add_row("From", headers.from_address or "N/A")
        table.add_row("Reply-To", headers.reply_to or "[dim]same as From[/dim]")
        table.add_row("Return-Path", headers.return_path or "N/A")
        table.add_row("To", headers.to_address or "N/A")
        table.add_row("Subject", headers.subject or "N/A")
        table.add_row("Date", headers.date or "N/A")
        table.add_row("Message-ID", headers.message_id or "N/A")
        table.add_row("", "")
        table.add_row("[bold]Authentication[/bold]", "\n".join(auth_results))
        
        if headers.received_chain:
            table.add_row("", "")
            table.add_row("[bold]Received Chain[/bold]", f"{len(headers.received_chain)} hops")
            for i, hop in enumerate(headers.received_chain[:5], 1):
                table.add_row(f"  Hop {i}", hop[:80])
        
        console.print(table)


@app.command("urls")
def phish_urls(
    email_file: Path = typer.Argument(..., help="Email file (.eml)", exists=True),
    check_reputation: bool = typer.Option(True, "--check/--no-check", help="Check URL reputation"),
) -> None:
    """
    🔗 Extract and analyze URLs from email.
    """
    with error_handler(console):
        from chronos.core.phishing import PhishingAnalyzer
        
        analyzer = PhishingAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Extracting and checking URLs...", total=None)
            result = asyncio.run(analyzer.analyze_file(email_file, check_urls=check_reputation))
        
        if not result or not result.url_analyses:
            console.print("[yellow]No URLs found in email[/yellow]")
            return
        
        table = Table(title=f"URLs Found ({len(result.url_analyses)})")
        table.add_column("URL", style="cyan", max_width=50)
        table.add_column("Status")
        table.add_column("Domain", style="dim")
        table.add_column("Details", style="dim")
        
        for url_analysis in result.url_analyses:
            if url_analysis.is_malicious:
                status = "[red]⚠ Malicious[/red]"
            elif url_analysis.is_suspicious:
                status = "[yellow]⚡ Suspicious[/yellow]"
            else:
                status = "[green]✓ Clean[/green]"
            
            # Extract domain
            from urllib.parse import urlparse
            domain = urlparse(url_analysis.url).netloc or "N/A"
            
            details = []
            if url_analysis.urlhaus_match:
                details.append("URLhaus hit")
            if url_analysis.vt_detections:
                details.append(f"VT: {url_analysis.vt_detections} detections")
            
            table.add_row(
                url_analysis.url[:50],
                status,
                domain[:30],
                ", ".join(details) if details else "-",
            )
        
        console.print(table)
        
        # Summary
        malicious = sum(1 for u in result.url_analyses if u.is_malicious)
        suspicious = sum(1 for u in result.url_analyses if u.is_suspicious and not u.is_malicious)
        
        if malicious > 0:
            console.print(f"\n[bold red]⚠ {malicious} malicious URLs detected![/bold red]")
        elif suspicious > 0:
            console.print(f"\n[yellow]⚡ {suspicious} suspicious URLs detected[/yellow]")
        else:
            console.print(f"\n[green]✓ All URLs appear clean[/green]")


@app.command("batch")
def phish_batch(
    directory: Path = typer.Argument(..., help="Directory containing .eml files", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output CSV file"),
    threshold: float = typer.Option(0.7, "--threshold", "-t", help="Phishing confidence threshold"),
) -> None:
    """
    📁 Batch analyze multiple email files.
    """
    with error_handler(console):
        from chronos.core.phishing import PhishingAnalyzer
        
        # Find email files
        email_files = list(directory.glob("*.eml"))
        
        if not email_files:
            console.print(f"[yellow]No .eml files found in {directory}[/yellow]")
            return
        
        analyzer = PhishingAnalyzer()
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Analyzing {len(email_files)} emails...", total=len(email_files))
            
            for email_file in email_files:
                try:
                    result = asyncio.run(analyzer.analyze_file(email_file, check_urls=False))
                    if result:
                        results.append((email_file.name, result))
                except Exception as e:
                    console.print(f"[dim]Error analyzing {email_file.name}: {e}[/dim]")
                
                progress.advance(task)
        
        if not results:
            console.print("[yellow]No emails successfully analyzed[/yellow]")
            return
        
        # Export if requested
        if output:
            import csv
            with open(output, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "File", "Subject", "From", "Is Phishing", "Confidence",
                    "Indicator Count", "Top Indicator"
                ])
                for filename, result in results:
                    top_indicator = result.indicators[0].description if result.indicators else ""
                    writer.writerow([
                        filename,
                        result.subject or "",
                        result.sender or "",
                        result.is_phishing,
                        f"{result.confidence_score:.2f}",
                        len(result.indicators),
                        top_indicator[:50],
                    ])
            console.print(f"[green]✓ Results exported to {output}[/green]\n")
        
        # Summary
        phishing = [(f, r) for f, r in results if r.is_phishing]
        suspicious = [(f, r) for f, r in results if r.confidence_score >= threshold and not r.is_phishing]
        clean = [(f, r) for f, r in results if r.confidence_score < threshold and not r.is_phishing]
        
        console.print(Panel(
            f"[bold]Total Analyzed:[/bold] {len(results)}\n\n"
            f"[red]Phishing: {len(phishing)}[/red]\n"
            f"[yellow]Suspicious (≥{threshold:.0%}): {len(suspicious)}[/yellow]\n"
            f"[green]Clean: {len(clean)}[/green]",
            title="Batch Analysis Results",
            border_style="blue",
        ))
        
        # Show detected phishing
        if phishing:
            table = Table(title="Detected Phishing Emails")
            table.add_column("File", style="cyan")
            table.add_column("Subject")
            table.add_column("From", style="dim")
            table.add_column("Confidence", justify="right", style="red")
            
            for filename, result in phishing[:20]:
                table.add_row(
                    filename[:30],
                    (result.subject or "")[:40],
                    (result.sender or "")[:30],
                    f"{result.confidence_score:.0%}",
                )
            
            console.print(table)
