"""
CHRONOS Analyze Command
=======================

Commands for cryptographic analysis and vulnerability assessment.
Real implementation using the file scanner.
"""

import time
import json
from pathlib import Path
from typing import Optional, List
from enum import Enum
from datetime import datetime
from collections import Counter

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text

from chronos.cli.utils import error_handler, print_success, print_warning, AnalysisError
from chronos.core.scanner import (
    FileScanner,
    ScanResult,
    ScanFinding,
    SeverityLevel,
    FindingType,
)

console = Console()

app = typer.Typer(
    name="analyze",
    help="📊 Cryptographic analysis and vulnerability assessment commands.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


class CryptoAlgorithm(str, Enum):
    """Cryptographic algorithms for analysis."""
    RSA = "rsa"
    ECC = "ecc"
    AES = "aes"
    SHA = "sha"
    ALL = "all"


class AnalysisDepth(str, Enum):
    """Analysis depth levels."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


def _get_crypto_findings(findings: List[ScanFinding]) -> List[ScanFinding]:
    """Filter findings to crypto-related only."""
    crypto_types = {FindingType.WEAK_CRYPTO, FindingType.QUANTUM_VULNERABLE}
    return [f for f in findings if f.finding_type in crypto_types]


def _format_crypto_summary(crypto_findings: List[ScanFinding]) -> Panel:
    """Format a cryptographic analysis summary."""
    content = Text()
    
    # Count by type
    weak_count = sum(1 for f in crypto_findings if f.finding_type == FindingType.WEAK_CRYPTO)
    quantum_count = sum(1 for f in crypto_findings if f.finding_type == FindingType.QUANTUM_VULNERABLE)
    
    content.append("📊 Cryptographic Analysis Results\n\n", style="bold")
    
    if weak_count > 0:
        content.append(f"🔴 Weak Cryptography: {weak_count}\n", style="red")
    else:
        content.append("✅ No weak cryptography found\n", style="green")
    
    if quantum_count > 0:
        content.append(f"⚛️  Quantum Vulnerable: {quantum_count}\n", style="yellow")
    else:
        content.append("✅ No quantum-vulnerable algorithms found\n", style="green")
    
    content.append("\n")
    
    # Algorithm breakdown
    algorithms = Counter()
    for f in crypto_findings:
        msg_lower = f.message.lower()
        if "md5" in msg_lower:
            algorithms["MD5"] += 1
        elif "sha1" in msg_lower or "sha-1" in msg_lower:
            algorithms["SHA-1"] += 1
        elif "des" in msg_lower:
            algorithms["DES"] += 1
        elif "rc4" in msg_lower:
            algorithms["RC4"] += 1
        elif "rsa" in msg_lower:
            algorithms["RSA"] += 1
        elif "ecc" in msg_lower or "elliptic" in msg_lower:
            algorithms["ECC"] += 1
        elif "diffie" in msg_lower:
            algorithms["Diffie-Hellman"] += 1
    
    if algorithms:
        content.append("[bold]Detected Algorithms:[/bold]\n")
        for algo, count in algorithms.most_common():
            content.append(f"  • {algo}: {count} occurrence(s)\n")
    
    return Panel(content, title="🔐 Crypto Summary", border_style="cyan")


@app.command("crypto")
def crypto_command(
    target: Path = typer.Argument(
        Path("."),
        help="Target path to analyze for cryptographic usage.",
    ),
    algorithm: CryptoAlgorithm = typer.Option(
        CryptoAlgorithm.ALL,
        "--algorithm",
        "-a",
        help="Specific algorithm to analyze.",
    ),
    quantum_check: bool = typer.Option(
        True,
        "--quantum/--no-quantum",
        "-q/-Q",
        help="Check for quantum vulnerability.",
    ),
    output: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format (table, json).",
    ),
) -> None:
    """
    🔐 Analyze cryptographic implementations.
    
    Scans code for cryptographic usage and evaluates:
    - Algorithm strength and configuration
    - Weak hash algorithms (MD5, SHA-1)
    - Deprecated encryption (DES, RC4)
    - Quantum vulnerability assessment (RSA, ECC)
    
    [bold]Examples:[/bold]
        chronos analyze crypto ./src
        chronos analyze crypto . --algorithm rsa --quantum
    """
    with error_handler(console):
        console.print(Panel(
            f"[bold]Target:[/bold] {target.absolute()}\n"
            f"[bold]Algorithm:[/bold] {algorithm.value}\n"
            f"[bold]Quantum Check:[/bold] {quantum_check}",
            title="🔐 Cryptographic Analysis",
            border_style="blue",
        ))
        
        # Run the scanner
        scanner = FileScanner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Analyzing cryptographic patterns...", total=None)
            result = scanner.scan(
                target=target,
                recursive=True,
                quantum_check=quantum_check,
            )
        
        # Filter to crypto findings only
        crypto_findings = _get_crypto_findings(result.findings)
        
        # Filter by algorithm if specified
        if algorithm != CryptoAlgorithm.ALL:
            algo_filter = algorithm.value.lower()
            crypto_findings = [
                f for f in crypto_findings 
                if algo_filter in f.message.lower()
            ]
        
        if output == "json":
            output_data = {
                "target": str(target.absolute()),
                "files_scanned": result.files_scanned,
                "crypto_findings": len(crypto_findings),
                "findings": [
                    {
                        "type": f.finding_type.value,
                        "severity": f.severity.value,
                        "file": f.file_path,
                        "line": f.line_number,
                        "message": f.message,
                        "recommendation": f.recommendation,
                        "cwe": f.cwe_id,
                    }
                    for f in crypto_findings
                ],
            }
            console.print_json(json.dumps(output_data, indent=2))
        else:
            console.print()
            console.print(_format_crypto_summary(crypto_findings))
            
            if crypto_findings:
                table = Table(
                    show_header=True,
                    header_style="bold cyan",
                    title="🔐 Cryptographic Findings",
                )
                table.add_column("Type", width=15)
                table.add_column("Severity", width=10)
                table.add_column("File", width=35)
                table.add_column("Line", width=6)
                table.add_column("Issue", width=45)
                
                for finding in crypto_findings:
                    severity_color = {
                        SeverityLevel.CRITICAL: "red bold",
                        SeverityLevel.HIGH: "red",
                        SeverityLevel.MEDIUM: "yellow",
                        SeverityLevel.LOW: "blue",
                    }.get(finding.severity, "white")
                    
                    table.add_row(
                        finding.finding_type.value,
                        finding.severity.value.upper(),
                        Path(finding.file_path).name,
                        str(finding.line_number),
                        finding.message[:45],
                        style=severity_color,
                    )
                
                console.print(table)
                console.print()
            else:
                console.print(Panel(
                    "[green]✓ No cryptographic issues found![/green]",
                    border_style="green",
                ))


@app.command("vulnerabilities")
def vulnerabilities_command(
    target: Path = typer.Argument(
        Path("."),
        help="Target to scan for vulnerabilities.",
    ),
    depth: AnalysisDepth = typer.Option(
        AnalysisDepth.STANDARD,
        "--depth",
        "-d",
        help="Analysis depth level.",
    ),
    cve_check: bool = typer.Option(
        True,
        "--cve/--no-cve",
        help="Check against CVE database.",
    ),
) -> None:
    """
    🔍 Scan for security vulnerabilities.
    
    Performs vulnerability assessment including:
    - SQL injection patterns
    - Command injection vulnerabilities
    - Path traversal issues
    - Unsafe deserialization
    - Hardcoded secrets
    """
    with error_handler(console):
        console.print(Panel(
            f"[bold]Target:[/bold] {target.absolute()}\n"
            f"[bold]Depth:[/bold] {depth.value}\n"
            f"[bold]CVE Check:[/bold] {cve_check}",
            title="🔍 Vulnerability Analysis",
            border_style="blue",
        ))
        
        scanner = FileScanner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("Scanning for vulnerabilities...", total=None)
            result = scanner.scan(target=target, recursive=True, quantum_check=False)
        
        # Filter to vulnerability findings
        vuln_types = {
            FindingType.SQL_INJECTION,
            FindingType.COMMAND_INJECTION,
            FindingType.PATH_TRAVERSAL,
            FindingType.UNSAFE_DESERIALIZATION,
            FindingType.HARDCODED_SECRET,
            FindingType.INSECURE_RANDOM,
        }
        vuln_findings = [f for f in result.findings if f.finding_type in vuln_types]
        
        console.print()
        
        # Summary
        summary = Text()
        summary.append(f"📁 Files Scanned: {result.files_scanned}\n", style="bold")
        summary.append(f"🔍 Vulnerabilities Found: {len(vuln_findings)}\n\n")
        
        # Group by type
        by_type = Counter(f.finding_type.value for f in vuln_findings)
        if by_type:
            summary.append("[bold]By Category:[/bold]\n")
            for vuln_type, count in by_type.most_common():
                summary.append(f"  • {vuln_type}: {count}\n")
        
        console.print(Panel(summary, title="📊 Vulnerability Summary", border_style="cyan"))
        
        if vuln_findings:
            table = Table(
                show_header=True,
                header_style="bold cyan",
                title="🔍 Vulnerability Findings",
            )
            table.add_column("Severity", width=10)
            table.add_column("Type", width=20)
            table.add_column("File", width=30)
            table.add_column("Line", width=6)
            table.add_column("CWE", width=10)
            
            for finding in vuln_findings:
                severity_color = {
                    SeverityLevel.CRITICAL: "red bold",
                    SeverityLevel.HIGH: "red",
                    SeverityLevel.MEDIUM: "yellow",
                    SeverityLevel.LOW: "blue",
                }.get(finding.severity, "white")
                
                table.add_row(
                    finding.severity.value.upper(),
                    finding.finding_type.value,
                    Path(finding.file_path).name,
                    str(finding.line_number),
                    finding.cwe_id or "-",
                    style=severity_color,
                )
            
            console.print(table)
        else:
            console.print(Panel(
                "[green]✓ No vulnerabilities found![/green]",
                border_style="green",
            ))


@app.command("report")
def report_command(
    target: Path = typer.Argument(
        Path("."),
        help="Target to generate report for.",
    ),
    output: Path = typer.Option(
        Path("chronos-report.json"),
        "--output",
        "-o",
        help="Output file path for the report.",
    ),
    format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Report format (json, markdown).",
    ),
) -> None:
    """
    📄 Generate comprehensive security analysis report.
    
    Creates a detailed report including:
    - Executive summary
    - Threat analysis results
    - Cryptographic assessment
    - Vulnerability findings
    - Remediation recommendations
    """
    with error_handler(console):
        console.print(f"[blue]Generating {format.upper()} report...[/blue]")
        
        scanner = FileScanner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Running security scan...", total=None)
            result = scanner.scan(target=target, recursive=True, quantum_check=True)
            progress.update(task, description="Generating report...")
        
        # Generate report content
        report = {
            "report_type": "CHRONOS Security Analysis",
            "generated_at": datetime.now().isoformat(),
            "target": str(target.absolute()),
            "summary": {
                "files_scanned": result.files_scanned,
                "total_findings": len(result.findings),
                "critical": result.critical_count,
                "high": result.high_count,
                "medium": result.medium_count,
                "low": result.low_count,
            },
            "findings_by_type": dict(Counter(f.finding_type.value for f in result.findings)),
            "findings": [f.to_dict() for f in result.findings],
            "recommendations": [
                "Review all CRITICAL and HIGH severity findings immediately",
                "Replace weak cryptographic algorithms (MD5, SHA-1, DES, RC4)",
                "Prepare migration plan for quantum-vulnerable algorithms",
                "Remove hardcoded secrets and use environment variables",
                "Implement input validation to prevent injection attacks",
            ],
        }
        
        if format == "markdown":
            # Generate markdown
            md_content = f"""# CHRONOS Security Analysis Report

**Generated:** {report['generated_at']}
**Target:** {report['target']}

## Executive Summary

| Metric | Value |
|--------|-------|
| Files Scanned | {result.files_scanned} |
| Total Findings | {len(result.findings)} |
| Critical | {result.critical_count} |
| High | {result.high_count} |
| Medium | {result.medium_count} |
| Low | {result.low_count} |

## Findings by Type

"""
            for ftype, count in report['findings_by_type'].items():
                md_content += f"- **{ftype}**: {count}\n"
            
            md_content += "\n## Detailed Findings\n\n"
            for f in result.findings[:20]:  # Limit to first 20
                md_content += f"""### {f.finding_type.value} ({f.severity.value.upper()})
- **File:** {f.file_path}:{f.line_number}
- **Message:** {f.message}
- **Recommendation:** {f.recommendation}
- **CWE:** {f.cwe_id or 'N/A'}

"""
            
            output = output.with_suffix('.md')
            output.write_text(md_content)
        else:
            # JSON format
            output = output.with_suffix('.json')
            output.write_text(json.dumps(report, indent=2))
        
        console.print(f"\n[green]✓[/green] Report generated: [cyan]{output}[/cyan]")


@app.command("quantum-readiness")
def quantum_readiness_command(
    target: Path = typer.Argument(
        Path("."),
        help="Target to assess quantum readiness.",
    ),
) -> None:
    """
    ⚛️ Assess quantum computing readiness.
    
    Evaluates your system's preparedness for quantum threats:
    - Current cryptographic inventory
    - Quantum-vulnerable algorithms
    - Migration recommendations
    - Post-quantum alternatives
    """
    with error_handler(console):
        console.print(Panel(
            f"[bold]Assessing:[/bold] {target.absolute()}",
            title="⚛️ Quantum Readiness Assessment",
            border_style="magenta",
        ))
        
        scanner = FileScanner()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold magenta]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Evaluating quantum readiness...", total=None)
            result = scanner.scan(target=target, recursive=True, quantum_check=True)
        
        # Analyze quantum vulnerability
        quantum_findings = [
            f for f in result.findings 
            if f.finding_type == FindingType.QUANTUM_VULNERABLE
        ]
        
        # Calculate readiness score
        if result.files_scanned == 0:
            score = "N/A"
            score_color = "dim"
        elif len(quantum_findings) == 0:
            score = "EXCELLENT"
            score_color = "green bold"
        elif len(quantum_findings) <= 3:
            score = "GOOD"
            score_color = "green"
        elif len(quantum_findings) <= 10:
            score = "MODERATE"
            score_color = "yellow"
        else:
            score = "NEEDS ATTENTION"
            score_color = "red"
        
        # Count by algorithm
        algorithms = Counter()
        for f in quantum_findings:
            msg_lower = f.message.lower()
            if "rsa" in msg_lower:
                algorithms["RSA"] += 1
            elif "ecc" in msg_lower or "elliptic" in msg_lower:
                algorithms["ECC/ECDSA"] += 1
            elif "diffie" in msg_lower:
                algorithms["Diffie-Hellman"] += 1
        
        # Build summary
        summary = Text()
        summary.append(f"[bold]Quantum Readiness Score:[/bold] [{score_color}]{score}[/{score_color}]\n\n")
        summary.append(f"[bold]Files Scanned:[/bold] {result.files_scanned}\n")
        summary.append(f"[bold]Quantum-Vulnerable Instances:[/bold] {len(quantum_findings)}\n\n")
        
        if algorithms:
            summary.append("[bold]Detected Quantum-Vulnerable Algorithms:[/bold]\n")
            for algo, count in algorithms.most_common():
                summary.append(f"  • {algo}: {count} occurrence(s)\n")
            summary.append("\n")
        
        summary.append("[bold]Post-Quantum Recommendations:[/bold]\n")
        if algorithms.get("RSA"):
            summary.append("  • RSA → CRYSTALS-Kyber (for key exchange) or CRYSTALS-Dilithium (for signatures)\n")
        if algorithms.get("ECC/ECDSA"):
            summary.append("  • ECC/ECDSA → CRYSTALS-Dilithium or FALCON for signatures\n")
        if algorithms.get("Diffie-Hellman"):
            summary.append("  • DH → Hybrid key exchange (X25519 + Kyber)\n")
        
        if not algorithms:
            summary.append("  ✅ No immediate quantum threats detected\n")
            summary.append("  • Continue monitoring NIST PQC standardization\n")
            summary.append("  • Implement crypto-agility patterns for future flexibility\n")
        
        console.print(Panel(summary, title="Assessment Results", border_style="magenta"))
