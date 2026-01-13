"""
CHRONOS CLI - Log Analysis Commands
===================================

Analyze security logs for anomalies and threats.
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
app = typer.Typer(help="📜 Security log analysis and anomaly detection")


@app.command("analyze")
def logs_analyze(
    source: Path = typer.Argument(..., help="Log file or directory to analyze", exists=True),
    log_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Log type: syslog, auth, cloudtrail, nginx, json (auto-detected)"
    ),
    use_baseline: bool = typer.Option(True, "--baseline/--no-baseline", help="Compare against baseline"),
    ml_detection: bool = typer.Option(True, "--ml/--no-ml", help="Use ML anomaly detection"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔍 Analyze logs for anomalies and security threats.
    
    Supports multiple log formats and uses statistical + ML-based
    anomaly detection to identify suspicious patterns.
    """
    with error_handler(console):
        from chronos.core.logs import LogAnalyzer
        
        analyzer = LogAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Parsing logs...", total=None)
            
            if source.is_dir():
                log_files = list(source.glob("*.log")) + list(source.glob("*.json"))
                entries = []
                for f in log_files:
                    entries.extend(analyzer.parse_file(f, log_type))
            else:
                entries = analyzer.parse_file(source, log_type)
            
            progress.remove_task(task)
            
            if not entries:
                console.print("[yellow]No log entries parsed[/yellow]")
                return
            
            console.print(f"[dim]Parsed {len(entries)} log entries[/dim]")
            
            # Run anomaly detection
            task = progress.add_task("Detecting anomalies...", total=None)
            anomalies = analyzer.detect_anomalies(
                entries,
                use_baseline=use_baseline,
                use_ml=ml_detection,
            )
            progress.remove_task(task)
        
        if json_output:
            import json
            output = {
                "entries_analyzed": len(entries),
                "anomalies_found": len(anomalies),
                "anomalies": [a.to_dict() for a in anomalies],
            }
            console.print(json.dumps(output, indent=2))
            return
        
        # Summary panel
        severity_counts = {}
        for a in anomalies:
            severity_counts[a.severity] = severity_counts.get(a.severity, 0) + 1
        
        console.print(Panel(
            f"[bold]Log Entries:[/bold] {len(entries):,}\n"
            f"[bold]Anomalies Found:[/bold] {len(anomalies)}\n\n"
            f"[red]Critical: {severity_counts.get('critical', 0)}[/red]\n"
            f"[orange1]High: {severity_counts.get('high', 0)}[/orange1]\n"
            f"[yellow]Medium: {severity_counts.get('medium', 0)}[/yellow]\n"
            f"[green]Low: {severity_counts.get('low', 0)}[/green]",
            title=f"Analysis: {source.name}",
            border_style="blue",
        ))
        
        if not anomalies:
            console.print("[green]✓ No anomalies detected[/green]")
            return
        
        # Anomalies table
        table = Table(title=f"Detected Anomalies ({len(anomalies)})")
        table.add_column("Time", style="dim")
        table.add_column("Severity")
        table.add_column("Type", style="cyan")
        table.add_column("Description", max_width=50)
        table.add_column("Source", style="dim")
        
        severity_styles = {
            "critical": "[red]CRIT[/red]",
            "high": "[orange1]HIGH[/orange1]",
            "medium": "[yellow]MED[/yellow]",
            "low": "[green]LOW[/green]",
        }
        
        for anomaly in anomalies[:30]:
            time_str = anomaly.timestamp.strftime("%H:%M:%S") if anomaly.timestamp else "N/A"
            sev_display = severity_styles.get(anomaly.severity, anomaly.severity)
            
            table.add_row(
                time_str,
                sev_display,
                anomaly.anomaly_type,
                anomaly.description[:50],
                anomaly.source_ip or "-",
            )
        
        console.print(table)
        
        if len(anomalies) > 30:
            console.print(f"[dim]... and {len(anomalies) - 30} more anomalies[/dim]")


