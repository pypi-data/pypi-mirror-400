"""
CHRONOS CLI - Incident Response Commands
========================================

Execute and manage IR playbooks.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from chronos.cli.utils import error_handler

console = Console()
app = typer.Typer(help="🚨 Incident response and playbook execution")


@app.command("list")
def ir_list(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Filter by tag"),
) -> None:
    """
    📋 List available IR playbooks.
    """
    with error_handler(console):
        from chronos.core.playbooks import PlaybookEngine
        
        engine = PlaybookEngine()
        
        # Load custom playbooks from default location
        engine.load_playbooks_directory()
        
        playbooks = engine.list_playbooks()
        
        if tag:
            playbooks = [p for p in playbooks if tag.lower() in [t.lower() for t in p["tags"]]]
        
        if not playbooks:
            console.print("[yellow]No playbooks found[/yellow]")
            if tag:
                console.print(f"[dim]Try removing the --tag filter[/dim]")
            return
        
        table = Table(title=f"IR Playbooks ({len(playbooks)})")
        table.add_column("Name", style="cyan")
        table.add_column("Description", max_width=40)
        table.add_column("Triggers", style="dim")
        table.add_column("Actions", justify="center")
        table.add_column("Status")
        
        for pb in playbooks:
            status = "[green]Enabled[/green]" if pb["enabled"] else "[red]Disabled[/red]"
            triggers = ", ".join(pb["triggers"][:3])
            if len(pb["triggers"]) > 3:
                triggers += "..."
            
            table.add_row(
                pb["name"],
                pb["description"][:40],
                triggers,
                str(pb["action_count"]),
                status,
            )
        
        console.print(table)


@app.command("show")
def ir_show(
    name: str = typer.Argument(..., help="Playbook name to display"),
) -> None:
    """
    🔍 Show details of a playbook.
    """
    with error_handler(console):
        from chronos.core.playbooks import PlaybookEngine
        
        engine = PlaybookEngine()
        engine.load_playbooks_directory()
        
        playbook = engine.get_playbook(name)
        
        if not playbook:
            # Try fuzzy match
            all_playbooks = engine.list_playbooks()
            matches = [p["name"] for p in all_playbooks if name.lower() in p["name"].lower()]
            
            if matches:
                console.print(f"[yellow]Playbook '{name}' not found. Did you mean:[/yellow]")
                for m in matches:
                    console.print(f"  • {m}")
            else:
                console.print(f"[red]Playbook not found: {name}[/red]")
            return
        
        # Display playbook details
        actions_text = ""
        for i, action in enumerate(playbook.actions, 1):
            cond = f" [dim](if {action.condition})[/dim]" if action.condition else ""
            actions_text += f"\n  {i}. [{action.action_type.value}] {action.name}{cond}"
            actions_text += f"\n     [dim]Target: {action.target}[/dim]"
        
        console.print(Panel(
            f"[bold]Name:[/bold] {playbook.name}\n"
            f"[bold]Version:[/bold] {playbook.version}\n"
            f"[bold]Author:[/bold] {playbook.author}\n"
            f"[bold]Enabled:[/bold] {'Yes' if playbook.enabled else 'No'}\n\n"
            f"[bold]Description:[/bold]\n{playbook.description}\n\n"
            f"[bold]Triggers:[/bold] {', '.join(playbook.triggers)}\n"
            f"[bold]Severity Threshold:[/bold] {playbook.severity_threshold}\n"
            f"[bold]Tags:[/bold] {', '.join(playbook.tags)}\n\n"
            f"[bold]Actions ({len(playbook.actions)}):[/bold]"
            f"{actions_text}",
            title=f"Playbook: {playbook.name}",
            border_style="blue",
        ))


@app.command("run")
def ir_run(
    name: str = typer.Argument(..., help="Playbook name to execute"),
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Simulate without changes (default: dry-run)"),
    target: Optional[str] = typer.Option(None, "--target", "-t", help="Override target parameter"),
    var: Optional[list[str]] = typer.Option(None, "--var", "-v", help="Set context variable (key=value)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation for live execution"),
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """
    ▶️ Execute an IR playbook.
    
    By default runs in dry-run mode to show what would happen.
    Use --execute to perform real actions (requires confirmation).
    
    Example:
        chronos ir run malware_response --var file_path=/path/to/malware
    """
    with error_handler(console):
        from chronos.core.playbooks import PlaybookEngine
        import json as json_module
        
        engine = PlaybookEngine()
        engine.load_playbooks_directory()
        
        playbook = engine.get_playbook(name)
        
        if not playbook:
            console.print(f"[red]Playbook not found: {name}[/red]")
            console.print("[dim]Use 'chronos ir list' to see available playbooks[/dim]")
            raise typer.Exit(1)
        
        # Build context from variables
        context = {}
        if var:
            for v in var:
                if "=" in v:
                    key, value = v.split("=", 1)
                    context[key.strip()] = value.strip()
        
        if target:
            context["target"] = target
            context["file_path"] = target
        
        # Confirmation for live execution
        if not dry_run and not force:
            console.print(Panel(
                f"[bold red]⚠ LIVE EXECUTION WARNING[/bold red]\n\n"
                f"Playbook: [cyan]{name}[/cyan]\n"
                f"Actions: {len(playbook.actions)}\n"
                f"Context: {context or '(none)'}\n\n"
                "This will execute real actions that may:\n"
                "  • Quarantine files\n"
                "  • Block IP addresses\n"
                "  • Disable user accounts\n"
                "  • Kill processes\n"
                "  • Modify system configuration",
                title="Confirmation Required",
                border_style="red",
            ))
            
            if not Confirm.ask("Are you sure you want to proceed?"):
                console.print("[yellow]Execution cancelled[/yellow]")
                raise typer.Exit(0)
        
        # Execute
        mode = "[DRY-RUN]" if dry_run else "[LIVE]"
        console.print(f"\n{mode} Executing playbook: [cyan]{name}[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task("Running playbook...", total=None)
            
            result = engine.execute(
                playbook_name=name,
                context=context,
                dry_run=dry_run,
                require_confirmation=False,  # Already confirmed above
            )
        
        if json_output:
            console.print(json_module.dumps(result.to_dict(), indent=2))
            return
        
        # Display results
        if result.success:
            status = "[green]✓ SUCCESS[/green]"
            border = "green"
        else:
            status = "[red]✗ FAILED[/red]"
            border = "red"
        
        duration = (result.completed_at - result.started_at).total_seconds()
        
        console.print(Panel(
            f"{status} {'(DRY-RUN)' if dry_run else ''}\n\n"
            f"[bold]Playbook:[/bold] {result.playbook_name}\n"
            f"[bold]Duration:[/bold] {duration:.2f}s\n"
            f"[bold]Actions Executed:[/bold] {result.actions_executed}\n"
            f"[bold]Actions Failed:[/bold] {result.actions_failed}",
            title="Execution Result",
            border_style=border,
        ))
        
        # Action details
        if result.action_results:
            table = Table(title="Action Results")
            table.add_column("Action", style="cyan")
            table.add_column("Status")
            table.add_column("Details", max_width=50)
            
            for ar in result.action_results:
                if ar.get("skipped"):
                    status = "[dim]SKIPPED[/dim]"
                    details = ar.get("reason", "")[:50]
                elif ar.get("success"):
                    status = "[green]✓ OK[/green]"
                    details = ar.get("message", "")[:50]
                else:
                    status = "[red]✗ FAIL[/red]"
                    details = ar.get("error", "")[:50]
                
                table.add_row(ar.get("action", "Unknown"), status, details)
            
            console.print(table)
        
        if result.error_message:
            console.print(f"\n[red]Error: {result.error_message}[/red]")


@app.command("history")
def ir_history(
    playbook: Optional[str] = typer.Option(None, "--playbook", "-p", help="Filter by playbook"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum entries to show"),
) -> None:
    """
    📜 Show IR action history.
    """
    with error_handler(console):
        from chronos.core.database import get_db
        
        db = get_db()
        actions = db.get_actions(playbook=playbook, limit=limit)
        
        if not actions:
            console.print("[yellow]No IR actions recorded[/yellow]")
            return
        
        table = Table(title=f"IR Action History ({len(actions)} shown)")
        table.add_column("Time", style="dim")
        table.add_column("Playbook", style="cyan")
        table.add_column("Action")
        table.add_column("Target", style="dim", max_width=30)
        table.add_column("Status")
        
        status_styles = {
            "executed": "[green]✓ Executed[/green]",
            "dry_run": "[yellow]● Dry-Run[/yellow]",
            "failed": "[red]✗ Failed[/red]",
            "pending": "[dim]○ Pending[/dim]",
        }
        
        for action in actions:
            time_str = action.created_at.strftime("%m-%d %H:%M") if action.created_at else "N/A"
            status = status_styles.get(action.status.value, action.status.value)
            
            table.add_row(
                time_str,
                action.playbook,
                action.action_name,
                action.target[:30] if action.target else "-",
                status,
            )
        
        console.print(table)


@app.command("create")
def ir_create(
    name: str = typer.Argument(..., help="Name for the new playbook"),
    description: str = typer.Option("Custom playbook", "--description", "-d", help="Playbook description"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output YAML file path"),
) -> None:
    """
    ✨ Create a new playbook template.
    """
    with error_handler(console):
        from chronos.core.settings import get_settings
        
        settings = get_settings()
        
        if output is None:
            output = settings.playbooks_path / f"{name.lower().replace(' ', '_')}.yaml"
        
        # Create template
        template = f'''name: {name}
description: {description}
version: "1.0.0"
author: CHRONOS User
triggers:
  - custom_trigger
severity_threshold: medium
enabled: true
tags:
  - custom
actions:
  - name: Example Action
    type: notify
    description: Send a notification
    target: security-team
    params:
      channel: log
      message: "Playbook triggered: {{{{trigger_reason}}}}"
    continue_on_error: true
    timeout: 30
  
  # Add more actions below:
  # - name: Quarantine File
  #   type: quarantine_file
  #   target: "{{{{file_path}}}}"
  #   params:
  #     backup: true
  #
  # - name: Block IP
  #   type: block_ip
  #   target: "{{{{source_ip}}}}"
  #   params:
  #     duration_hours: 24
'''
        
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(template)
        
        console.print(Panel(
            f"[green]✓ Playbook template created[/green]\n\n"
            f"[bold]File:[/bold] {output.absolute()}\n\n"
            "Edit the YAML file to customize:\n"
            "  • Add/remove triggers\n"
            "  • Configure actions\n"
            "  • Set conditions\n\n"
            "[bold]Available action types:[/bold]\n"
            "  • quarantine_file - Isolate suspicious files\n"
            "  • block_ip - Block network addresses\n"
            "  • disable_user - Lock user accounts\n"
            "  • kill_process - Terminate processes\n"
            "  • notify - Send alerts\n"
            "  • collect_evidence - Gather forensic data\n"
            "  • run_command - Execute custom commands",
            title="Playbook Created",
            border_style="green",
        ))


@app.command("validate")
def ir_validate(
    playbook_file: Path = typer.Argument(..., help="Playbook YAML file to validate", exists=True),
) -> None:
    """
    ✅ Validate a playbook YAML file.
    """
    with error_handler(console):
        from chronos.core.playbooks import Playbook
        
        try:
            content = playbook_file.read_text()
            playbook = Playbook.from_yaml(content)
            
            # Validation checks
            issues = []
            warnings = []
            
            if not playbook.name:
                issues.append("Missing playbook name")
            
            if not playbook.actions:
                issues.append("No actions defined")
            
            if not playbook.triggers:
                warnings.append("No triggers defined - playbook won't auto-execute")
            
            for i, action in enumerate(playbook.actions, 1):
                if not action.target and action.action_type.value not in ("notify", "custom"):
                    warnings.append(f"Action {i} ({action.name}) has no target")
            
            if issues:
                console.print(Panel(
                    "[red]✗ Validation Failed[/red]\n\n"
                    "[bold]Errors:[/bold]\n" +
                    "\n".join(f"  • {i}" for i in issues) +
                    ("\n\n[bold]Warnings:[/bold]\n" + "\n".join(f"  • {w}" for w in warnings) if warnings else ""),
                    title="Validation Result",
                    border_style="red",
                ))
                raise typer.Exit(1)
            
            status = "[green]✓ Valid[/green]"
            if warnings:
                status += " [yellow](with warnings)[/yellow]"
            
            console.print(Panel(
                f"{status}\n\n"
                f"[bold]Playbook:[/bold] {playbook.name}\n"
                f"[bold]Version:[/bold] {playbook.version}\n"
                f"[bold]Actions:[/bold] {len(playbook.actions)}\n"
                f"[bold]Triggers:[/bold] {len(playbook.triggers)}\n" +
                ("\n[bold]Warnings:[/bold]\n" + "\n".join(f"  • {w}" for w in warnings) if warnings else ""),
                title="Validation Result",
                border_style="green" if not warnings else "yellow",
            ))
            
        except Exception as e:
            console.print(Panel(
                f"[red]✗ Parse Error[/red]\n\n{str(e)}",
                title="Validation Failed",
                border_style="red",
            ))
            raise typer.Exit(1)
