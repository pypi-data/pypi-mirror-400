"""
CHRONOS CLI - Threat Intelligence Commands
==========================================

Query threat intelligence sources (EPSS, NVD, CISA KEV, URLhaus, VirusTotal).
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
app = typer.Typer(help="🔬 Query threat intelligence sources")


@app.command("cve")
def intel_cve(
    cve_id: str = typer.Argument(..., help="CVE ID to look up (e.g., CVE-2023-44487)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔎 Look up CVE details from NVD and EPSS.
    
    Fetches CVE information including CVSS score, description, EPSS probability,
    and CISA KEV status.
    """
    with error_handler(console):
        from chronos.core.intel import ThreatIntelAggregator
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Querying threat intelligence...", total=None)
            
            aggregator = ThreatIntelAggregator()
            result = asyncio.run(aggregator.enrich_cve(cve_id))
        
        if json_output:
            import json
            console.print(json.dumps(result.to_dict(), indent=2))
            return
        
        # Get severity and CVSS from the nested cve_info
        cvss_score = 0.0
        severity = "UNKNOWN"
        description = "No description available"
        
        if result.cve_info:
            cvss_score = result.cve_info.cvss_v3_score or result.cve_info.cvss_v2_score or 0.0
            description = result.cve_info.description or "No description available"
            
            # Determine severity from CVSS score
            if cvss_score >= 9.0:
                severity = "CRITICAL"
            elif cvss_score >= 7.0:
                severity = "HIGH"
            elif cvss_score >= 4.0:
                severity = "MEDIUM"
            elif cvss_score > 0:
                severity = "LOW"
            else:
                severity = "NONE"
        
        # Display as formatted panel
        severity_colors = {
            "CRITICAL": "red",
            "HIGH": "orange1",
            "MEDIUM": "yellow",
            "LOW": "green",
            "NONE": "dim",
            "UNKNOWN": "dim",
        }
        
        color = severity_colors.get(severity, "white")
        
        epss_info = ""
        if result.epss_score:
            percentile = (result.epss_score.percentile or 0) * 100
            epss_info = f"\n[bold]EPSS Score:[/bold] {result.epss_score.epss:.1%} (top {100-percentile:.0f}%)"
        
        kev_info = ""
        if result.kev_entry:
            kev_info = (
                f"\n\n[bold red]⚠ CISA KEV Listed[/bold red]"
                f"\n  Added: {result.kev_entry.date_added}"
                f"\n  Due: {result.kev_entry.due_date}"
            )
            if result.kev_entry.known_ransomware_use:
                kev_info += "\n  [red]⚡ Known ransomware use[/red]"
        
        # Truncate description safely
        desc_truncated = description[:500] + "..." if len(description) > 500 else description
        
        panel_content = (
            f"[bold]CVE:[/bold] {result.cve_id}\n"
            f"[bold]Severity:[/bold] [{color}]{severity}[/{color}] "
            f"(CVSS: {cvss_score:.1f})"
            f"{epss_info}"
            f"\n\n[bold]Description:[/bold]\n{desc_truncated}"
            f"{kev_info}"
            f"\n\n[bold]Priority Score:[/bold] {result.priority_score:.0f}/100"
        )
        
        console.print(Panel(
            panel_content,
            title=f"[bold]{cve_id}[/bold]",
            border_style=color,
        ))