@app.command("baseline")
def logs_baseline(
    source: Path = typer.Argument(..., help="Log file to create baseline from", exists=True),
    name: str = typer.Option("default", "--name", "-n", help="Baseline name"),
    log_type: Optional[str] = typer.Option(None, "--type", "-t", help="Log type"),
) -> None:
    """
    📊 Create a baseline from normal log activity.
    
    The baseline captures typical patterns like:
    - Events per hour
    - Common source IPs
    - Typical user activity
    - Normal error rates
    """
    with error_handler(console):
        from chronos.core.logs import LogAnalyzer
        
        analyzer = LogAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Parsing logs...", total=None)
            entries = analyzer.parse_file(source, log_type)
            progress.remove_task(task)
            
            if not entries:
                console.print("[yellow]No log entries parsed[/yellow]")
                return
            
            task = progress.add_task("Creating baseline...", total=None)
            baseline = analyzer.create_baseline(entries, name=name)
            progress.remove_task(task)
        
        console.print(Panel(
            f"[bold]Baseline Name:[/bold] {name}\n"
            f"[bold]Entries Analyzed:[/bold] {baseline.total_entries:,}\n"
            f"[bold]Time Range:[/bold] {baseline.start_time} to {baseline.end_time}\n\n"
            f"[bold]Statistics:[/bold]\n"
            f"  Events/Hour (avg): {baseline.avg_events_per_hour:.1f}\n"
            f"  Events/Hour (std): {baseline.std_events_per_hour:.1f}\n"
            f"  Unique Sources: {len(baseline.common_sources)}\n"
            f"  Unique Users: {len(baseline.common_users)}\n"
            f"  Error Rate: {baseline.error_rate:.1%}",
            title="Baseline Created",
            border_style="green",
        ))


