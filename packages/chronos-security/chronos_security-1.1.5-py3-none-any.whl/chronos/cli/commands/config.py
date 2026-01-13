"""
CHRONOS Config Command
======================

CLI commands for configuration management.
"""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

from chronos.cli.utils import error_handler
from chronos.cli.utils.config import (
    ConfigManager,
    ConfigurationError,
    get_config,
    load_config,
)
from chronos.core.schema import ChronosConfig, DEFAULT_CONFIG

console = Console()

app = typer.Typer(
    name="config",
    help="⚙️ Configuration management commands.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@app.command("show")
def show_command(
    section: Optional[str] = typer.Argument(
        None,
        help="Configuration section to show (e.g., detection, crypto, api).",
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, yaml, json).",
    ),
    defaults: bool = typer.Option(
        False,
        "--defaults",
        "-d",
        help="Show default values instead of current config.",
    ),
) -> None:
    """
    📋 Show current configuration settings.
    
    Display all configuration values or a specific section.
    
    [bold]Examples:[/bold]
        chronos config show
        chronos config show detection
        chronos config show --format yaml
        chronos config show crypto --format json
    """
    with error_handler(console):
        try:
            config = DEFAULT_CONFIG if defaults else get_config()
        except ConfigurationError:
            config = DEFAULT_CONFIG
        
        if section:
            # Show specific section
            if not hasattr(config, section):
                console.print(f"[red]Unknown section:[/red] {section}")
                console.print("\n[dim]Available sections: crypto, detection, analysis, defense, api, logging, integrations[/dim]")
                raise typer.Exit(1)
            
            section_config = getattr(config, section)
            title = f"Configuration: {section}"
            
            if format == "yaml":
                import yaml
                yaml_str = yaml.dump(
                    section_config.model_dump() if hasattr(section_config, "model_dump") else section_config,
                    default_flow_style=False,
                )
                console.print(Syntax(yaml_str, "yaml", theme="monokai"))
            elif format == "json":
                json_str = json.dumps(
                    section_config.model_dump() if hasattr(section_config, "model_dump") else section_config,
                    indent=2,
                )
                console.print(Syntax(json_str, "json", theme="monokai"))
            else:
                _print_section_table(console, section, section_config)
        else:
            # Show all configuration
            if format == "yaml":
                manager = ConfigManager()
                manager._config = config
                yaml_str = manager.export_yaml(config)
                console.print(Syntax(yaml_str, "yaml", theme="monokai"))
            elif format == "json":
                json_str = config.model_dump_json(indent=2)
                console.print(Syntax(json_str, "json", theme="monokai"))
            else:
                _print_config_tree(console, config)


def _print_section_table(console: Console, section: str, config: any) -> None:
    """Print a configuration section as a table."""
    table = Table(title=f"Configuration: {section}", border_style="blue")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Type", style="dim")
    
    config_dict = config.model_dump() if hasattr(config, "model_dump") else config
    
    for key, value in config_dict.items():
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value[:3])
            if len(value) > 3:
                value_str += f" (+{len(value) - 3} more)"
        elif isinstance(value, dict):
            value_str = f"{{...}} ({len(value)} items)"
        else:
            value_str = str(value)
        
        table.add_row(key, value_str, type(value).__name__)
    
    console.print(table)


def _print_config_tree(console: Console, config: ChronosConfig) -> None:
    """Print configuration as a tree view."""
    tree = Tree(
        "[bold blue]CHRONOS Configuration[/bold blue]",
        guide_style="dim",
    )
    
    # Add top-level settings
    general = tree.add("[cyan]General[/cyan]")
    general.add(f"version: [green]{config.version}[/green]")
    general.add(f"project_name: [green]{config.project_name}[/green]")
    general.add(f"security_level: [yellow]{config.security_level}[/yellow]")
    general.add(f"data_directory: [dim]{config.data_directory}[/dim]")
    
    # Add sections
    sections = [
        ("crypto", "🔐 Cryptography", config.crypto),
        ("detection", "🔍 Detection", config.detection),
        ("analysis", "📊 Analysis", config.analysis),
        ("defense", "🛡️ Defense", config.defense),
        ("api", "🌐 API", config.api),
        ("logging", "📝 Logging", config.logging),
        ("integrations", "🔗 Integrations", config.integrations),
    ]
    
    for section_key, section_name, section_config in sections:
        branch = tree.add(f"[cyan]{section_name}[/cyan]")
        section_dict = section_config.model_dump()
        
        for key, value in list(section_dict.items())[:5]:
            if isinstance(value, bool):
                value_str = "[green]✓[/green]" if value else "[red]✗[/red]"
            elif isinstance(value, list):
                value_str = f"[dim][{len(value)} items][/dim]"
            else:
                value_str = f"[white]{value}[/white]"
            branch.add(f"{key}: {value_str}")
        
        if len(section_dict) > 5:
            branch.add(f"[dim]... +{len(section_dict) - 5} more[/dim]")
    
    console.print(tree)


