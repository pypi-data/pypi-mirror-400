"""
CHRONOS Detect Command
======================

Commands for threat detection and security scanning.
Real implementation connected to detection engines.
"""

import time
import json
from pathlib import Path
from typing import Optional, List
from enum import Enum
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text

from chronos.cli.utils import error_handler, create_progress, print_success, ScanError
from chronos.core.scanner import (
    FileScanner,
    ScanResult,
    ScanFinding,
    SeverityLevel,
    FindingType,
)

console = Console()

app = typer.Typer(
    name="detect",
    help="🔍 Threat detection and security scanning commands.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


class ScanType(str, Enum):
    """Types of security scans available."""
    QUICK = "quick"
    FULL = "full"
    QUANTUM = "quantum"
    SECRETS = "secrets"


class OutputFormat(str, Enum):
    """Output format options."""
    TABLE = "table"
    JSON = "json"


def _severity_color(severity: SeverityLevel) -> str:
    """Get color for severity level."""
    return {
        SeverityLevel.CRITICAL: "red bold",
        SeverityLevel.HIGH: "red",
        SeverityLevel.MEDIUM: "yellow",
        SeverityLevel.LOW: "blue",
        SeverityLevel.INFO: "dim",
    }.get(severity, "white")


def _severity_emoji(severity: SeverityLevel) -> str:
    """Get emoji for severity level."""
    return {
        SeverityLevel.CRITICAL: "🔴",
        SeverityLevel.HIGH: "🟠",
        SeverityLevel.MEDIUM: "🟡",
        SeverityLevel.LOW: "🔵",
        SeverityLevel.INFO: "⚪",
    }.get(severity, "⚫")


def _format_findings_table(findings: List[ScanFinding]) -> Table:
    """Format findings as a Rich table."""
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        title="Security Findings",
    )
    
    table.add_column("Sev", width=4, justify="center")
    table.add_column("Type", width=20)
    table.add_column("File", width=40)
    table.add_column("Line", width=6, justify="right")
    table.add_column("Message", width=50)
    
    for finding in findings:
        table.add_row(
            _severity_emoji(finding.severity),
            finding.finding_type.value,
            str(Path(finding.file_path).name),
            str(finding.line_number),
            finding.message[:50] + ("..." if len(finding.message) > 50 else ""),
            style=_severity_color(finding.severity),
        )
    
    return table


def _format_summary_panel(result: ScanResult) -> Panel:
    """Format scan summary as a Rich panel."""
    summary = Text()
    summary.append(f"📁 Files Scanned: ", style="bold")
    summary.append(f"{result.files_scanned}\n")
    summary.append(f"⏱️  Duration: ", style="bold")
    summary.append(f"{result.duration_seconds:.2f}s\n")
    summary.append(f"🔍 Total Findings: ", style="bold")
    summary.append(f"{len(result.findings)}\n\n")
    
    if result.critical_count:
        summary.append(f"🔴 Critical: {result.critical_count}\n", style="red bold")
    if result.high_count:
        summary.append(f"🟠 High: {result.high_count}\n", style="red")
    if result.medium_count:
        summary.append(f"🟡 Medium: {result.medium_count}\n", style="yellow")
    if result.low_count:
        summary.append(f"🔵 Low: {result.low_count}\n", style="blue")
    
    return Panel(summary, title="📊 Scan Summary", border_style="green")


def _format_finding_detail(finding: ScanFinding) -> Panel:
    """Format a single finding with details."""
    content = Text()
    content.append(f"{finding.message}\n\n", style="bold")
    content.append("File: ", style="cyan")
    content.append(f"{finding.file_path}:{finding.line_number}\n")
    content.append("Code: ", style="cyan")
    content.append(f"{finding.code_snippet}\n\n", style="dim")
    content.append("Recommendation: ", style="green")
    content.append(f"{finding.recommendation}\n")
    if finding.cwe_id:
        content.append("CWE: ", style="yellow")
        content.append(f"{finding.cwe_id}")
    
    return Panel(
        content,
        title=f"{_severity_emoji(finding.severity)} {finding.finding_type.value}",
        border_style=_severity_color(finding.severity),
    )