@app.command("search")
def logs_search(
    source: Path = typer.Argument(..., help="Log file to search", exists=True),
    pattern: str = typer.Argument(..., help="Search pattern (regex supported)"),
    log_type: Optional[str] = typer.Option(None, "--type", "-t", help="Log type"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum results"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    🔎 Search logs with pattern matching.
    """
    import re
    
    with error_handler(console):
        from chronos.core.logs import LogAnalyzer
        
        analyzer = LogAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Parsing and searching...", total=None)
            entries = analyzer.parse_file(source, log_type)
            progress.remove_task(task)
        
        if not entries:
            console.print("[yellow]No log entries parsed[/yellow]")
            return
        
        # Search
        regex = re.compile(pattern, re.IGNORECASE)
        matches = []
        
        for entry in entries:
            if regex.search(entry.raw_message):
                matches.append(entry)
                if len(matches) >= limit:
                    break
        
        if json_output:
            import json
            output = {
                "pattern": pattern,
                "total_entries": len(entries),
                "matches": len(matches),
                "results": [e.to_dict() for e in matches],
            }
            console.print(json.dumps(output, indent=2))
            return
        
        console.print(f"[dim]Found {len(matches)} matches in {len(entries)} entries[/dim]\n")
        
        if not matches:
            console.print(f"[yellow]No matches for pattern: {pattern}[/yellow]")
            return
        
        for entry in matches[:50]:
            time_str = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "N/A"
            
            # Highlight match
            highlighted = regex.sub(
                lambda m: f"[bold yellow]{m.group()}[/bold yellow]",
                entry.raw_message[:200],
            )
            
            console.print(f"[dim]{time_str}[/dim] {highlighted}")
        
        if len(matches) > 50:
            console.print(f"\n[dim]... and {len(matches) - 50} more matches[/dim]")


@app.command("stats")
def logs_stats(
    source: Path = typer.Argument(..., help="Log file to analyze", exists=True),
    log_type: Optional[str] = typer.Option(None, "--type", "-t", help="Log type"),
) -> None:
    """
    📈 Show log statistics and patterns.
    """
    with error_handler(console):
        from chronos.core.logs import LogAnalyzer
        from collections import Counter
        from datetime import timedelta
        
        analyzer = LogAnalyzer()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Analyzing logs...", total=None)
            entries = analyzer.parse_file(source, log_type)
        
        if not entries:
            console.print("[yellow]No log entries parsed[/yellow]")
            return
        
        # Calculate stats
        timestamps = [e.timestamp for e in entries if e.timestamp]
        sources = Counter(e.source_ip for e in entries if e.source_ip)
        users = Counter(e.user for e in entries if e.user)
        levels = Counter(e.level for e in entries if e.level)
        
        time_range = ""
        if timestamps:
            start = min(timestamps)
            end = max(timestamps)
            duration = end - start
            time_range = f"{start} to {end}\n[dim]Duration: {duration}[/dim]"
        
        # Events per hour
        hourly = Counter()
        for entry in entries:
            if entry.timestamp:
                hourly[entry.timestamp.replace(minute=0, second=0, microsecond=0)] += 1
        
        avg_per_hour = sum(hourly.values()) / max(len(hourly), 1)
        
        console.print(Panel(
            f"[bold]Total Entries:[/bold] {len(entries):,}\n"
            f"[bold]Time Range:[/bold] {time_range or 'N/A'}\n"
            f"[bold]Avg Events/Hour:[/bold] {avg_per_hour:.1f}\n\n"
            f"[bold]Unique Sources:[/bold] {len(sources)}\n"
            f"[bold]Unique Users:[/bold] {len(users)}",
            title=f"Statistics: {source.name}",
            border_style="blue",
        ))
        
        # Top sources
        if sources:
            table = Table(title="Top 10 Source IPs")
            table.add_column("IP Address", style="cyan")
            table.add_column("Count", justify="right")
            table.add_column("Percent", justify="right")
            
            for ip, count in sources.most_common(10):
                pct = count / len(entries) * 100
                table.add_row(ip, str(count), f"{pct:.1f}%")
            
            console.print(table)
        
        # Log levels
        if levels:
            table = Table(title="Log Levels")
            table.add_column("Level", style="cyan")
            table.add_column("Count", justify="right")
            
            level_styles = {
                "error": "[red]",
                "warning": "[yellow]",
                "info": "[green]",
                "debug": "[dim]",
            }
            
            for level, count in levels.most_common():
                style = level_styles.get(level.lower(), "")
                end_style = "[/]" if style else ""
                table.add_row(f"{style}{level}{end_style}", str(count))
            
            console.print(table)


@app.command("tail")
def logs_tail(
    source: Path = typer.Argument(..., help="Log file to tail", exists=True),
    lines: int = typer.Option(20, "--lines", "-n", help="Number of lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow new entries"),
) -> None:
    """
    📋 Show recent log entries.
    """
    import time
    
    with error_handler(console):
        from chronos.core.logs import LogAnalyzer
        
        analyzer = LogAnalyzer()
        
        def show_entries():
            entries = analyzer.parse_file(source)
            recent = entries[-lines:] if entries else []
            
            for entry in recent:
                time_str = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "N/A"
                level = entry.level or "INFO"
                
                level_styles = {
                    "error": "[red]ERR[/red]",
                    "warning": "[yellow]WRN[/yellow]",
                    "info": "[green]INF[/green]",
                    "debug": "[dim]DBG[/dim]",
                }
                
                level_display = level_styles.get(level.lower(), level[:3].upper())
                
                console.print(f"[dim]{time_str}[/dim] {level_display} {entry.raw_message[:120]}")
        
        show_entries()
        
        if follow:
            console.print("\n[dim]Following... Press Ctrl+C to stop[/dim]\n")
            last_size = source.stat().st_size
            
            try:
                while True:
                    time.sleep(1)
                    current_size = source.stat().st_size
                    
                    if current_size > last_size:
                        # Read new content
                        with open(source, "r") as f:
                            f.seek(last_size)
                            new_content = f.read()
                        
                        for line in new_content.strip().split("\n"):
                            if line:
                                console.print(f"[cyan]NEW[/cyan] {line[:120]}")
                        
                        last_size = current_size
                        
            except KeyboardInterrupt:
                console.print("\n[dim]Stopped following[/dim]")