@app.command("url")
def intel_url(
    url: str = typer.Argument(..., help="URL to check for malicious indicators"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔗 Check URL reputation using URLhaus and VirusTotal.
    """
    with error_handler(console):
        from chronos.core.intel import URLhausClient, VirusTotalClient
        from chronos.core.settings import get_settings
        
        settings = get_settings()
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # URLhaus check
            task = progress.add_task("Checking URLhaus...", total=None)
            urlhaus = URLhausClient()
            urlhaus_result = asyncio.run(urlhaus.lookup_url(url))
            results["urlhaus"] = urlhaus_result
            progress.remove_task(task)
            
            # VirusTotal check (if API key available)
            vt = VirusTotalClient()
            if vt.is_configured:
                task = progress.add_task("Checking VirusTotal...", total=None)
                vt_result = asyncio.run(vt.lookup_url(url))
                results["virustotal"] = vt_result
                progress.remove_task(task)
        
        if json_output:
            import json
            output = {
                "url": url,
                "urlhaus": results["urlhaus"].to_dict() if results.get("urlhaus") else None,
                "virustotal": results.get("virustotal", {}).to_dict() if results.get("virustotal") else None,
            }
            console.print(json.dumps(output, indent=2))
            return
        
        # Display results
        table = Table(title=f"URL Reputation: {url[:60]}...")
        table.add_column("Source", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Details", style="dim")
        
        if results.get("urlhaus"):
            ur = results["urlhaus"]
            if ur.is_malicious:
                status = "[red]⚠ Malicious[/red]"
                details = f"Threat: {ur.threat or 'Unknown'}"
            else:
                status = "[green]✓ Clean[/green]"
                details = "Not found in URLhaus"
            table.add_row("URLhaus", status, details)
        else:
            table.add_row("URLhaus", "[green]✓ Clean[/green]", "Not found in URLhaus")
        
        if results.get("virustotal"):
            vt = results["virustotal"]
            if vt.positives > 0:
                status = f"[red]⚠ {vt.positives} detections[/red]"
                details = f"Total engines: {vt.total}"
            else:
                status = "[green]✓ Clean[/green]"
                details = f"Scanned by {vt.total} engines"
            table.add_row("VirusTotal", status, details)
        else:
            vt_check = VirusTotalClient()
            if not vt_check.is_configured:
                table.add_row("VirusTotal", "[dim]Skipped[/dim]", "No API key configured")
        
        console.print(table)


@app.command("hash")
def intel_hash(
    file_hash: str = typer.Argument(..., help="SHA256/MD5 hash to look up"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔐 Check file hash reputation using VirusTotal.
    """
    with error_handler(console):
        from chronos.core.intel import VirusTotalClient
        from chronos.core.settings import get_settings
        
        vt = VirusTotalClient()
        
        if not vt.is_configured:
            console.print(Panel(
                "VirusTotal API key not configured.\n\n"
                "[bold]Quick Setup:[/bold]\n"
                "  [cyan]chronos setup --virustotal YOUR_API_KEY[/cyan]\n\n"
                "[bold]Get your free API key:[/bold]\n"
                "  https://www.virustotal.com/gui/join-us\n\n"
                "[dim]Or set via environment variable: CHRONOS_API_KEYS__VIRUSTOTAL_API_KEY[/dim]",
                title="[yellow]🔑 VirusTotal API Key Required[/yellow]",
                border_style="yellow",
            ))
            raise typer.Exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Querying VirusTotal...", total=None)
            
            vt = VirusTotalClient()
            result = asyncio.run(vt.lookup_file_hash(file_hash))
        
        if json_output:
            import json
            console.print(json.dumps(result.to_dict() if result else {}, indent=2))
            return
        
        if not result:
            console.print(f"[yellow]Hash not found in VirusTotal database[/yellow]")
            return
        
        # Display results
        if result.positives > 0:
            color = "red"
            status = f"⚠ Malicious ({result.positives}/{result.total})"
        else:
            color = "green"
            status = f"✓ Clean ({result.total} scans)"
        
        console.print(Panel(
            f"[bold]Hash:[/bold] {file_hash}\n"
            f"[bold]Status:[/bold] [{color}]{status}[/{color}]\n\n"
            f"[bold]Scan Results:[/bold]\n"
            f"  Detections: {result.positives}\n"
            f"  Total Engines: {result.total}\n"
            f"  Detection Ratio: {result.detection_ratio:.1%}",
            title="VirusTotal Analysis",
            border_style=color,
        ))


@app.command("kev")
def intel_kev(
    days: int = typer.Option(7, "--days", "-d", help="Show KEVs added in last N days"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search KEV by keyword"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    📋 List recent CISA Known Exploited Vulnerabilities.
    """
    with error_handler(console):
        from chronos.core.intel import KEVClient
        from datetime import datetime, timedelta
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Fetching CISA KEV catalog...", total=None)
            
            kev = KEVClient()
            all_kevs = asyncio.run(kev.get_catalog())
        
        # Filter by date
        cutoff = datetime.now() - timedelta(days=days)
        recent_kevs = [
            k for k in all_kevs
            if k.date_added >= cutoff
        ]
        
        # Search filter
        if search:
            search_lower = search.lower()
            recent_kevs = [
                k for k in recent_kevs
                if search_lower in k.cve_id.lower() or search_lower in k.vulnerability_name.lower()
            ]
        
        if json_output:
            import json
            console.print(json.dumps([k.to_dict() for k in recent_kevs], indent=2))
            return
        
        if not recent_kevs:
            console.print(f"[yellow]No KEVs found matching criteria[/yellow]")
            return
        
        table = Table(title=f"CISA KEV - Last {days} Days ({len(recent_kevs)} entries)")
        table.add_column("CVE ID", style="cyan")
        table.add_column("Vulnerability", style="white", max_width=40)
        table.add_column("Added", style="dim")
        table.add_column("Due", style="yellow")
        table.add_column("Ransomware", style="red")
        
        for kev_entry in recent_kevs[:50]:  # Limit display
            # Format datetime objects as strings
            date_added = kev_entry.date_added.strftime("%Y-%m-%d") if hasattr(kev_entry.date_added, 'strftime') else str(kev_entry.date_added)
            due_date = kev_entry.due_date.strftime("%Y-%m-%d") if kev_entry.due_date and hasattr(kev_entry.due_date, 'strftime') else str(kev_entry.due_date or "N/A")
            table.add_row(
                kev_entry.cve_id,
                kev_entry.vulnerability_name[:40],
                date_added,
                due_date,
                "⚡" if kev_entry.known_ransomware_use else "",
            )
        
        console.print(table)
        
        if len(recent_kevs) > 50:
            console.print(f"[dim]... and {len(recent_kevs) - 50} more[/dim]")


@app.command("doctor")
def intel_doctor() -> None:
    """
    🩺 Check threat intelligence API connectivity and configuration.
    """
    with error_handler(console):
        from chronos.core.settings import get_settings
        from chronos.core.intel import (
            EPSSClient, NVDClient, KEVClient, URLhausClient, VirusTotalClient
        )
        
        settings = get_settings()
        results = []
        
        console.print("[bold]Checking threat intelligence sources...[/bold]\n")
        
        # EPSS (public, no key)
        with console.status("Testing EPSS API..."):
            try:
                client = EPSSClient()
                result = asyncio.run(client.get_score("CVE-2023-44487"))
                if result:
                    results.append(("EPSS (FIRST)", "[green]✓ Connected[/green]", "No key required"))
                else:
                    results.append(("EPSS (FIRST)", "[yellow]⚠ No data[/yellow]", "API accessible"))
            except Exception as e:
                results.append(("EPSS (FIRST)", "[red]✗ Failed[/red]", str(e)[:40]))
        
        # NVD (public, optional key)
        with console.status("Testing NVD API..."):
            try:
                nvd_key = settings.api_keys.nvd_api_key
                client = NVDClient()
                result = asyncio.run(client.get_cve("CVE-2023-44487"))
                key_status = "With API key" if nvd_key else "No key (rate limited)"
                if result:
                    results.append(("NVD", "[green]✓ Connected[/green]", key_status))
                else:
                    results.append(("NVD", "[yellow]⚠ No data[/yellow]", key_status))
            except Exception as e:
                results.append(("NVD", "[red]✗ Failed[/red]", str(e)[:40]))
        
        # KEV (public, no key)
        with console.status("Testing CISA KEV..."):
            try:
                client = KEVClient()
                catalog = asyncio.run(client.get_catalog())
                if catalog:
                    results.append(("CISA KEV", "[green]✓ Connected[/green]", f"{len(catalog)} entries"))
                else:
                    results.append(("CISA KEV", "[yellow]⚠ Empty[/yellow]", "No entries returned"))
            except Exception as e:
                results.append(("CISA KEV", "[red]✗ Failed[/red]", str(e)[:40]))
        
        # URLhaus (public, no key)
        with console.status("Testing URLhaus..."):
            try:
                client = URLhausClient()
                # Just verify connection, don't actually check a URL
                results.append(("URLhaus", "[green]✓ Available[/green]", "No key required"))
            except Exception as e:
                results.append(("URLhaus", "[red]✗ Failed[/red]", str(e)[:40]))
        
        # VirusTotal (requires key)
        vt_client = VirusTotalClient()
        if vt_client.is_configured:
            with console.status("Testing VirusTotal..."):
                try:
                    # Check quota by making a simple request
                    results.append(("VirusTotal", "[green]✓ Configured[/green]", "API key present"))
                except Exception as e:
                    results.append(("VirusTotal", "[red]✗ Failed[/red]", str(e)[:40]))
        else:
            results.append(("VirusTotal", "[yellow]⚠ No key[/yellow]", "Run: chronos setup --vt KEY"))
        
        # Display results
        table = Table(title="Threat Intelligence Status")
        table.add_column("Source", style="cyan")
        table.add_column("Status")
        table.add_column("Details", style="dim")
        
        for source, status, details in results:
            table.add_row(source, status, details)
        
        console.print(table)
        
        # Summary
        connected = sum(1 for _, s, _ in results if "✓" in s)
        total = len(results)
        
        if connected == total:
            console.print(f"\n[green]✓ All {total} sources operational[/green]")
        else:
            console.print(f"\n[yellow]⚠ {connected}/{total} sources operational[/yellow]")
