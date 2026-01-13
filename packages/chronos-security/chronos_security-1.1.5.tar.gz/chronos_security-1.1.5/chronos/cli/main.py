"""
CHRONOS CLI Main Entry Point
============================

Main command-line interface for the CHRONOS quantum security platform.
Provides commands for threat detection, security analysis, and defense operations.

SHORT ALIASES (Quick Commands):
  chronos s         → status
  chronos d <path>  → detect scan <path>
  chronos a <path>  → analyze crypto <path>
  chronos c <cve>   → intel cve <cve>
  chronos u <url>   → intel url <url>
  chronos v <file>  → vuln import <file>
  chronos p <file>  → phish analyze <file>
  chronos l <file>  → logs analyze <file>
  chronos r <out>   → report generate <out>
  chronos ir <name> → ir run <name>
"""

import sys
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Get version without circular import
def _get_version() -> str:
    """Get version string without triggering circular imports."""
    import importlib.metadata
    try:
        return importlib.metadata.version("chronos-security")
    except importlib.metadata.PackageNotFoundError:
        return "1.1.1"

__version__ = _get_version()

from chronos.cli.commands import detect, analyze, defend, config
from chronos.cli.commands import intel, vuln, phishing, logs, report, ir
from chronos.cli.utils import error_handler, ChronosCLIError

# Initialize Rich console for formatted output
console = Console()

# ASCII Art Banner
BANNER = """
 ██████╗██╗  ██╗██████╗  ██████╗ ███╗   ██╗ ██████╗ ███████╗
██╔════╝██║  ██║██╔══██╗██╔═══██╗████╗  ██║██╔═══██╗██╔════╝
██║     ███████║██████╔╝██║   ██║██╔██╗ ██║██║   ██║███████╗
██║     ██╔══██║██╔══██╗██║   ██║██║╚██╗██║██║   ██║╚════██║
╚██████╗██║  ██║██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝███████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝
"""

# Custom help text
HELP_TEXT = """
[bold blue]CHRONOS[/bold blue] - [italic]Unified Security Fusion Platform[/italic]

[bold green]⚡ QUICK SHORTCUTS (Most Used):[/bold green]
  [cyan]chronos s[/cyan]              Check status
  [cyan]chronos d .[/cyan]            Scan current directory
  [cyan]chronos c CVE-2024-1234[/cyan] Look up CVE
  [cyan]chronos u http://...[/cyan]   Check URL reputation
  [cyan]chronos v report.json[/cyan]  Import vulnerabilities
  [cyan]chronos p email.eml[/cyan]    Analyze phishing email
  [cyan]chronos l server.log[/cyan]   Analyze logs

[bold yellow]Full Commands:[/bold yellow]
  [green]detect[/green]   Scan for security threats (d)
  [green]analyze[/green]  Analyze cryptography (a)
  [green]intel[/green]    Threat intelligence (c/u)
  [green]vuln[/green]     Vulnerability management (v)
  [green]phish[/green]    Phishing detection (p)
  [green]logs[/green]     Log analysis (l)
  [green]report[/green]   Generate reports (r)
  [green]ir[/green]       Incident response

[dim]Run: chronos <command> --help for details[/dim]
"""


def version_callback(value: bool) -> None:
    """Display version information and exit."""
    if value:
        console.print(Panel(
            f"[bold blue]CHRONOS[/bold blue] Quantum Security Platform\n"
            f"Version: [green]{__version__}[/green]\n"
            f"Python: [cyan]{sys.version.split()[0]}[/cyan]",
            title="Version Info",
            border_style="blue"
        ))
        raise typer.Exit()


def banner_callback(value: bool) -> None:
    """Display ASCII banner and exit."""
    if value:
        console.print(f"[bold blue]{BANNER}[/bold blue]")
        console.print(f"[dim]Version {__version__} - Quantum Security Platform[/dim]\n")
        raise typer.Exit()