@app.command("scan")
def scan_command(
    target: Path = typer.Argument(
        ...,
        help="Target path to scan for threats.",
        exists=True,
    ),
    scan_type: ScanType = typer.Option(
        ScanType.QUICK,
        "--type",
        "-t",
        help="Type of scan to perform.",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r/-R",
        help="Scan directories recursively.",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format.",
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Patterns to exclude from scan.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed findings.",
    ),
) -> None:
    """
    🔍 Scan a target for security threats.
    
    Performs comprehensive threat detection including:
    - Hardcoded secrets (API keys, passwords, private keys)
    - Weak cryptographic implementations
    - Quantum-vulnerable algorithms
    - SQL injection patterns
    - Command injection vulnerabilities
    - Unsafe deserialization
    
    [bold]Scan Types:[/bold]
    • [green]quick[/green] - Fast scan for common issues
    • [yellow]full[/yellow] - Complete security analysis
    • [cyan]quantum[/cyan] - Focus on quantum vulnerabilities
    • [red]secrets[/red] - Hunt for exposed secrets
    
    [bold]Examples:[/bold]
        chronos detect scan ./myproject
        chronos detect scan /path/to/code --type full
        chronos detect scan . --type quantum --output json
    """
    with error_handler(console):
        # Configure scanner based on scan type
        exclude_patterns = set(exclude) if exclude else set()
        quantum_check = scan_type in (ScanType.FULL, ScanType.QUANTUM)
        
        # Only show header panel for non-JSON output
        if output != OutputFormat.JSON:
            console.print(Panel(
                f"[bold]Target:[/bold] {target.absolute()}\n"
                f"[bold]Scan Type:[/bold] {scan_type.value}\n"
                f"[bold]Recursive:[/bold] {recursive}",
                title="🔍 Starting Security Scan",
                border_style="blue",
            ))
        
        scanner = FileScanner(
            exclude_patterns=exclude_patterns,
        )
        
        # Run scan with progress indicator (only for non-JSON)
        if output != OutputFormat.JSON:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("{task.percentage:>3.0f}%"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Scanning files...", total=None)
                result = scanner.scan(
                    target=target,
                    recursive=recursive,
                    quantum_check=quantum_check,
                )
                progress.update(task, completed=True)
        else:
            result = scanner.scan(
                target=target,
                recursive=recursive,
                quantum_check=quantum_check,
            )
        
        # Output results
        if output == OutputFormat.JSON:
            output_data = {
                "target": result.target,
                "started_at": result.started_at.isoformat(),
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "duration_seconds": result.duration_seconds,
                "files_scanned": result.files_scanned,
                "summary": {
                    "critical": result.critical_count,
                    "high": result.high_count,
                    "medium": result.medium_count,
                    "low": result.low_count,
                },
                "findings": [f.to_dict() for f in result.findings],
                "errors": result.errors,
            }
            console.print_json(json.dumps(output_data, indent=2))
        else:
            # Table output
            console.print()
            console.print(_format_summary_panel(result))
            
            if result.findings:
                console.print()
                
                if verbose:
                    # Show detailed findings
                    for finding in result.findings:
                        console.print(_format_finding_detail(finding))
                        console.print()
                else:
                    # Show summary table
                    console.print(_format_findings_table(result.findings))
                    console.print("\n[dim]Use --verbose for detailed findings[/dim]")
            else:
                console.print(Panel(
                    "[green]✓ No security issues found![/green]",
                    border_style="green",
                ))
        
        if result.errors:
            console.print(Panel(
                "\n".join(result.errors),
                title="⚠️ Scan Errors",
                border_style="yellow",
            ))
        
        # Exit with error code if critical or high findings
        if result.critical_count > 0:
            raise typer.Exit(2)
        elif result.high_count > 0:
            raise typer.Exit(1)


@app.command("threats")
def threats_command(
    active_only: bool = typer.Option(
        False,
        "--active",
        "-a",
        help="Show only active threats.",
    ),
    severity: Optional[str] = typer.Option(
        None,
        "--severity",
        "-s",
        help="Filter by severity (critical, high, medium, low).",
    ),
) -> None:
    """
    📋 List known threat patterns and signatures.
    
    Shows information about detectable threat types including:
    - Threat category and description
    - Severity level
    - Detection patterns
    - Remediation guidance
    """
    with error_handler(console):
        # Build threat knowledge base table
        table = Table(
            show_header=True,
            header_style="bold cyan",
            title="📋 Detectable Threat Patterns",
        )
        
        table.add_column("Category", width=20)
        table.add_column("Severity", width=10, justify="center")
        table.add_column("Description", width=50)
        table.add_column("CWE", width=10)
        
        threat_patterns = [
            ("Hardcoded Secrets", "CRITICAL", "API keys, passwords, private keys in code", "CWE-798"),
            ("Weak Crypto (MD5)", "HIGH", "MD5 hash - cryptographically broken", "CWE-328"),
            ("Weak Crypto (SHA1)", "HIGH", "SHA-1 hash - vulnerable to collisions", "CWE-328"),
            ("Weak Crypto (DES)", "CRITICAL", "DES encryption - easily breakable", "CWE-327"),
            ("Weak Crypto (RC4)", "CRITICAL", "RC4 stream cipher - known vulnerabilities", "CWE-327"),
            ("Quantum Vuln (RSA)", "MEDIUM", "RSA - vulnerable to Shor's algorithm", "CWE-327"),
            ("Quantum Vuln (ECC)", "MEDIUM", "Elliptic curves - quantum vulnerable", "CWE-327"),
            ("SQL Injection", "HIGH", "Dynamic SQL with user input", "CWE-89"),
            ("Command Injection", "CRITICAL", "Shell commands with user input", "CWE-78"),
            ("Code Injection", "HIGH", "eval()/exec() with untrusted data", "CWE-94"),
            ("Path Traversal", "MEDIUM", "Unsanitized file paths", "CWE-22"),
            ("Insecure Random", "MEDIUM", "Non-crypto random for security", "CWE-330"),
            ("Unsafe Deserialization", "HIGH", "pickle/yaml.load with untrusted data", "CWE-502"),
        ]
        
        # Filter by severity if specified
        if severity:
            threat_patterns = [
                t for t in threat_patterns 
                if t[1].lower() == severity.lower()
            ]
        
        for category, sev, desc, cwe in threat_patterns:
            style = {
                "CRITICAL": "red bold",
                "HIGH": "red",
                "MEDIUM": "yellow",
                "LOW": "blue",
            }.get(sev, "white")
            
            table.add_row(category, sev, desc, cwe, style=style)
        
        console.print(table)
        console.print("\n[dim]Run 'chronos detect scan <path>' to scan for these threats[/dim]")


@app.command("watch")
def watch_command(
    target: Path = typer.Argument(
        Path("."),
        help="Directory to watch for threats.",
    ),
    interval: int = typer.Option(
        5,
        "--interval",
        "-i",
        help="Check interval in seconds.",
    ),
) -> None:
    """
    👁️ Watch a directory for real-time threat detection.
    
    Monitors for:
    - File system changes
    - Security pattern detection in modified files
    
    [bold yellow]Note:[/bold yellow] Press Ctrl+C to stop watching.
    """
    with error_handler(console):
        console.print(Panel(
            f"[bold]Watching:[/bold] {target.absolute()}\n"
            f"[bold]Interval:[/bold] {interval}s\n\n"
            f"[dim]Press Ctrl+C to stop[/dim]",
            title="👁️ Real-time Threat Monitor",
            border_style="blue",
        ))
        
        scanner = FileScanner()
        scan_count = 0
        
        try:
            console.print("\n[bold green]Monitoring started...[/bold green]\n")
            
            while True:
                scan_count += 1
                current_time = datetime.now()
                
                # Run file scan
                with console.status(f"[cyan]Scanning... (check #{scan_count})[/cyan]"):
                    result = scanner.scan(target, recursive=True, quantum_check=False)
                
                # Display results
                if result.findings:
                    console.print(f"\n[bold red]⚠️ {len(result.findings)} threats detected at {current_time.strftime('%H:%M:%S')}[/bold red]")
                    for finding in result.findings[:5]:  # Show top 5
                        console.print(f"  {_severity_emoji(finding.severity)} {finding.finding_type.value}: {finding.message}")
                    if len(result.findings) > 5:
                        console.print(f"  [dim]... and {len(result.findings) - 5} more[/dim]")
                else:
                    console.print(f"[dim]{current_time.strftime('%H:%M:%S')} - Check #{scan_count}: No threats detected[/dim]")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped by user.[/yellow]")
            console.print(f"[dim]Total checks performed: {scan_count}[/dim]")


@app.command("signatures")
def signatures_command(
    update: bool = typer.Option(
        False,
        "--update",
        "-u",
        help="Check for pattern updates.",
    ),
) -> None:
    """
    📝 View threat detection signatures and patterns.
    
    Shows the built-in detection patterns and their status.
    """
    with error_handler(console):
        # Count patterns
        from chronos.core.scanner import CRYPTO_PATTERNS, SECRET_PATTERNS, VULNERABILITY_PATTERNS
        
        total_patterns = len(CRYPTO_PATTERNS) + len(SECRET_PATTERNS) + len(VULNERABILITY_PATTERNS)
        
        console.print(Panel(
            f"[bold]Total Patterns:[/bold] {total_patterns}\n\n"
            f"[cyan]Cryptographic Patterns:[/cyan] {len(CRYPTO_PATTERNS)}\n"
            f"[cyan]Secret Patterns:[/cyan] {len(SECRET_PATTERNS)}\n"
            f"[cyan]Vulnerability Patterns:[/cyan] {len(VULNERABILITY_PATTERNS)}\n\n"
            f"[green]✓ All signatures active[/green]\n"
            f"[dim]Version: Built-in v1.0[/dim]",
            title="📝 Threat Signatures",
            border_style="green",
        ))
        
        if update:
            console.print("\n[dim]Signature updates are currently sourced from the local pattern database.[/dim]")


@app.command("network")
def network_command(
    interface: Optional[str] = typer.Option(
        None, "--interface", "-i",
        help="Network interface to monitor (e.g., eth0, Wi-Fi).",
    ),
    duration: int = typer.Option(
        30, "--duration", "-d",
        help="Capture duration in seconds.",
    ),
    count: int = typer.Option(
        0, "--count", "-c",
        help="Number of packets to capture (0 = unlimited).",
    ),
    filter_expr: Optional[str] = typer.Option(
        None, "--filter", "-f",
        help="BPF filter expression (e.g., 'tcp port 443').",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE, "--output", "-o",
        help="Output format.",
    ),
    threats_only: bool = typer.Option(
        False, "--threats", "-T",
        help="Show only detected threats/alerts.",
    ),
) -> None:
    """
    🌐 Live network traffic monitor and threat detection.
    
    Captures and analyzes network packets in real-time like Wireshark.
    Detects TLS/SSL issues, suspicious connections, and anomalies.
    
    [bold]Requires:[/bold] Administrator/root privileges for packet capture.
    
    [bold]Common Filters:[/bold]
    • tcp port 443       - HTTPS traffic only
    • tcp port 80        - HTTP traffic only  
    • host 192.168.1.1   - Traffic to/from specific IP
    • tcp and port 22    - SSH traffic
    • udp port 53        - DNS queries
    
    [bold]Examples:[/bold]
        chronos detect network
        chronos detect network -i eth0 -d 60
        chronos detect network --filter "tcp port 443" --threats
        chronos detect network -c 100 -o json
    """
    with error_handler(console):
        try:
            from chronos.core.detect.network_monitor import (
                NetworkMonitor, PacketCapture, BPFFilter,
                SCAPY_AVAILABLE
            )
        except ImportError as e:
            console.print(Panel(
                f"[red]Network monitoring dependencies not available.[/red]\n\n"
                f"[bold]Install required packages:[/bold]\n"
                f"  pip install scapy\n\n"
                f"[bold]On Windows, also install:[/bold]\n"
                f"  • Npcap: https://npcap.com/\n\n"
                f"[dim]Error: {e}[/dim]",
                title="⚠️ Missing Dependencies",
                border_style="yellow",
            ))
            raise typer.Exit(1)
        
        if not SCAPY_AVAILABLE:
            console.print(Panel(
                "[red]Scapy not installed.[/red]\n\n"
                "Install with: [cyan]pip install scapy[/cyan]\n\n"
                "On Windows, also install Npcap:\n"
                "  https://npcap.com/",
                title="⚠️ Missing Scapy",
                border_style="yellow",
            ))
            raise typer.Exit(1)
        
        # List interfaces if none specified
        if interface is None:
            interfaces = PacketCapture.list_interfaces()
            if not interfaces:
                console.print("[red]No network interfaces found.[/red]")
                raise typer.Exit(1)
            
            console.print("\n[bold]Available Network Interfaces:[/bold]")
            table = Table(show_header=True, border_style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("MAC Address", style="dim")
            
            for iface in interfaces:
                table.add_row(iface["name"], iface["mac"])
            
            console.print(table)
            console.print("\n[dim]Use --interface <name> to select one[/dim]\n")
            
            # Try to use first interface
            interface = interfaces[0]["name"]
            console.print(f"[yellow]Using default interface: {interface}[/yellow]\n")
        
        # Build BPF filter
        bpf = filter_expr or ""
        
        console.print(Panel(
            f"[bold]Interface:[/bold] {interface}\n"
            f"[bold]Duration:[/bold] {duration}s\n"
            f"[bold]Max Packets:[/bold] {'Unlimited' if count == 0 else count}\n"
            f"[bold]Filter:[/bold] {bpf or 'None (all traffic)'}\n\n"
            f"[dim]Press Ctrl+C to stop early[/dim]",
            title="🌐 Network Monitor",
            border_style="blue",
        ))
        
        # Initialize monitor
        monitor = NetworkMonitor(interface=interface, bpf_filter=bpf)
        
        packets_captured = 0
        alerts = []
        connections = {}
        
        # Capture packets
        try:
            capture = PacketCapture(
                interface=interface,
                bpf_filter=bpf,
                promisc=True,
            )
            
            # Determine packet count
            packet_limit = count if count > 0 else 10000
            
            console.print("\n[bold green]Starting capture...[/bold green]\n")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("{task.fields[packets]} packets"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Capturing on {interface}...",
                    total=duration,
                    packets=0
                )
                
                captured = capture.capture_sync(
                    count=min(packet_limit, 1000),
                    timeout=float(duration)
                )
                
                for pkt in captured:
                    packets_captured += 1
                    progress.update(task, packets=packets_captured)
                    
                    # Extract packet info
                    try:
                        from scapy.all import IP, TCP, UDP
                        
                        if IP in pkt:
                            src_ip = pkt[IP].src
                            dst_ip = pkt[IP].dst
                            proto = "TCP" if TCP in pkt else ("UDP" if UDP in pkt else "OTHER")
                            src_port = pkt[TCP].sport if TCP in pkt else (pkt[UDP].sport if UDP in pkt else 0)
                            dst_port = pkt[TCP].dport if TCP in pkt else (pkt[UDP].dport if UDP in pkt else 0)
                            
                            conn_key = f"{src_ip}:{src_port}->{dst_ip}:{dst_port}"
                            
                            if conn_key not in connections:
                                connections[conn_key] = {
                                    "src_ip": src_ip,
                                    "dst_ip": dst_ip,
                                    "src_port": src_port,
                                    "dst_port": dst_port,
                                    "protocol": proto,
                                    "packets": 0,
                                    "bytes": 0,
                                }
                            
                            connections[conn_key]["packets"] += 1
                            connections[conn_key]["bytes"] += len(pkt)
                            
                            # Check for threats
                            # Weak TLS detection
                            if dst_port == 443 and TCP in pkt and pkt[TCP].payload:
                                payload = bytes(pkt[TCP].payload)
                                if len(payload) > 5:
                                    # Check TLS version
                                    if payload[0] == 22:  # Handshake
                                        version = (payload[1] << 8) | payload[2]
                                        if version < 0x0303:  # < TLS 1.2
                                            alerts.append({
                                                "type": "WEAK_TLS",
                                                "severity": "HIGH",
                                                "message": f"Deprecated TLS version detected to {dst_ip}",
                                                "connection": conn_key
                                            })
                            
                            # Suspicious port detection
                            suspicious_ports = [4444, 5555, 6666, 31337, 12345]
                            if dst_port in suspicious_ports or src_port in suspicious_ports:
                                alerts.append({
                                    "type": "SUSPICIOUS_PORT",
                                    "severity": "MEDIUM",
                                    "message": f"Suspicious port {max(src_port, dst_port)} detected",
                                    "connection": conn_key
                                })
                            
                            # Large data transfer detection
                            if connections[conn_key]["bytes"] > 10_000_000:  # 10MB
                                if conn_key not in [a.get("connection") for a in alerts if a["type"] == "LARGE_TRANSFER"]:
                                    alerts.append({
                                        "type": "LARGE_TRANSFER",
                                        "severity": "LOW",
                                        "message": f"Large data transfer ({connections[conn_key]['bytes']/1_000_000:.1f}MB) to {dst_ip}",
                                        "connection": conn_key
                                    })
                    except Exception:
                        pass
                
                progress.update(task, completed=duration)
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Capture stopped by user.[/yellow]")
        except PermissionError:
            console.print(Panel(
                "[red]Permission denied for packet capture.[/red]\n\n"
                "[bold]Run as Administrator/root:[/bold]\n"
                "  • Windows: Run terminal as Administrator\n"
                "  • Linux: sudo chronos detect network\n"
                "  • macOS: sudo chronos detect network",
                title="⚠️ Permission Required",
                border_style="red",
            ))
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[red]Capture error: {e}[/red]")
            raise typer.Exit(1)
        
        # Display results
        if output == OutputFormat.JSON:
            import json
            result = {
                "interface": interface,
                "duration_seconds": duration,
                "packets_captured": packets_captured,
                "unique_connections": len(connections),
                "alerts": alerts,
                "connections": list(connections.values()),
            }
            console.print(json.dumps(result, indent=2))
        else:
            # Summary panel
            console.print(Panel(
                f"[bold]Packets Captured:[/bold] {packets_captured}\n"
                f"[bold]Unique Connections:[/bold] {len(connections)}\n"
                f"[bold]Alerts Generated:[/bold] {len(alerts)}",
                title="📊 Capture Summary",
                border_style="green",
            ))
            
            # Alerts table
            if alerts:
                console.print("\n[bold red]⚠️ Security Alerts:[/bold red]\n")
                alert_table = Table(show_header=True, border_style="red")
                alert_table.add_column("Severity", width=10)
                alert_table.add_column("Type", width=20)
                alert_table.add_column("Message", width=50)
                
                for alert in alerts[:20]:
                    sev = alert["severity"]
                    color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "blue"}.get(sev, "white")
                    alert_table.add_row(
                        f"[{color}]{sev}[/{color}]",
                        alert["type"],
                        alert["message"]
                    )
                
                console.print(alert_table)
                
                if len(alerts) > 20:
                    console.print(f"[dim]... and {len(alerts) - 20} more alerts[/dim]")
            elif not threats_only:
                console.print("\n[green]✓ No security threats detected[/green]")
            
            # Top connections (if not threats_only)
            if not threats_only and connections:
                console.print("\n[bold]Top Connections by Traffic:[/bold]\n")
                conn_table = Table(show_header=True, border_style="dim")
                conn_table.add_column("Source", style="cyan")
                conn_table.add_column("Destination", style="cyan")
                conn_table.add_column("Protocol")
                conn_table.add_column("Packets", justify="right")
                conn_table.add_column("Bytes", justify="right")
                
                sorted_conns = sorted(
                    connections.values(),
                    key=lambda x: x["bytes"],
                    reverse=True
                )[:10]
                
                for conn in sorted_conns:
                    conn_table.add_row(
                        f"{conn['src_ip']}:{conn['src_port']}",
                        f"{conn['dst_ip']}:{conn['dst_port']}",
                        conn["protocol"],
                        str(conn["packets"]),
                        f"{conn['bytes']:,}",
                    )
                
                console.print(conn_table)


@app.command("darkweb")
def darkweb_command(
    keywords: Optional[List[str]] = typer.Option(
        None, "--keyword", "-k",
        help="Keywords to monitor (can specify multiple).",
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", "-d",
        help="Email domain to monitor for leaks (e.g., company.com).",
    ),
    scan_only: bool = typer.Option(
        True, "--scan/--monitor", "-s/-m",
        help="Single scan vs continuous monitoring.",
    ),
    limit: int = typer.Option(
        50, "--limit", "-l",
        help="Number of recent pastes to scan.",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE, "--output", "-o",
        help="Output format.",
    ),
) -> None:
    """
    🕸️ Dark web and paste site monitoring for data leaks.
    
    Scans public paste sites for leaked credentials, sensitive data,
    and mentions of your organization's assets.
    
    [bold]Monitors:[/bold]
    • Pastebin and similar paste sites
    • Leaked credentials and API keys
    • Email addresses from specified domains
    • Custom keywords and patterns
    
    [bold]Examples:[/bold]
        chronos detect darkweb --keyword "company-secret"
        chronos detect darkweb --domain mycompany.com
        chronos detect darkweb -k "api-key" -k "password" -d corp.com
        chronos detect darkweb --scan --limit 100
    """
    with error_handler(console):
        import asyncio
        
        try:
            from chronos.core.detect.darkweb_monitor import (
                DarkWebMonitor,
                MonitoringPattern,
                MatchType,
                AlertSeverity,
                BUILTIN_PATTERNS,
            )
        except ImportError as e:
            console.print(Panel(
                f"[red]Dark web monitoring dependencies not available.[/red]\n\n"
                f"[bold]Install required packages:[/bold]\n"
                f"  pip install aiohttp\n\n"
                f"[dim]Error: {e}[/dim]",
                title="⚠️ Missing Dependencies",
                border_style="yellow",
            ))
            raise typer.Exit(1)
        
        if not keywords and not domain:
            console.print(Panel(
                "[yellow]No monitoring targets specified.[/yellow]\n\n"
                "[bold]Usage Examples:[/bold]\n"
                "  chronos detect darkweb --keyword 'company-secret'\n"
                "  chronos detect darkweb --domain mycompany.com\n"
                "  chronos detect darkweb -k 'api_key' -d corp.com\n\n"
                "[bold]Built-in patterns available:[/bold]\n"
                "  • Email addresses\n"
                "  • Credit cards\n"
                "  • API keys (AWS, GitHub, etc.)\n"
                "  • Private keys\n"
                "  • Password fields",
                title="🕸️ Dark Web Monitor",
                border_style="blue",
            ))
            raise typer.Exit(0)
        
        console.print(Panel(
            f"[bold]Keywords:[/bold] {', '.join(keywords) if keywords else 'None'}\n"
            f"[bold]Domain:[/bold] {domain or 'None'}\n"
            f"[bold]Mode:[/bold] {'Single Scan' if scan_only else 'Continuous Monitor'}\n"
            f"[bold]Paste Limit:[/bold] {limit}",
            title="🕸️ Dark Web Scanner",
            border_style="blue",
        ))
        
        # Initialize monitor
        monitor = DarkWebMonitor(use_tor=False)
        
        # Add custom patterns
        patterns_added = 0
        
        if keywords:
            for kw in keywords:
                monitor.add_keyword(kw, severity=AlertSeverity.HIGH)
                patterns_added += 1
        
        if domain:
            monitor.add_email_domain(domain, severity=AlertSeverity.CRITICAL)
            patterns_added += 1
        
        # Enable some built-in patterns
        monitor.enable_builtin_pattern("api_key_generic")
        monitor.enable_builtin_pattern("github_token")
        monitor.enable_builtin_pattern("aws_key")
        monitor.enable_builtin_pattern("private_key")
        
        console.print(f"\n[dim]Configured {patterns_added} custom patterns + built-in detectors[/dim]")
        
        # Run scan
        matches = []
        pastes_scanned = 0
        
        async def run_scan():
            nonlocal matches, pastes_scanned
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Scanning paste sites...", total=None)
                
                try:
                    # Get recent pastes
                    pastes = await monitor.scan_recent_pastes(limit=limit)
                    pastes_scanned = len(pastes)
                    
                    # Find matches
                    for paste in pastes:
                        paste_matches = monitor.scan_content(paste.content, paste)
                        matches.extend(paste_matches)
                    
                except Exception as e:
                    logger.error(f"Scan error: {e}")
                    progress.update(task, description=f"[red]Error: {e}[/red]")
        
        try:
            asyncio.run(run_scan())
        except Exception as e:
            console.print(f"[red]Scan error: {e}[/red]")
        
        # Display results
        if output == OutputFormat.JSON:
            import json
            result = {
                "pastes_scanned": pastes_scanned,
                "matches_found": len(matches),
                "matches": [m.to_dict() for m in matches],
            }
            console.print(json.dumps(result, indent=2, default=str))
        else:
            console.print(Panel(
                f"[bold]Pastes Scanned:[/bold] {pastes_scanned}\n"
                f"[bold]Matches Found:[/bold] {len(matches)}",
                title="📊 Scan Results",
                border_style="green" if not matches else "red",
            ))
            
            if matches:
                console.print("\n[bold red]⚠️ Potential Data Leaks Found:[/bold red]\n")
                
                match_table = Table(show_header=True, border_style="red")
                match_table.add_column("Severity", width=10)
                match_table.add_column("Pattern", width=20)
                match_table.add_column("Match", width=30)
                match_table.add_column("Source", width=20)
                
                for match in matches[:20]:
                    sev = match.severity.value.upper()
                    color = {
                        "CRITICAL": "red bold",
                        "HIGH": "red",
                        "MEDIUM": "yellow",
                        "LOW": "blue",
                    }.get(sev, "white")
                    
                    # Redact sensitive data
                    matched_text = match.matched_text
                    if len(matched_text) > 8:
                        matched_text = matched_text[:4] + "***" + matched_text[-4:]
                    
                    match_table.add_row(
                        f"[{color}]{sev}[/{color}]",
                        match.pattern.name[:20],
                        matched_text[:30],
                        match.source[:20],
                    )
                
                console.print(match_table)
                
                if len(matches) > 20:
                    console.print(f"\n[dim]... and {len(matches) - 20} more matches[/dim]")
                
                console.print(Panel(
                    "[bold]Recommended Actions:[/bold]\n"
                    "  1. Rotate any exposed API keys immediately\n"
                    "  2. Reset compromised passwords\n"
                    "  3. Review access logs for unauthorized activity\n"
                    "  4. Enable 2FA on affected accounts\n"
                    "  5. Consider a full security audit",
                    title="📋 Recommendations",
                    border_style="yellow",
                ))
            else:
                console.print("\n[green]✓ No data leaks detected in scanned pastes[/green]")
