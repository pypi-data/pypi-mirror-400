"""
CHRONOS Incident Response Playbooks
===================================

YAML-based playbook system for automated incident response actions
with dry-run support and audit trail.
"""

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union
import re

try:
    import yaml
except ImportError:
    yaml = None

from chronos.core.database import (
    Action,
    ActionStatus,
    EventType,
    get_db,
)
from chronos.core.settings import get_settings
from chronos.utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Models
# =============================================================================

class ActionType(str, Enum):
    """Types of IR actions."""
    QUARANTINE_FILE = "quarantine_file"
    BLOCK_IP = "block_ip"
    DISABLE_USER = "disable_user"
    KILL_PROCESS = "kill_process"
    NOTIFY = "notify"
    RUN_COMMAND = "run_command"
    COLLECT_EVIDENCE = "collect_evidence"
    ISOLATE_HOST = "isolate_host"
    RESTORE_FILE = "restore_file"
    ENABLE_USER = "enable_user"
    CUSTOM = "custom"


@dataclass
class PlaybookAction:
    """Single playbook action definition."""
    name: str
    action_type: ActionType
    description: str
    target: str  # File path, IP, username, etc.
    params: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None  # Condition expression
    continue_on_error: bool = False
    timeout_seconds: int = 60


@dataclass
class Playbook:
    """Incident response playbook definition."""
    name: str
    description: str
    version: str
    author: str
    triggers: List[str]  # Event types that trigger this playbook
    actions: List[PlaybookAction]
    severity_threshold: str = "medium"  # Minimum severity to trigger
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> "Playbook":
        """Parse playbook from YAML content."""
        if yaml is None:
            raise ImportError("PyYAML is required for playbook parsing")
        
        data = yaml.safe_load(yaml_content)
        
        actions = []
        for action_data in data.get("actions", []):
            action_type = ActionType(action_data.get("type", "custom"))
            actions.append(PlaybookAction(
                name=action_data.get("name", "Unnamed Action"),
                action_type=action_type,
                description=action_data.get("description", ""),
                target=action_data.get("target", ""),
                params=action_data.get("params", {}),
                condition=action_data.get("condition"),
                continue_on_error=action_data.get("continue_on_error", False),
                timeout_seconds=action_data.get("timeout", 60),
            ))
        
        return cls(
            name=data.get("name", "Unnamed Playbook"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", "Unknown"),
            triggers=data.get("triggers", []),
            actions=actions,
            severity_threshold=data.get("severity_threshold", "medium"),
            enabled=data.get("enabled", True),
            tags=data.get("tags", []),
        )
    
    def to_yaml(self) -> str:
        """Serialize playbook to YAML."""
        if yaml is None:
            raise ImportError("PyYAML is required for playbook serialization")
        
        data = {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "triggers": self.triggers,
            "severity_threshold": self.severity_threshold,
            "enabled": self.enabled,
            "tags": self.tags,
            "actions": [
                {
                    "name": a.name,
                    "type": a.action_type.value,
                    "description": a.description,
                    "target": a.target,
                    "params": a.params,
                    "condition": a.condition,
                    "continue_on_error": a.continue_on_error,
                    "timeout": a.timeout_seconds,
                }
                for a in self.actions
            ],
        }
        
        return yaml.dump(data, default_flow_style=False, sort_keys=False)


@dataclass
class ExecutionResult:
    """Result of playbook execution."""
    playbook_name: str
    started_at: datetime
    completed_at: datetime
    dry_run: bool
    success: bool
    actions_executed: int
    actions_failed: int
    action_results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "playbook_name": self.playbook_name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": (self.completed_at - self.started_at).total_seconds(),
            "dry_run": self.dry_run,
            "success": self.success,
            "actions_executed": self.actions_executed,
            "actions_failed": self.actions_failed,
            "action_results": self.action_results,
            "error_message": self.error_message,
        }


# =============================================================================
# Built-in Playbooks
# =============================================================================