@app.command("get")
def get_command(
    key: str = typer.Argument(
        ...,
        help="Configuration key in dot notation (e.g., detection.enabled).",
    ),
) -> None:
    """
    🔍 Get a specific configuration value.
    
    [bold]Examples:[/bold]
        chronos config get security_level
        chronos config get detection.enabled
        chronos config get crypto.quantum_resistant
    """
    with error_handler(console):
        manager = ConfigManager()
        try:
            manager.load()
        except ConfigurationError:
            manager._config = DEFAULT_CONFIG
        
        value = manager.get(key)
        
        if value is None:
            console.print(f"[red]Key not found:[/red] {key}")
            raise typer.Exit(1)
        
        if isinstance(value, (dict, list)):
            console.print(json.dumps(value, indent=2))
        else:
            console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")


@app.command("set")
def set_command(
    key: str = typer.Argument(
        ...,
        help="Configuration key in dot notation.",
    ),
    value: str = typer.Argument(
        ...,
        help="Value to set.",
    ),
    save: bool = typer.Option(
        True,
        "--save/--no-save",
        "-s/-S",
        help="Save changes to config file.",
    ),
) -> None:
    """
    ✏️ Set a configuration value.
    
    [bold]Examples:[/bold]
        chronos config set security_level high
        chronos config set detection.enabled true
        chronos config set api.port 9000
    """
    with error_handler(console):
        manager = ConfigManager()
        try:
            manager.load()
        except ConfigurationError:
            manager._config = DEFAULT_CONFIG
        
        # Parse value
        parsed_value: any
        if value.lower() in ("true", "yes", "on"):
            parsed_value = True
        elif value.lower() in ("false", "no", "off"):
            parsed_value = False
        elif value.isdigit():
            parsed_value = int(value)
        else:
            try:
                parsed_value = float(value)
            except ValueError:
                parsed_value = value
        
        try:
            manager.set(key, parsed_value)
            console.print(f"[green]✓[/green] Set [cyan]{key}[/cyan] = [green]{parsed_value}[/green]")
            
            if save:
                path = manager.save()
                console.print(f"[dim]Saved to {path}[/dim]")
        except ConfigurationError as e:
            console.print(f"[red]Error:[/red] {e.message}")
            raise typer.Exit(1)


@app.command("init")
def init_command(
    path: Path = typer.Argument(
        Path(".chronos/config.yaml"),
        help="Path to create configuration file.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration.",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        "-i",
        help="Interactive configuration setup.",
    ),
) -> None:
    """
    🚀 Initialize a new configuration file.
    
    Creates a default configuration file with all settings.
    
    [bold]Examples:[/bold]
        chronos config init
        chronos config init ./custom-config.yaml
        chronos config init --interactive
    """
    with error_handler(console):
        if path.exists() and not force:
            console.print(f"[yellow]Configuration already exists:[/yellow] {path}")
            console.print("Use [bold]--force[/bold] to overwrite.")
            raise typer.Exit(1)
        
        # Create directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config = DEFAULT_CONFIG
        
        if interactive:
            config = _interactive_setup(console)
        
        # Export and save
        manager = ConfigManager()
        manager._config = config
        yaml_content = manager.export_yaml(config)
        
        path.write_text(yaml_content, encoding="utf-8")
        
        console.print(Panel(
            f"[green]✓[/green] Configuration created at [cyan]{path}[/cyan]\n\n"
            f"[bold]Next steps:[/bold]\n"
            f"  • Edit the file to customize settings\n"
            f"  • Run [bold]chronos config show[/bold] to view configuration\n"
            f"  • Run [bold]chronos config validate[/bold] to check for errors",
            title="Configuration Initialized",
            border_style="green",
        ))


def _interactive_setup(console: Console) -> ChronosConfig:
    """Interactive configuration setup."""
    from chronos.core.schema import SecurityLevel
    
    console.print(Panel(
        "Answer the following questions to configure CHRONOS.",
        title="Interactive Setup",
        border_style="blue",
    ))
    
    config_dict = DEFAULT_CONFIG.model_dump()
    
    # Security level
    console.print("\n[bold]Security Level[/bold]")
    console.print("[dim]Options: low, medium, high, maximum[/dim]")
    level = console.input("[cyan]? Security level [high]: [/cyan]").strip().lower()
    if level in ("low", "medium", "high", "maximum"):
        config_dict["security_level"] = level
    
    # Quantum resistant
    console.print("\n[bold]Quantum Resistance[/bold]")
    qr = console.input("[cyan]? Enable quantum-resistant crypto [Y/n]: [/cyan]").strip().lower()
    config_dict["crypto"]["quantum_resistant"] = qr not in ("n", "no", "false")
    
    # Detection
    console.print("\n[bold]Threat Detection[/bold]")
    det = console.input("[cyan]? Enable threat detection [Y/n]: [/cyan]").strip().lower()
    config_dict["detection"]["enabled"] = det not in ("n", "no", "false")
    
    # API
    console.print("\n[bold]API Server[/bold]")
    api = console.input("[cyan]? Enable API server [y/N]: [/cyan]").strip().lower()
    config_dict["api"]["enabled"] = api in ("y", "yes", "true")
    
    if config_dict["api"]["enabled"]:
        port = console.input("[cyan]? API port [8000]: [/cyan]").strip()
        if port.isdigit():
            config_dict["api"]["port"] = int(port)
    
    return ChronosConfig(**config_dict)