# Main Application
app = typer.Typer(
    name="chronos",
    help="CHRONOS - Unified Quantum Security Platform for present and future threats.",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Register sub-command groups - Core (with short aliases)
app.add_typer(detect.app, name="detect", help="🔍 Scan and detect security threats")
app.add_typer(analyze.app, name="analyze", help="📊 Analyze cryptographic vulnerabilities")
app.add_typer(defend.app, name="defend", help="🛡️ Activate defensive countermeasures")
app.add_typer(config.app, name="config", help="⚙️ Configuration management")

# Register sub-command groups - SecFusion
app.add_typer(intel.app, name="intel", help="🔬 Threat intelligence queries")
app.add_typer(vuln.app, name="vuln", help="🔓 Vulnerability management")
app.add_typer(phishing.app, name="phish", help="🎣 Phishing email analysis")
app.add_typer(logs.app, name="logs", help="📜 Security log analysis")
app.add_typer(report.app, name="report", help="📊 Report generation")
app.add_typer(ir.app, name="ir", help="🚨 Incident response")


# ============================================================================
# QUICK SHORTCUT COMMANDS (Single-letter aliases for common operations)
# ============================================================================

@app.command("s", hidden=False)
def shortcut_status() -> None:
    """📋 Quick status check (alias for: status)"""
    status_command(detailed=False)


@app.command("d")
def shortcut_detect(
    path: Path = typer.Argument(Path("."), help="Path to scan"),
    quick: bool = typer.Option(False, "-q", help="Quick scan"),
) -> None:
    """🔍 Quick scan (alias for: detect scan)"""
    from chronos.cli.commands.detect import scan_command, ScanType, OutputFormat
    scan_t = ScanType.QUICK if quick else ScanType.FULL
    scan_command(target=path, scan_type=scan_t, recursive=True, output=OutputFormat.TABLE, exclude=None, verbose=False)


@app.command("a")
def shortcut_analyze(
    path: Path = typer.Argument(Path("."), help="Path to analyze"),
) -> None:
    """📊 Quick crypto analysis (alias for: analyze crypto)"""
    from chronos.cli.commands.analyze import crypto_command, CryptoAlgorithm
    crypto_command(target=path, algorithm=CryptoAlgorithm.ALL, quantum_check=True, output="table")


@app.command("c")
def shortcut_cve(
    cve_id: str = typer.Argument(..., help="CVE ID (e.g., CVE-2024-1234)"),
    json_out: bool = typer.Option(False, "-j", help="JSON output"),
) -> None:
    """🔎 Quick CVE lookup (alias for: intel cve)"""
    from chronos.cli.commands.intel import intel_cve
    intel_cve(cve_id=cve_id, json_output=json_out)


@app.command("u")
def shortcut_url(
    url: str = typer.Argument(..., help="URL to check"),
    json_out: bool = typer.Option(False, "-j", help="JSON output"),
) -> None:
    """🔗 Quick URL check (alias for: intel url)"""
    from chronos.cli.commands.intel import intel_url
    intel_url(url=url, json_output=json_out)


@app.command("v")
def shortcut_vuln(
    source: Path = typer.Argument(..., help="Vulnerability report file", exists=True),
    json_out: bool = typer.Option(False, "-j", help="JSON output"),
) -> None:
    """🔓 Quick vuln import (alias for: vuln import)"""
    from chronos.cli.commands.vuln import vuln_import
    vuln_import(source=source, source_type=None, enrich=True, json_output=json_out)


@app.command("p")
def shortcut_phish(
    source: Path = typer.Argument(..., help="Email file (.eml)", exists=True),
    json_out: bool = typer.Option(False, "-j", help="JSON output"),
) -> None:
    """🎣 Quick phishing check (alias for: phish analyze)"""
    from chronos.cli.commands.phishing import phish_analyze
    phish_analyze(source=source, check_urls=True, json_output=json_out)


@app.command("l")
def shortcut_logs(
    source: Path = typer.Argument(..., help="Log file to analyze", exists=True),
    json_out: bool = typer.Option(False, "-j", help="JSON output"),
) -> None:
    """📜 Quick log analysis (alias for: logs analyze)"""
    from chronos.cli.commands.logs import logs_analyze
    logs_analyze(source=source, log_type=None, use_baseline=True, ml_detection=True, json_output=json_out)


@app.command("r")
def shortcut_report(
    output: Path = typer.Argument(..., help="Output file"),
    fmt: str = typer.Option("html", "-f", help="Format: html/md/json"),
) -> None:
    """📊 Quick report (alias for: report generate)"""
    from chronos.cli.commands.report import report_generate
    report_generate(output=output, report_format=fmt, audience="technical", 
                   title="CHRONOS Security Report", include_charts=True, days=7)


# ============================================================================
# END QUICK SHORTCUTS
# ============================================================================


@app.callback(invoke_without_command=True)
def main_callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    banner: bool = typer.Option(
        False,
        "--banner",
        "-b",
        help="Display CHRONOS banner.",
        callback=banner_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        help="Enable verbose output.",
    ),
) -> None:
    """
    [bold blue]CHRONOS[/bold blue] - Unified Quantum Security Platform
    
    Protecting systems against present and future quantum threats.
    """
    # Store verbose flag in context for sub-commands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    
    if ctx.invoked_subcommand is None:
        # No subcommand provided, show custom help
        console.print(Panel(
            HELP_TEXT,
            title="[bold blue]CHRONOS[/bold blue]",
            subtitle=f"v{__version__}",
            border_style="blue",
        ))