BUILTIN_PLAYBOOKS = {
    "malware_response": """
name: Malware Response Playbook
description: Automated response to malware detection events
version: "1.0.0"
author: CHRONOS
triggers:
  - malware_detected
  - ioc_detected
severity_threshold: high
enabled: true
tags:
  - malware
  - automated
actions:
  - name: Quarantine Infected File
    type: quarantine_file
    description: Move infected file to quarantine directory
    target: "{{file_path}}"
    params:
      backup: true
    continue_on_error: false
    timeout: 30
  
  - name: Kill Malicious Process
    type: kill_process
    description: Terminate any running malicious process
    target: "{{process_name}}"
    condition: "process_running"
    continue_on_error: true
    timeout: 10
  
  - name: Collect Evidence
    type: collect_evidence
    description: Gather artifacts for forensic analysis
    target: "{{file_path}}"
    params:
      collect_hash: true
      collect_metadata: true
      collect_strings: true
    continue_on_error: true
    timeout: 60
  
  - name: Send Alert
    type: notify
    description: Send notification to security team
    target: security-team
    params:
      channel: slack
      message: "Malware detected and quarantined: {{file_path}}"
      severity: high
    continue_on_error: true
    timeout: 15
""",
    
    "brute_force_response": """
name: Brute Force Attack Response
description: Respond to detected brute force authentication attempts
version: "1.0.0"
author: CHRONOS
triggers:
  - auth_failure_spike
  - brute_force_detected
severity_threshold: medium
enabled: true
tags:
  - authentication
  - automated
actions:
  - name: Block Attacking IP
    type: block_ip
    description: Add IP to firewall blocklist
    target: "{{source_ip}}"
    params:
      duration_hours: 24
      rule_comment: "CHRONOS: Brute force block"
    continue_on_error: false
    timeout: 30
  
  - name: Disable Targeted Account
    type: disable_user
    description: Temporarily disable the targeted user account
    target: "{{target_user}}"
    condition: "failed_attempts > 20"
    params:
      reason: "Account locked due to suspicious activity"
      notify_user: true
    continue_on_error: true
    timeout: 30
  
  - name: Collect Authentication Logs
    type: collect_evidence
    description: Gather authentication logs for analysis
    target: "/var/log/auth.log"
    params:
      last_hours: 24
      filter_ip: "{{source_ip}}"
    continue_on_error: true
    timeout: 60
  
  - name: Alert Security Team
    type: notify
    description: Send high priority alert
    target: security-team
    params:
      channel: pagerduty
      message: "Brute force attack detected from {{source_ip}} targeting {{target_user}}"
      severity: high
    continue_on_error: true
    timeout: 15
""",
    
    "phishing_response": """
name: Phishing Incident Response
description: Respond to confirmed phishing emails
version: "1.0.0"
author: CHRONOS
triggers:
  - phishing_confirmed
  - phishing_high_confidence
severity_threshold: high
enabled: true
tags:
  - phishing
  - email
actions:
  - name: Block Sender Domain
    type: block_ip
    description: Add sender domain to email blocklist
    target: "{{sender_domain}}"
    params:
      block_type: domain
      duration_hours: 168
    continue_on_error: true
    timeout: 30
  
  - name: Block Malicious URLs
    type: block_ip
    description: Block URLs found in phishing email
    target: "{{malicious_urls}}"
    params:
      block_type: url
      add_to_proxy: true
    continue_on_error: true
    timeout: 60
  
  - name: Notify Recipients
    type: notify
    description: Alert users who received the phishing email
    target: "{{recipients}}"
    params:
      channel: email
      template: phishing_warning
      message: "A phishing email was detected. Do not click any links."
    continue_on_error: true
    timeout: 30
  
  - name: Create Incident Ticket
    type: notify
    description: Create incident ticket for tracking
    target: security-team
    params:
      channel: jira
      project: SEC
      issue_type: Incident
      priority: High
    continue_on_error: true
    timeout: 20
""",
    
    "data_exfiltration_response": """
name: Data Exfiltration Response
description: Respond to suspected data exfiltration
version: "1.0.0"
author: CHRONOS
triggers:
  - data_exfiltration_detected
  - unusual_data_transfer
severity_threshold: critical
enabled: true
tags:
  - data_loss
  - critical
actions:
  - name: Isolate Host
    type: isolate_host
    description: Network isolate the suspected host
    target: "{{host_ip}}"
    params:
      isolation_level: full
      allow_management: true
    continue_on_error: false
    timeout: 60
  
  - name: Disable User Account
    type: disable_user
    description: Disable the user account associated with activity
    target: "{{username}}"
    params:
      reason: "Suspected data exfiltration"
      preserve_session: false
    continue_on_error: false
    timeout: 30
  
  - name: Collect Network Evidence
    type: collect_evidence
    description: Capture network flow data
    target: "{{host_ip}}"
    params:
      collect_netflow: true
      collect_pcap: true
      duration_minutes: 30
    continue_on_error: true
    timeout: 1800
  
  - name: Executive Alert
    type: notify
    description: Notify executive leadership
    target: executives
    params:
      channel: email
      priority: critical
      message: "CRITICAL: Suspected data exfiltration detected"
    continue_on_error: true
    timeout: 15
"""
}