@app.command("validate")
def validate_command(
    path: Optional[Path] = typer.Argument(
        None,
        help="Path to configuration file to validate.",
    ),
) -> None:
    """
    ✅ Validate configuration file.
    
    Checks the configuration for errors and warnings.
    """
    with error_handler(console):
        manager = ConfigManager(config_path=path)
        
        try:
            config = manager.load()
            manager.validate()
            
            console.print(Panel(
                "[green]✓[/green] Configuration is valid!\n\n"
                f"[bold]Version:[/bold] {config.version}\n"
                f"[bold]Security Level:[/bold] {config.security_level}\n"
                f"[bold]Modules Enabled:[/bold]\n"
                f"  • Detection: {'✓' if config.detection.enabled else '✗'}\n"
                f"  • Analysis: {'✓' if config.analysis.enabled else '✗'}\n"
                f"  • Defense: {'✓' if config.defense.enabled else '✗'}\n"
                f"  • API: {'✓' if config.api.enabled else '✗'}",
                title="Validation Results",
                border_style="green",
            ))
        except ConfigurationError as e:
            console.print(Panel(
                f"[red]✗[/red] Configuration validation failed!\n\n{e.message}",
                title="Validation Failed",
                border_style="red",
            ))
            raise typer.Exit(1)


@app.command("export")
def export_command(
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Export format (yaml, json, env).",
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path.",
    ),
) -> None:
    """
    📤 Export configuration to file.
    
    [bold]Examples:[/bold]
        chronos config export --format yaml
        chronos config export --format json -o config.json
        chronos config export --format env -o .env
    """
    with error_handler(console):
        manager = ConfigManager()
        try:
            manager.load()
        except ConfigurationError:
            manager._config = DEFAULT_CONFIG
        
        if format == "yaml":
            content = manager.export_yaml()
            syntax = "yaml"
        elif format == "json":
            content = manager.export_json()
            syntax = "json"
        elif format == "env":
            content = manager.export_env()
            syntax = "bash"
        else:
            console.print(f"[red]Unknown format:[/red] {format}")
            raise typer.Exit(1)
        
        if output:
            output.write_text(content, encoding="utf-8")
            console.print(f"[green]✓[/green] Exported to [cyan]{output}[/cyan]")
        else:
            console.print(Syntax(content, syntax, theme="monokai"))


@app.command("reset")
def reset_command(
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt.",
    ),
) -> None:
    """
    🔄 Reset configuration to defaults.
    
    [bold yellow]Warning:[/bold yellow] This will overwrite your current configuration!
    """
    with error_handler(console):
        if not confirm:
            response = console.input(
                "[yellow]⚠[/yellow] This will reset all settings to defaults. Continue? [y/N]: "
            ).strip().lower()
            if response not in ("y", "yes"):
                console.print("[dim]Reset cancelled.[/dim]")
                raise typer.Exit(0)
        
        manager = ConfigManager()
        manager.reset()
        manager.save()
        
        console.print("[green]✓[/green] Configuration reset to defaults.")


@app.command("path")
def path_command() -> None:
    """
    📂 Show configuration file paths.
    
    Displays the locations where CHRONOS looks for configuration files.
    """
    from chronos.cli.utils.config import CONFIG_LOCATIONS
    
    with error_handler(console):
        table = Table(title="Configuration File Locations", border_style="blue")
        table.add_column("Priority", style="dim")
        table.add_column("Path", style="cyan")
        table.add_column("Status", style="white")
        
        for i, location in enumerate(CONFIG_LOCATIONS, 1):
            path = Path(location)
            status = "[green]Found[/green]" if path.exists() else "[dim]Not found[/dim]"
            table.add_row(str(i), str(path), status)
        
        console.print(table)
        
        # Show environment variables
        console.print("\n[bold]Environment Variable Prefix:[/bold] CHRONOS_")
        console.print("[dim]Example: CHRONOS_SECURITY_LEVEL=high[/dim]")