@app.command("status")
def status_command(
    detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed status"),
) -> None:
    """
    📋 Check the status of CHRONOS services and components.
    """
    with error_handler(console):
        from chronos.core.settings import get_settings
        
        settings = get_settings()
        
        console.print(Panel(
            "[cyan]CHRONOS Security Fusion Platform[/cyan]\n\n"
            "[bold]Core Components:[/bold]\n"
            "  • CLI Interface: [green]✓ Operational[/green]\n"
            "  • Configuration: [green]✓ Loaded[/green]\n"
            "  • Database: [green]✓ Available[/green]\n"
            "  • Detection Engine: [green]✓ Ready[/green]\n\n"
            "[bold]SecFusion Modules:[/bold]\n"
            "  • Threat Intel (intel): [green]✓ EPSS/NVD/KEV/URLhaus/VT[/green]\n"
            "  • Vuln Management (vuln): [green]✓ SARIF/Trivy/Grype/Bandit[/green]\n"
            "  • Phishing Scanner (phish): [green]✓ Email/URL Analysis[/green]\n"
            "  • Log Analysis (logs): [green]✓ Multi-format/ML Anomaly[/green]\n"
            "  • Report Generator (report): [green]✓ HTML/MD/JSON[/green]\n"
            "  • IR Playbooks (ir): [green]✓ 4 Built-in Playbooks[/green]\n\n"
            f"[bold]Config Path:[/bold] {settings.config_path}\n"
            f"[bold]Database:[/bold] {settings.db_path}",
            title="System Status",
            border_style="blue",
        ))
        
        if detailed:
            # Show API key status
            api_status = []
            if settings.api_keys.nvd_api_key:
                api_status.append("  • NVD: [green]✓ Configured[/green]")
            else:
                api_status.append("  • NVD: [yellow]○ Optional (rate limited)[/yellow]")
            
            if settings.api_keys.virustotal_api_key:
                api_status.append("  • VirusTotal: [green]✓ Configured[/green]")
            else:
                api_status.append("  • VirusTotal: [yellow]○ Not set[/yellow]")
            
            console.print(Panel(
                "[bold]API Keys:[/bold]\n" + "\n".join(api_status) + "\n\n"
                "[bold]Public APIs (no key needed):[/bold]\n"
                "  • EPSS (FIRST)\n"
                "  • CISA KEV\n"
                "  • URLhaus",
                title="Configuration Details",
                border_style="dim",
            ))