# =============================================================================
# Action Handlers
# =============================================================================

class ActionHandler:
    """Base class for action handlers."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        """Check if handler can execute this action type."""
        raise NotImplementedError
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute the action.
        
        Args:
            action: Action to execute
            context: Execution context with variables
            dry_run: If True, simulate without making changes
        
        Returns:
            Result dictionary with status and details
        """
        raise NotImplementedError
    
    def _substitute_variables(self, text: str, context: Dict[str, Any]) -> str:
        """Substitute {{variable}} patterns with context values."""
        if not text:
            return text
        
        pattern = r"\{\{(\w+)\}\}"
        
        def replacer(match):
            var_name = match.group(1)
            return str(context.get(var_name, match.group(0)))
        
        return re.sub(pattern, replacer, text)


class QuarantineHandler(ActionHandler):
    """Handle file quarantine actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type in (ActionType.QUARANTINE_FILE, ActionType.RESTORE_FILE)
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        target_path = Path(target)
        
        settings = get_settings()
        quarantine_dir = settings.quarantine_path
        
        if action.action_type == ActionType.QUARANTINE_FILE:
            if not target_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {target}",
                }
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "message": f"Would quarantine: {target}",
                    "destination": str(quarantine_dir / target_path.name),
                }
            
            # Create quarantine directory if needed
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file to quarantine
            dest = quarantine_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{target_path.name}"
            shutil.move(str(target_path), str(dest))
            
            return {
                "success": True,
                "message": f"Quarantined: {target}",
                "destination": str(dest),
            }
        
        else:  # RESTORE_FILE
            # Find file in quarantine
            matches = list(quarantine_dir.glob(f"*_{target_path.name}"))
            
            if not matches:
                return {
                    "success": False,
                    "error": f"File not found in quarantine: {target_path.name}",
                }
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "message": f"Would restore: {matches[-1].name}",
                }
            
            # Restore most recent match
            shutil.move(str(matches[-1]), str(target_path))
            
            return {
                "success": True,
                "message": f"Restored: {target}",
            }


class BlockIPHandler(ActionHandler):
    """Handle IP/domain blocking actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type == ActionType.BLOCK_IP
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        block_type = action.params.get("block_type", "ip")
        duration = action.params.get("duration_hours", 24)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would block {block_type}: {target} for {duration} hours",
            }
        
        # Platform-specific blocking
        if sys.platform == "win32":
            # Windows - use netsh for IP blocking
            if block_type == "ip":
                cmd = f'netsh advfirewall firewall add rule name="CHRONOS_BLOCK_{target}" dir=in action=block remoteip={target}'
            else:
                return {
                    "success": False,
                    "error": "Domain blocking requires DNS/proxy configuration on Windows",
                }
        else:
            # Linux - use iptables
            if block_type == "ip":
                cmd = f"iptables -A INPUT -s {target} -j DROP"
            else:
                return {
                    "success": False,
                    "error": "Domain blocking requires DNS/proxy configuration",
                }
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.timeout_seconds,
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr or "Command failed",
                }
            
            return {
                "success": True,
                "message": f"Blocked {block_type}: {target}",
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class UserHandler(ActionHandler):
    """Handle user enable/disable actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type in (ActionType.DISABLE_USER, ActionType.ENABLE_USER)
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        disable = action.action_type == ActionType.DISABLE_USER
        
        if dry_run:
            action_word = "disable" if disable else "enable"
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would {action_word} user: {target}",
            }
        
        # Platform-specific user management
        if sys.platform == "win32":
            action_flag = "/active:no" if disable else "/active:yes"
            cmd = f"net user {target} {action_flag}"
        else:
            # Linux - use usermod
            if disable:
                cmd = f"usermod -L {target}"
            else:
                cmd = f"usermod -U {target}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.timeout_seconds,
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": result.stderr or "Command failed",
                }
            
            action_word = "Disabled" if disable else "Enabled"
            return {
                "success": True,
                "message": f"{action_word} user: {target}",
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class ProcessHandler(ActionHandler):
    """Handle process kill actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type == ActionType.KILL_PROCESS
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would kill process: {target}",
            }
        
        if sys.platform == "win32":
            cmd = f"taskkill /F /IM {target}"
        else:
            cmd = f"pkill -9 -f {target}"
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.timeout_seconds,
            )
            
            # Process might not exist, which is okay
            return {
                "success": True,
                "message": f"Kill command executed for: {target}",
                "return_code": result.returncode,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class NotifyHandler(ActionHandler):
    """Handle notification actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type == ActionType.NOTIFY
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        message = self._substitute_variables(action.params.get("message", ""), context)
        channel = action.params.get("channel", "log")
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would notify {target} via {channel}: {message[:100]}",
            }
        
        # For now, just log the notification
        # In production, this would integrate with Slack, PagerDuty, email, etc.
        logger.info(f"IR NOTIFICATION [{channel}] to {target}: {message}")
        
        return {
            "success": True,
            "message": f"Notification sent to {target} via {channel}",
            "channel": channel,
            "content": message[:200],
        }


class CommandHandler(ActionHandler):
    """Handle custom command execution."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type in (ActionType.RUN_COMMAND, ActionType.CUSTOM)
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        command = self._substitute_variables(action.params.get("command", ""), context)
        
        if not command:
            return {
                "success": False,
                "error": "No command specified",
            }
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would run: {command}",
            }
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=action.timeout_seconds,
            )
            
            return {
                "success": result.returncode == 0,
                "message": "Command executed",
                "stdout": result.stdout[:1000],
                "stderr": result.stderr[:500],
                "return_code": result.returncode,
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }


class EvidenceHandler(ActionHandler):
    """Handle evidence collection actions."""
    
    def can_handle(self, action: PlaybookAction) -> bool:
        return action.action_type == ActionType.COLLECT_EVIDENCE
    
    def execute(
        self,
        action: PlaybookAction,
        context: Dict[str, Any],
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        target = self._substitute_variables(action.target, context)
        target_path = Path(target)
        
        collect_hash = action.params.get("collect_hash", True)
        collect_metadata = action.params.get("collect_metadata", True)
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "message": f"Would collect evidence from: {target}",
            }
        
        evidence = {
            "target": target,
            "collected_at": datetime.now().isoformat(),
        }
        
        if target_path.exists():
            if collect_metadata:
                stat = target_path.stat()
                evidence["metadata"] = {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
            
            if collect_hash:
                import hashlib
                sha256 = hashlib.sha256()
                with open(target_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha256.update(chunk)
                evidence["sha256"] = sha256.hexdigest()
        
        return {
            "success": True,
            "message": "Evidence collected",
            "evidence": evidence,
        }


# =============================================================================
# Playbook Engine
# =============================================================================

class PlaybookEngine:
    """
    Execute incident response playbooks.
    
    Features:
    - YAML playbook parsing
    - Dry-run by default
    - Audit trail for all actions
    - Built-in playbooks for common scenarios
    """
    
    HANDLERS: List[ActionHandler] = [
        QuarantineHandler(),
        BlockIPHandler(),
        UserHandler(),
        ProcessHandler(),
        NotifyHandler(),
        CommandHandler(),
        EvidenceHandler(),
    ]
    
    def __init__(self):
        self._db = get_db()
        self._settings = get_settings()
        self._playbooks: Dict[str, Playbook] = {}
        self._load_builtin_playbooks()
    
    def _load_builtin_playbooks(self) -> None:
        """Load built-in playbooks."""
        for name, yaml_content in BUILTIN_PLAYBOOKS.items():
            try:
                playbook = Playbook.from_yaml(yaml_content)
                self._playbooks[name] = playbook
            except Exception as e:
                logger.error(f"Failed to load builtin playbook {name}: {e}")
    
    def load_playbook(self, path: Path) -> Playbook:
        """Load playbook from YAML file."""
        if not path.exists():
            raise FileNotFoundError(f"Playbook not found: {path}")
        
        content = path.read_text()
        playbook = Playbook.from_yaml(content)
        self._playbooks[playbook.name] = playbook
        
        logger.info(f"Loaded playbook: {playbook.name}")
        return playbook
    
    def load_playbooks_directory(self, directory: Optional[Path] = None) -> int:
        """Load all playbooks from directory."""
        if directory is None:
            directory = self._settings.playbooks_path
        
        if not directory.exists():
            return 0
        
        count = 0
        for yaml_file in directory.glob("*.yaml"):
            try:
                self.load_playbook(yaml_file)
                count += 1
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")
        
        for yml_file in directory.glob("*.yml"):
            try:
                self.load_playbook(yml_file)
                count += 1
            except Exception as e:
                logger.error(f"Failed to load {yml_file}: {e}")
        
        return count
    
    def list_playbooks(self) -> List[Dict[str, Any]]:
        """List all loaded playbooks."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "version": p.version,
                "author": p.author,
                "triggers": p.triggers,
                "enabled": p.enabled,
                "action_count": len(p.actions),
                "tags": p.tags,
            }
            for p in self._playbooks.values()
        ]
    
    def get_playbook(self, name: str) -> Optional[Playbook]:
        """Get playbook by name."""
        return self._playbooks.get(name)
    
    def execute(
        self,
        playbook_name: str,
        context: Dict[str, Any],
        dry_run: Optional[bool] = None,
        require_confirmation: bool = True,
    ) -> ExecutionResult:
        """
        Execute a playbook.
        
        Args:
            playbook_name: Name of playbook to execute
            context: Variables for action templates
            dry_run: If True, simulate without making changes
                    (defaults to settings.ir.dry_run_default)
            require_confirmation: If True and not dry_run, log warning
        
        Returns:
            ExecutionResult with action outcomes
        """
        playbook = self._playbooks.get(playbook_name)
        if not playbook:
            return ExecutionResult(
                playbook_name=playbook_name,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                dry_run=True,
                success=False,
                actions_executed=0,
                actions_failed=1,
                error_message=f"Playbook not found: {playbook_name}",
            )
        
        if not playbook.enabled:
            return ExecutionResult(
                playbook_name=playbook_name,
                started_at=datetime.now(),
                completed_at=datetime.now(),
                dry_run=True,
                success=False,
                actions_executed=0,
                actions_failed=0,
                error_message="Playbook is disabled",
            )
        
        # Default to dry_run from settings
        if dry_run is None:
            dry_run = self._settings.ir.dry_run_default
        
        # Warning for live execution
        if not dry_run and require_confirmation:
            logger.warning(
                f"LIVE EXECUTION of playbook '{playbook_name}' - "
                "actions will make real changes!"
            )
        
        started_at = datetime.now()
        action_results = []
        actions_executed = 0
        actions_failed = 0
        
        logger.info(f"{'[DRY-RUN] ' if dry_run else ''}Executing playbook: {playbook_name}")
        
        for action in playbook.actions:
            # Evaluate condition if present
            if action.condition:
                if not self._evaluate_condition(action.condition, context):
                    action_results.append({
                        "action": action.name,
                        "skipped": True,
                        "reason": f"Condition not met: {action.condition}",
                    })
                    continue
            
            # Find handler
            handler = next(
                (h for h in self.HANDLERS if h.can_handle(action)),
                None
            )
            
            if not handler:
                result = {
                    "action": action.name,
                    "success": False,
                    "error": f"No handler for action type: {action.action_type}",
                }
                actions_failed += 1
            else:
                try:
                    result = handler.execute(action, context, dry_run)
                    result["action"] = action.name
                    result["type"] = action.action_type.value
                    
                    if result.get("success", False):
                        actions_executed += 1
                    else:
                        actions_failed += 1
                        
                except Exception as e:
                    result = {
                        "action": action.name,
                        "success": False,
                        "error": str(e),
                    }
                    actions_failed += 1
            
            action_results.append(result)
            
            # Record in database
            status = ActionStatus.DRY_RUN if dry_run else (
                ActionStatus.EXECUTED if result.get("success") else ActionStatus.FAILED
            )
            self._db.insert_action(
                playbook=playbook_name,
                action_name=action.name,
                target=action.target,
                status=status,
                details=result,
            )
            
            # Stop on failure unless continue_on_error
            if not result.get("success") and not action.continue_on_error and not dry_run:
                break
        
        completed_at = datetime.now()
        
        return ExecutionResult(
            playbook_name=playbook_name,
            started_at=started_at,
            completed_at=completed_at,
            dry_run=dry_run,
            success=actions_failed == 0,
            actions_executed=actions_executed,
            actions_failed=actions_failed,
            action_results=action_results,
        )
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Evaluate simple condition expression."""
        # Simple variable presence check
        if condition.startswith("exists:"):
            var_name = condition.split(":", 1)[1].strip()
            return var_name in context and context[var_name]
        
        # Simple comparison
        match = re.match(r"(\w+)\s*(>|<|>=|<=|==|!=)\s*(\d+)", condition)
        if match:
            var_name, op, value = match.groups()
            var_value = context.get(var_name, 0)
            try:
                var_value = float(var_value)
                value = float(value)
                
                ops = {
                    ">": lambda a, b: a > b,
                    "<": lambda a, b: a < b,
                    ">=": lambda a, b: a >= b,
                    "<=": lambda a, b: a <= b,
                    "==": lambda a, b: a == b,
                    "!=": lambda a, b: a != b,
                }
                return ops[op](var_value, value)
            except:
                return False
        
        # Boolean check
        if condition in context:
            return bool(context[condition])
        
        return True  # Default to true for unknown conditions
    
    def create_playbook(
        self,
        name: str,
        description: str,
        actions: List[Dict[str, Any]],
        triggers: Optional[List[str]] = None,
        output_path: Optional[Path] = None,
    ) -> Playbook:
        """
        Create a new playbook.
        
        Args:
            name: Playbook name
            description: Playbook description
            actions: List of action definitions
            triggers: Event triggers
            output_path: Path to save YAML file
        
        Returns:
            Created Playbook
        """
        playbook_actions = []
        for action_data in actions:
            action_type = ActionType(action_data.get("type", "custom"))
            playbook_actions.append(PlaybookAction(
                name=action_data.get("name", "Unnamed"),
                action_type=action_type,
                description=action_data.get("description", ""),
                target=action_data.get("target", ""),
                params=action_data.get("params", {}),
                condition=action_data.get("condition"),
                continue_on_error=action_data.get("continue_on_error", False),
            ))
        
        playbook = Playbook(
            name=name,
            description=description,
            version="1.0.0",
            author="CHRONOS User",
            triggers=triggers or [],
            actions=playbook_actions,
        )
        
        self._playbooks[name] = playbook
        
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(playbook.to_yaml())
            logger.info(f"Saved playbook to {output_path}")
        
        return playbook