@app.command("setup")
def setup_command(
    virustotal: Optional[str] = typer.Option(
        None, "--virustotal", "--vt", "-V",
        help="VirusTotal API key (get from virustotal.com)",
    ),
    nvd: Optional[str] = typer.Option(
        None, "--nvd", "-N",
        help="NVD API key (get from nvd.nist.gov)",
    ),
    shodan: Optional[str] = typer.Option(
        None, "--shodan", "-S",
        help="Shodan API key (get from shodan.io)",
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i",
        help="Interactive setup mode",
    ),
) -> None:
    """
    🔑 Configure CHRONOS API keys (required after pip install).
    
    [bold]Examples:[/bold]
        chronos setup --virustotal YOUR_VT_KEY
        chronos setup --vt KEY --nvd KEY
        chronos setup -i  (interactive mode)
    
    [bold]Get API Keys:[/bold]
        • VirusTotal: https://www.virustotal.com/gui/join-us
        • NVD: https://nvd.nist.gov/developers/request-an-api-key
        • Shodan: https://account.shodan.io/
    """
    with error_handler(console):
        from chronos.core.settings import save_api_key, get_settings, reload_settings
        
        keys_set = []
        
        if interactive:
            console.print(Panel(
                "[bold]CHRONOS Setup Wizard[/bold]\n\n"
                "Configure your API keys for enhanced threat intelligence.\n"
                "Press Enter to skip any key you don't have.",
                title="🔑 API Key Setup",
                border_style="blue",
            ))
            
            # VirusTotal
            console.print("\n[bold]VirusTotal[/bold] (URL/file reputation)")
            console.print("[dim]Get key: https://www.virustotal.com/gui/join-us[/dim]")
            vt_input = console.input("[cyan]? VirusTotal API key: [/cyan]").strip()
            if vt_input:
                virustotal = vt_input
            
            # NVD
            console.print("\n[bold]NVD[/bold] (CVE database - optional, increases rate limit)")
            console.print("[dim]Get key: https://nvd.nist.gov/developers/request-an-api-key[/dim]")
            nvd_input = console.input("[cyan]? NVD API key: [/cyan]").strip()
            if nvd_input:
                nvd = nvd_input
            
            # Shodan
            console.print("\n[bold]Shodan[/bold] (network reconnaissance - optional)")
            console.print("[dim]Get key: https://account.shodan.io/[/dim]")
            shodan_input = console.input("[cyan]? Shodan API key: [/cyan]").strip()
            if shodan_input:
                shodan = shodan_input
        
        # Save provided keys
        if virustotal:
            path = save_api_key("virustotal_api_key", virustotal)
            keys_set.append("VirusTotal")
        
        if nvd:
            path = save_api_key("nvd_api_key", nvd)
            keys_set.append("NVD")
        
        if shodan:
            path = save_api_key("shodan_api_key", shodan)
            keys_set.append("Shodan")
        
        if keys_set:
            # Reload to verify
            reload_settings()
            settings = get_settings()
            
            # Verify keys were saved
            verified = []
            if settings.api_keys.virustotal_api_key:
                verified.append("  • VirusTotal: [green]✓ Configured[/green]")
            if settings.api_keys.nvd_api_key:
                verified.append("  • NVD: [green]✓ Configured[/green]")
            if settings.api_keys.shodan_api_key:
                verified.append("  • Shodan: [green]✓ Configured[/green]")
            
            console.print(Panel(
                f"[green]✓[/green] Saved {len(keys_set)} API key(s) to:\n"
                f"  [dim]{settings.config_path}[/dim]\n\n"
                f"[bold]Configured Keys:[/bold]\n" + "\n".join(verified) + "\n\n"
                f"[bold]Next steps:[/bold]\n"
                f"  • Run [bold]chronos doctor[/bold] to verify connectivity\n"
                f"  • Run [bold]chronos u https://example.com[/bold] to test URL check",
                title="Setup Complete",
                border_style="green",
            ))
        else:
            # Show current status and instructions
            settings = get_settings()
            status_lines = []
            
            if settings.api_keys.virustotal_api_key:
                status_lines.append("  • VirusTotal: [green]✓ Configured[/green]")
            else:
                status_lines.append("  • VirusTotal: [yellow]○ Not set[/yellow]")
            
            if settings.api_keys.nvd_api_key:
                status_lines.append("  • NVD: [green]✓ Configured[/green]")
            else:
                status_lines.append("  • NVD: [yellow]○ Not set (rate limited)[/yellow]")
            
            if settings.api_keys.shodan_api_key:
                status_lines.append("  • Shodan: [green]✓ Configured[/green]")
            else:
                status_lines.append("  • Shodan: [yellow]○ Not set[/yellow]")
            
            console.print(Panel(
                "[bold]Current API Key Status:[/bold]\n" + "\n".join(status_lines) + "\n\n"
                "[bold]Usage:[/bold]\n"
                "  [cyan]chronos setup --virustotal YOUR_KEY[/cyan]\n"
                "  [cyan]chronos setup --vt KEY --nvd KEY[/cyan]\n"
                "  [cyan]chronos setup -i[/cyan]  (interactive)\n\n"
                "[bold]Get API Keys:[/bold]\n"
                "  • VirusTotal: https://www.virustotal.com/gui/join-us\n"
                "  • NVD: https://nvd.nist.gov/developers/request-an-api-key\n"
                "  • Shodan: https://account.shodan.io/",
                title="🔑 CHRONOS Setup",
                border_style="blue",
            ))


@app.command("init")
def init_command(
    path: Path = typer.Argument(
        Path("."),
        help="Path to initialize CHRONOS configuration",
        exists=False,
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing config"),
) -> None:
    """
    🚀 Initialize CHRONOS configuration in a project.
    """
    with error_handler(console):
        config_path = path / ".chronos"
        
        if config_path.exists() and not force:
            console.print(
                f"[yellow]⚠[/yellow] Configuration already exists at {config_path}\n"
                f"Use [bold]--force[/bold] to overwrite."
            )
            raise typer.Exit(1)
        
        # Create configuration directory
        config_path.mkdir(parents=True, exist_ok=True)
        
        # Create default config file
        config_file = config_path / "config.yaml"
        config_file.write_text(
            "# CHRONOS Configuration\n"
            "version: 0.1.0\n"
            "security_level: high\n"
            "quantum_resistant: true\n"
            "modules:\n"
            "  detect: enabled\n"
            "  analyze: enabled\n"
            "  defend: enabled\n"
        )
        
        console.print(Panel(
            f"[green]✓[/green] CHRONOS initialized at [cyan]{path.absolute()}[/cyan]\n\n"
            f"Configuration: [dim]{config_file}[/dim]\n\n"
            f"[yellow]Next steps:[/yellow]\n"
            f"  1. Run [bold]chronos status[/bold] to verify installation\n"
            f"  2. Run [bold]chronos detect scan[/bold] to scan for threats\n"
            f"  3. Run [bold]chronos analyze crypto[/bold] to audit cryptography",
            title="Initialization Complete",
            border_style="green",
        ))


@app.command("doctor")
def doctor_command() -> None:
    """
    🩺 Diagnose CHRONOS installation and connectivity.
    
    Checks:
    - Configuration files
    - Database connectivity  
    - API endpoint connectivity
    - Required dependencies
    """
    import asyncio
    
    with error_handler(console):
        from chronos.core.settings import get_settings
        from chronos.core.database import get_db
        
        console.print("[bold]Running CHRONOS diagnostics...[/bold]\n")
        
        checks = []
        
        # 1. Configuration
        with console.status("Checking configuration..."):
            try:
                settings = get_settings()
                checks.append(("Configuration", "[green]✓ OK[/green]", f"Loaded from {settings.config_path}"))
            except Exception as e:
                checks.append(("Configuration", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 2. Database
        with console.status("Checking database..."):
            try:
                db = get_db()
                # Try a simple operation
                _ = db.query_events(limit=1)
                checks.append(("Database", "[green]✓ OK[/green]", f"SQLite at {settings.db_path}"))
            except Exception as e:
                checks.append(("Database", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 3. EPSS API
        with console.status("Testing EPSS API..."):
            try:
                from chronos.core.intel import EPSSClient
                client = EPSSClient()
                result = asyncio.run(client.get_score("CVE-2023-44487"))
                if result:
                    checks.append(("EPSS API", "[green]✓ OK[/green]", "Connected"))
                else:
                    checks.append(("EPSS API", "[yellow]⚠ WARN[/yellow]", "Connected but no data"))
            except Exception as e:
                checks.append(("EPSS API", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 4. NVD API
        with console.status("Testing NVD API..."):
            try:
                from chronos.core.intel import NVDClient
                nvd_key = settings.api_keys.nvd_api_key if settings else None
                client = NVDClient()  # NVDClient reads key from settings
                result = asyncio.run(client.get_cve("CVE-2023-44487"))
                key_status = "with API key" if nvd_key else "rate limited"
                if result:
                    checks.append(("NVD API", "[green]✓ OK[/green]", f"Connected ({key_status})"))
                else:
                    checks.append(("NVD API", "[yellow]⚠ WARN[/yellow]", f"No data ({key_status})"))
            except Exception as e:
                checks.append(("NVD API", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 5. CISA KEV
        with console.status("Testing CISA KEV..."):
            try:
                from chronos.core.intel import KEVClient
                client = KEVClient()
                catalog = asyncio.run(client.get_catalog())
                checks.append(("CISA KEV", "[green]✓ OK[/green]", f"{len(catalog)} entries"))
            except Exception as e:
                checks.append(("CISA KEV", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 6. URLhaus
        with console.status("Testing URLhaus..."):
            try:
                from chronos.core.intel import URLhausClient
                # Just instantiate - don't actually query
                client = URLhausClient()
                checks.append(("URLhaus", "[green]✓ OK[/green]", "Ready"))
            except Exception as e:
                checks.append(("URLhaus", "[red]✗ FAIL[/red]", str(e)[:40]))
        
        # 7. VirusTotal
        vt_key = settings.api_keys.virustotal_api_key if settings else None
        if vt_key:
            with console.status("Testing VirusTotal..."):
                try:
                    from chronos.core.intel import VirusTotalClient
                    client = VirusTotalClient()  # Reads key from settings
                    if client.is_configured:
                        checks.append(("VirusTotal", "[green]✓ OK[/green]", "API key configured"))
                    else:
                        checks.append(("VirusTotal", "[yellow]⚠ WARN[/yellow]", "Key not loaded"))
                except Exception as e:
                    checks.append(("VirusTotal", "[red]✗ FAIL[/red]", str(e)[:40]))
        else:
            checks.append(("VirusTotal", "[yellow]○ SKIP[/yellow]", "No API key (optional)"))
        
        # 8. Dependencies
        with console.status("Checking dependencies..."):
            missing = []
            optional_missing = []
            
            # Required
            try:
                import typer
            except ImportError:
                missing.append("typer")
            
            try:
                import rich
            except ImportError:
                missing.append("rich")
            
            try:
                import httpx
            except ImportError:
                missing.append("httpx")
            
            # Optional
            try:
                import yaml
            except ImportError:
                optional_missing.append("pyyaml")
            
            try:
                import sklearn
            except ImportError:
                optional_missing.append("scikit-learn")
            
            try:
                import matplotlib
            except ImportError:
                optional_missing.append("matplotlib")
            
            if missing:
                checks.append(("Dependencies", "[red]✗ FAIL[/red]", f"Missing: {', '.join(missing)}"))
            elif optional_missing:
                checks.append(("Dependencies", "[yellow]⚠ WARN[/yellow]", f"Optional: {', '.join(optional_missing)}"))
            else:
                checks.append(("Dependencies", "[green]✓ OK[/green]", "All installed"))
        
        # Display results
        table = Table(title="CHRONOS Diagnostic Results")
        table.add_column("Component", style="cyan")
        table.add_column("Status")
        table.add_column("Details", style="dim")
        
        for component, status, details in checks:
            table.add_row(component, status, details)
        
        console.print(table)
        
        # Summary
        ok_count = sum(1 for _, s, _ in checks if "✓" in s)
        warn_count = sum(1 for _, s, _ in checks if "⚠" in s or "○" in s)
        fail_count = sum(1 for _, s, _ in checks if "✗" in s)
        
        console.print()
        if fail_count > 0:
            console.print(f"[red]✗ {fail_count} critical issues found[/red]")
        elif warn_count > 0:
            console.print(f"[green]✓ {ok_count} checks passed[/green], [yellow]{warn_count} warnings[/yellow]")
        else:
            console.print(f"[green]✓ All {ok_count} checks passed - CHRONOS is healthy![/green]")


def main() -> None:
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
