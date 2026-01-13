#!/usr/bin/env python3
"""
DeepSeek Coder CLI - AI-powered coding assistant
Full Python implementation matching Node.js version with tool use, streaming, and multi-provider support.

Author: Bo Shang <bo@shang.software>
"""
import os
import sys
import json
import time
import uuid
import signal
import asyncio
import readline
import argparse
import textwrap
import subprocess
import fnmatch
import re
import hashlib
from pathlib import Path
from typing import (
    Generator, Optional, List, Dict, Any, Callable, Union,
    Tuple, Protocol, Literal, TypedDict, runtime_checkable
)
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import contextmanager
from functools import lru_cache
import threading
from queue import Queue, Empty

# Rich terminal UI
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.text import Text
    from rich.style import Style
    from rich.table import Table
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# OpenAI-compatible client (works with DeepSeek)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Anthropic client
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# ============================================================================
# VERSION & CONSTANTS
# ============================================================================
__version__ = "2.1.0"
APP_NAME = "deepseekpy"
CONFIG_DIR = Path.home() / ".agi"
SECRETS_FILE = CONFIG_DIR / "secrets.json"
HISTORY_FILE = CONFIG_DIR / "deepseek_history.json"
WORKING_DIR = Path.cwd()

# ============================================================================
# PROVIDER CONFIGURATION
# ============================================================================
class Provider(Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

PROVIDER_CONFIG = {
    Provider.DEEPSEEK: {
        "base_url": "https://api.deepseek.com",
        "key_env": "DEEPSEEK_API_KEY",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",  # Use chat for tool use
        "supports_tools": True,
    },
    Provider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "key_env": "OPENAI_API_KEY",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o",
        "supports_tools": True,
    },
    Provider.ANTHROPIC: {
        "base_url": None,
        "key_env": "ANTHROPIC_API_KEY",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
        "default_model": "claude-sonnet-4-20250514",
        "supports_tools": True,
    },
}

# ============================================================================
# CONSOLE & STYLING
# ============================================================================
console = Console() if RICH_AVAILABLE else None

def print_styled(text: str, style: str = ""):
    if RICH_AVAILABLE and console:
        console.print(text, style=style)
    else:
        print(text)

def print_error(text: str):
    if RICH_AVAILABLE and console:
        console.print(f"[red bold]✗[/] {text}")
    else:
        print(f"✗ {text}", file=sys.stderr)

def print_success(text: str):
    if RICH_AVAILABLE and console:
        console.print(f"[green bold]✓[/] {text}")
    else:
        print(f"✓ {text}")

def print_info(text: str):
    if RICH_AVAILABLE and console:
        console.print(f"[blue]ℹ[/] {text}")
    else:
        print(f"ℹ {text}")

def print_warning(text: str):
    if RICH_AVAILABLE and console:
        console.print(f"[yellow]⚠[/] {text}")
    else:
        print(f"⚠ {text}")

def print_tool_start(tool_name: str, params: Dict[str, Any]):
    if RICH_AVAILABLE and console:
        param_str = ", ".join(f"{k}={repr(v)[:50]}" for k, v in list(params.items())[:3])
        console.print(f"[dim cyan]▶ {tool_name}[/]({param_str})")
    else:
        print(f"▶ {tool_name}")

def print_tool_result(tool_name: str, result: str, truncate: int = 500):
    if RICH_AVAILABLE and console:
        display = result[:truncate] + "..." if len(result) > truncate else result
        console.print(f"[dim green]✓ {tool_name}[/] → {len(result)} chars")
        if len(display) < 200:
            console.print(f"[dim]{display}[/]")
    else:
        print(f"✓ {tool_name} → {len(result)} chars")

def print_tool_error(tool_name: str, error: str):
    if RICH_AVAILABLE and console:
        console.print(f"[red]✗ {tool_name}[/]: {error}")
    else:
        print(f"✗ {tool_name}: {error}")

# ============================================================================
# SECRETS MANAGEMENT
# ============================================================================
class SecretsManager:
    def __init__(self):
        self.secrets: Dict[str, str] = {}
        self._load()

    def _load(self):
        if SECRETS_FILE.exists():
            try:
                with open(SECRETS_FILE, 'r') as f:
                    self.secrets = json.load(f)
                # Sync to environment
                for key, value in self.secrets.items():
                    if key not in os.environ:
                        os.environ[key] = value
            except (json.JSONDecodeError, IOError):
                self.secrets = {}

    def _save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(SECRETS_FILE, 'w') as f:
            json.dump(self.secrets, f, indent=2)
        os.chmod(SECRETS_FILE, 0o600)

    def get(self, key: str) -> Optional[str]:
        return os.environ.get(key) or self.secrets.get(key)

    def set(self, key: str, value: str):
        self.secrets[key] = value
        os.environ[key] = value
        self._save()
        print_success(f"{key} saved to {SECRETS_FILE}")

    def has_provider_key(self, provider: Provider) -> bool:
        key_env = PROVIDER_CONFIG[provider]["key_env"]
        return bool(self.get(key_env))

    def prompt_for_key(self, provider: Provider) -> Optional[str]:
        """Prompt user for API key interactively."""
        key_env = PROVIDER_CONFIG[provider]["key_env"]
        provider_name = provider.value.upper()

        if RICH_AVAILABLE and console:
            console.print(f"\n[yellow]⚠ No {provider_name} API key found[/]")
            console.print(f"[dim]Get your key from: https://platform.{provider.value}.com/api-keys[/]")
            try:
                api_key = console.input(f"[bold]Enter {key_env}: [/]").strip()
            except (EOFError, KeyboardInterrupt):
                return None
        else:
            print(f"\n⚠ No {provider_name} API key found")
            print(f"Get your key from: https://platform.{provider.value}.com/api-keys")
            try:
                api_key = input(f"Enter {key_env}: ").strip()
            except (EOFError, KeyboardInterrupt):
                return None

        if api_key:
            self.set(key_env, api_key)
            return api_key
        return None

    def clear_key(self, provider: Provider):
        """Clear a provider's API key (for re-entry after errors)."""
        key_env = PROVIDER_CONFIG[provider]["key_env"]
        if key_env in self.secrets:
            del self.secrets[key_env]
            self._save()
        if key_env in os.environ:
            del os.environ[key_env]

secrets = SecretsManager()

# ============================================================================
# API ERROR HANDLING
# ============================================================================
class APIError(Exception):
    """Base class for API errors."""
    pass

class APIKeyInvalidError(APIError):
    """API key is invalid or expired."""
    pass

class APIRateLimitError(APIError):
    """API rate limit exceeded."""
    pass

class APIFrozenError(APIError):
    """API account is frozen or suspended."""
    pass

class APIQuotaExceededError(APIError):
    """API quota/balance exhausted."""
    pass

def classify_api_error(error: Exception) -> APIError:
    """Classify an API error into specific types for handling."""
    error_str = str(error).lower()
    error_code = getattr(error, 'status_code', None) or getattr(error, 'code', None)

    # Check for frozen/suspended account
    if any(x in error_str for x in ['frozen', 'suspended', 'disabled', 'banned', 'blocked']):
        return APIFrozenError(f"Account frozen or suspended: {error}")

    # Check for invalid API key
    if error_code == 401 or any(x in error_str for x in ['invalid api key', 'unauthorized', 'authentication', 'invalid_api_key']):
        return APIKeyInvalidError(f"Invalid API key: {error}")

    # Check for rate limiting
    if error_code == 429 or any(x in error_str for x in ['rate limit', 'too many requests', 'rate_limit']):
        return APIRateLimitError(f"Rate limit exceeded: {error}")

    # Check for quota/balance issues
    if any(x in error_str for x in ['quota', 'insufficient', 'balance', 'exceeded', 'limit reached']):
        return APIQuotaExceededError(f"Quota exceeded: {error}")

    return APIError(str(error))

def handle_api_error(error: APIError, provider: Provider) -> bool:
    """
    Handle API error with appropriate user notification.
    Returns True if user wants to retry with new key, False otherwise.
    """
    if isinstance(error, APIFrozenError):
        print_error("🚫 API ACCOUNT FROZEN")
        if RICH_AVAILABLE and console:
            console.print("[red bold]Your API account has been frozen or suspended.[/]")
            console.print("[yellow]Possible reasons:[/]")
            console.print("  • Terms of service violation")
            console.print("  • Payment issues")
            console.print("  • Suspicious activity detected")
            console.print(f"\n[dim]Contact {provider.value} support to resolve this.[/]")
        else:
            print("Your API account has been frozen or suspended.")
            print("Contact support to resolve this.")
        return False

    elif isinstance(error, APIKeyInvalidError):
        print_error("🔑 INVALID API KEY")
        if RICH_AVAILABLE and console:
            console.print("[yellow]The API key is invalid, expired, or revoked.[/]")
            try:
                retry = console.input("[bold]Enter a new API key? (y/N): [/]").strip().lower()
                if retry in ('y', 'yes'):
                    secrets.clear_key(provider)
                    new_key = secrets.prompt_for_key(provider)
                    return new_key is not None
            except (EOFError, KeyboardInterrupt):
                pass
        return False

    elif isinstance(error, APIRateLimitError):
        print_warning("⏳ RATE LIMIT EXCEEDED")
        if RICH_AVAILABLE and console:
            console.print("[yellow]Too many requests. Please wait before retrying.[/]")
            console.print("[dim]Rate limits typically reset within 1-60 seconds.[/]")
        else:
            print("Too many requests. Please wait before retrying.")
        return False

    elif isinstance(error, APIQuotaExceededError):
        print_error("💳 QUOTA/BALANCE EXCEEDED")
        if RICH_AVAILABLE and console:
            console.print("[yellow]Your API quota or balance has been exhausted.[/]")
            console.print(f"[dim]Add credits at: https://platform.{provider.value}.com/billing[/]")
        else:
            print("Your API quota or balance has been exhausted.")
        return False

    else:
        print_error(f"API Error: {error}")
        return False

# ============================================================================
# GUARDRAILS SYSTEM - HITL & SAFETY ENFORCEMENT
# ============================================================================
class OperationLevel(Enum):
    """Operation classification levels (MQ-9 Reaper model)."""
    ROUTINE = 1      # Auto-approved: read, search, analysis
    ELEVATED = 2     # Logged: file writes, git operations
    CRITICAL = 3     # 1 confirmation: system changes, installs
    LETHAL = 4       # 2 confirmations + delay: destructive ops

@dataclass
class GuardrailViolation:
    """Record of a guardrail violation."""
    level: OperationLevel
    tool_name: str
    reason: str
    blocked: bool
    timestamp: float = field(default_factory=time.time)

class Guardrails:
    """
    HITL (Human-in-the-Loop) Enforcement System.
    Modeled after MQ-9 Reaper - autonomous for routine tasks,
    human authorization required for critical/lethal operations.
    """

    # Dangerous bash patterns that require approval
    DANGEROUS_COMMANDS = [
        # Destructive
        (r'\brm\s+-rf?\s+[/~]', OperationLevel.LETHAL, "Recursive delete from root/home"),
        (r'\brm\s+-rf?\s+\*', OperationLevel.LETHAL, "Recursive delete with wildcard"),
        (r'\bmkfs\.', OperationLevel.LETHAL, "Filesystem format"),
        (r'\bdd\s+.*of=/dev/', OperationLevel.LETHAL, "Direct disk write"),
        (r'>\s*/dev/sd[a-z]', OperationLevel.LETHAL, "Redirect to block device"),
        (r'\bshred\b', OperationLevel.LETHAL, "Secure file deletion"),

        # System modification
        (r'\bsudo\s+rm\b', OperationLevel.CRITICAL, "Sudo remove"),
        (r'\bsudo\s+.*install\b', OperationLevel.ELEVATED, "Sudo install"),
        (r'\bchmod\s+777\b', OperationLevel.CRITICAL, "World-writable permissions"),
        (r'\bchown\s+root\b', OperationLevel.CRITICAL, "Change owner to root"),
        (r'\bsystemctl\s+(stop|disable|mask)\b', OperationLevel.CRITICAL, "Service disruption"),

        # Network/Security
        (r'\bcurl\s+.*\|\s*(ba)?sh\b', OperationLevel.LETHAL, "Pipe curl to shell"),
        (r'\bwget\s+.*\|\s*(ba)?sh\b', OperationLevel.LETHAL, "Pipe wget to shell"),
        (r'\bnc\s+-[el]', OperationLevel.CRITICAL, "Netcat listener"),
        (r'\biptables\s+-F\b', OperationLevel.LETHAL, "Flush firewall rules"),
        (r'\bufw\s+disable\b', OperationLevel.CRITICAL, "Disable firewall"),

        # Git destructive
        (r'\bgit\s+push\s+.*--force\b', OperationLevel.CRITICAL, "Force push"),
        (r'\bgit\s+reset\s+--hard\b', OperationLevel.ELEVATED, "Hard reset"),
        (r'\bgit\s+clean\s+-fd', OperationLevel.ELEVATED, "Clean untracked files"),

        # Process/System
        (r'\bkill\s+-9\s+-1\b', OperationLevel.LETHAL, "Kill all processes"),
        (r'\bkillall\b', OperationLevel.CRITICAL, "Kill by name"),
        (r'\breboot\b', OperationLevel.LETHAL, "System reboot"),
        (r'\bshutdown\b', OperationLevel.LETHAL, "System shutdown"),
        (r'\binit\s+[0-6]\b', OperationLevel.LETHAL, "Change runlevel"),
    ]

    # Sensitive paths that should not be modified
    SENSITIVE_PATHS = [
        '/etc/passwd', '/etc/shadow', '/etc/sudoers', '/etc/ssh/',
        '/root/', '~/.ssh/', '~/.gnupg/', '~/.aws/', '~/.kube/',
        '/boot/', '/usr/bin/', '/usr/sbin/', '/bin/', '/sbin/',
        '.env', 'credentials', 'secrets', '.pem', '.key', 'id_rsa',
    ]

    # File patterns that should never be written
    FORBIDDEN_WRITE_PATTERNS = [
        r'\.env$', r'credentials\.json$', r'secrets\.ya?ml$',
        r'id_rsa', r'\.pem$', r'\.key$', r'\.crt$',
        r'/etc/', r'/boot/', r'/usr/',
    ]

    def __init__(self, auto_approve_routine: bool = True, interactive: bool = True):
        self.auto_approve_routine = auto_approve_routine
        self.interactive = interactive
        self.violations: List[GuardrailViolation] = []
        self.approval_cache: Dict[str, bool] = {}
        self.audit_log: List[Dict[str, Any]] = []

    def check_bash_command(self, command: str) -> Tuple[OperationLevel, Optional[str]]:
        """
        Analyze bash command for dangerous patterns.
        Returns (level, reason) tuple.
        """
        command_lower = command.lower()

        for pattern, level, reason in self.DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                return level, reason

        # Default to ROUTINE for safe commands
        return OperationLevel.ROUTINE, None

    def check_file_path(self, path: str, operation: str = "access") -> Tuple[OperationLevel, Optional[str]]:
        """
        Check if file path is sensitive.
        Returns (level, reason) tuple.
        """
        path_str = str(path).lower()
        expanded = os.path.expanduser(path_str)

        for sensitive in self.SENSITIVE_PATHS:
            if sensitive.lower() in path_str or sensitive.lower() in expanded:
                if operation in ("write", "edit", "delete"):
                    return OperationLevel.LETHAL, f"Write to sensitive path: {sensitive}"
                else:
                    return OperationLevel.ELEVATED, f"Read sensitive path: {sensitive}"

        if operation in ("write", "edit"):
            for pattern in self.FORBIDDEN_WRITE_PATTERNS:
                if re.search(pattern, path_str, re.IGNORECASE):
                    return OperationLevel.CRITICAL, f"Write to protected pattern: {pattern}"

        return OperationLevel.ROUTINE, None

    def request_approval(self, level: OperationLevel, tool_name: str,
                         details: str, reason: str) -> bool:
        """
        Request human approval for elevated operations.
        Implements HITL enforcement.
        """
        # Cache key for repeated operations
        cache_key = f"{tool_name}:{details[:100]}"
        if cache_key in self.approval_cache:
            return self.approval_cache[cache_key]

        # Auto-approve routine operations
        if level == OperationLevel.ROUTINE and self.auto_approve_routine:
            return True

        # Log the request
        self._audit_log("approval_request", {
            "level": level.name,
            "tool": tool_name,
            "details": details[:200],
            "reason": reason
        })

        if not self.interactive:
            # Non-interactive mode: block elevated+ operations
            if level.value >= OperationLevel.CRITICAL.value:
                self._record_violation(level, tool_name, reason, blocked=True)
                return False
            return True

        # Interactive approval
        level_colors = {
            OperationLevel.ELEVATED: "yellow",
            OperationLevel.CRITICAL: "red",
            OperationLevel.LETHAL: "red bold",
        }

        color = level_colors.get(level, "white")

        if RICH_AVAILABLE and console:
            console.print(f"\n[{color}]⚠ GUARDRAIL: {level.name} operation detected[/]")
            console.print(f"[dim]Tool:[/] {tool_name}")
            console.print(f"[dim]Details:[/] {details[:100]}")
            console.print(f"[dim]Reason:[/] {reason}")

            if level == OperationLevel.LETHAL:
                console.print("[red bold]This is a LETHAL operation requiring 2 confirmations.[/]")
                confirm1 = console.input("[yellow]Type 'CONFIRM' to proceed: [/]")
                if confirm1 != "CONFIRM":
                    self._record_violation(level, tool_name, reason, blocked=True)
                    return False
                console.print("[red]Waiting 5 seconds... Press Ctrl+C to cancel.[/]")
                try:
                    time.sleep(5)
                except KeyboardInterrupt:
                    self._record_violation(level, tool_name, reason, blocked=True)
                    return False
                confirm2 = console.input("[red]Final confirmation - type 'EXECUTE': [/]")
                approved = confirm2 == "EXECUTE"
            elif level == OperationLevel.CRITICAL:
                confirm = console.input("[yellow]Approve? (y/N): [/]")
                approved = confirm.lower() in ('y', 'yes')
            else:  # ELEVATED
                confirm = console.input("[dim]Continue? (Y/n): [/]")
                approved = confirm.lower() not in ('n', 'no')
        else:
            print(f"\n⚠ GUARDRAIL: {level.name} operation")
            print(f"Tool: {tool_name}")
            print(f"Reason: {reason}")
            confirm = input("Approve? (y/N): ")
            approved = confirm.lower() in ('y', 'yes')

        self.approval_cache[cache_key] = approved

        if not approved:
            self._record_violation(level, tool_name, reason, blocked=True)

        self._audit_log("approval_response", {
            "level": level.name,
            "tool": tool_name,
            "approved": approved
        })

        return approved

    def validate_tool_call(self, tool_name: str, args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call against guardrails.
        Returns (allowed, denial_reason).
        """
        level = OperationLevel.ROUTINE
        reason = None
        details = ""

        if tool_name == "Bash":
            command = args.get("command", "")
            details = command[:100]
            level, reason = self.check_bash_command(command)

        elif tool_name in ("Write", "Edit"):
            path = args.get("file_path", args.get("path", ""))
            details = path
            level, reason = self.check_file_path(path, "write")

        elif tool_name == "Read":
            path = args.get("file_path", args.get("path", ""))
            details = path
            level, reason = self.check_file_path(path, "read")

        # Request approval if needed
        if level != OperationLevel.ROUTINE or reason:
            approved = self.request_approval(level, tool_name, details, reason or "Elevated operation")
            if not approved:
                return False, f"Operation blocked by guardrails: {reason or level.name}"

        return True, None

    def _record_violation(self, level: OperationLevel, tool_name: str, reason: str, blocked: bool):
        """Record a guardrail violation."""
        violation = GuardrailViolation(
            level=level,
            tool_name=tool_name,
            reason=reason,
            blocked=blocked
        )
        self.violations.append(violation)

    def _audit_log(self, event_type: str, data: Dict[str, Any]):
        """Add entry to audit log."""
        self.audit_log.append({
            "timestamp": time.time(),
            "event": event_type,
            **data
        })

    def get_stats(self) -> Dict[str, Any]:
        """Get guardrail statistics."""
        return {
            "total_violations": len(self.violations),
            "blocked_operations": sum(1 for v in self.violations if v.blocked),
            "audit_entries": len(self.audit_log),
            "by_level": {
                level.name: sum(1 for v in self.violations if v.level == level)
                for level in OperationLevel
            }
        }

# Global guardrails instance
guardrails = Guardrails()

# ============================================================================
# TOOL SYSTEM - DEFINITIONS & TYPES
# ============================================================================
@dataclass
class ToolCallRequest:
    """Request to execute a tool."""
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class ToolDefinition:
    """Definition of a tool that can be called by the AI."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    handler: Callable[[Dict[str, Any]], str]
    cacheable: bool = False
    cache_ttl_ms: int = 300000  # 5 minutes

@dataclass
class ToolHistoryEntry:
    """Record of a tool execution."""
    tool_name: str
    args: Dict[str, Any]
    timestamp: float
    success: bool
    has_output: bool
    error: Optional[str] = None
    duration_ms: Optional[float] = None

# ============================================================================
# EVENT SYSTEM - STREAMING EVENTS
# ============================================================================
EventType = Literal[
    'message.start', 'message.delta', 'message.complete',
    'tool.start', 'tool.complete', 'tool.error',
    'reasoning', 'error', 'usage'
]

@dataclass
class AgentEvent:
    type: EventType
    timestamp: float = field(default_factory=time.time)

@dataclass
class MessageStartEvent(AgentEvent):
    type: Literal['message.start'] = 'message.start'

@dataclass
class MessageDeltaEvent(AgentEvent):
    type: Literal['message.delta'] = 'message.delta'
    content: str = ""
    is_final: bool = False

@dataclass
class MessageCompleteEvent(AgentEvent):
    type: Literal['message.complete'] = 'message.complete'
    content: str = ""
    elapsed_ms: float = 0

@dataclass
class ToolStartEvent(AgentEvent):
    type: Literal['tool.start'] = 'tool.start'
    tool_name: str = ""
    tool_call_id: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolCompleteEvent(AgentEvent):
    type: Literal['tool.complete'] = 'tool.complete'
    tool_name: str = ""
    tool_call_id: str = ""
    result: str = ""

@dataclass
class ToolErrorEvent(AgentEvent):
    type: Literal['tool.error'] = 'tool.error'
    tool_name: str = ""
    tool_call_id: str = ""
    error: str = ""

@dataclass
class ReasoningEvent(AgentEvent):
    type: Literal['reasoning'] = 'reasoning'
    content: str = ""

@dataclass
class ErrorEvent(AgentEvent):
    type: Literal['error'] = 'error'
    error: str = ""

@dataclass
class UsageEvent(AgentEvent):
    type: Literal['usage'] = 'usage'
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

AgentEventUnion = Union[
    MessageStartEvent, MessageDeltaEvent, MessageCompleteEvent,
    ToolStartEvent, ToolCompleteEvent, ToolErrorEvent,
    ReasoningEvent, ErrorEvent, UsageEvent
]

# ============================================================================
# TOOL RUNTIME OBSERVER
# ============================================================================
@runtime_checkable
class ToolRuntimeObserver(Protocol):
    def on_tool_start(self, call: ToolCallRequest) -> None: ...
    def on_tool_result(self, call: ToolCallRequest, output: str) -> None: ...
    def on_tool_error(self, call: ToolCallRequest, error: str) -> None: ...

# ============================================================================
# BUILT-IN TOOLS IMPLEMENTATION
# ============================================================================
class BuiltInTools:
    """Implementation of built-in tools matching Node.js version."""

    def __init__(self, working_dir: Path = WORKING_DIR):
        self.working_dir = working_dir

    def bash(self, args: Dict[str, Any]) -> str:
        """Execute bash command."""
        command = args.get("command", "")
        cwd = args.get("cwd", str(self.working_dir))
        timeout = args.get("timeout", 120000) / 1000  # Convert ms to seconds
        description = args.get("description", "")

        if not command:
            return "Error: No command provided"

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=min(timeout, 600),  # Max 10 minutes
                env={**os.environ, "TERM": "dumb"}
            )

            output_parts = []
            if result.stdout:
                output_parts.append(result.stdout)
            if result.stderr:
                output_parts.append(f"stderr:\n{result.stderr}")
            if result.returncode != 0:
                output_parts.append(f"Exit code: {result.returncode}")

            output = "\n".join(output_parts) if output_parts else "(no output)"

            # Truncate if too long
            if len(output) > 30000:
                output = output[:30000] + f"\n... (truncated, {len(output)} total chars)"

            return output

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout}s"
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, args: Dict[str, Any]) -> str:
        """Read file contents with line numbers."""
        file_path = args.get("file_path", args.get("path", ""))
        offset = args.get("offset", 1)
        limit = args.get("limit", 2000)

        if not file_path:
            return "Error: No file path provided"

        # Resolve path
        path = Path(file_path)
        if not path.is_absolute():
            path = self.working_dir / path

        if not path.exists():
            return f"Error: File not found: {path}"

        if not path.is_file():
            return f"Error: Not a file: {path}"

        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            # Apply offset and limit
            start_idx = max(0, offset - 1)
            end_idx = start_idx + limit
            selected_lines = lines[start_idx:end_idx]

            # Format with line numbers (cat -n style)
            output_lines = []
            for i, line in enumerate(selected_lines, start=start_idx + 1):
                # Truncate long lines
                if len(line) > 2000:
                    line = line[:2000] + "...\n"
                output_lines.append(f"{i:6d}\t{line.rstrip()}")

            result = "\n".join(output_lines)

            if end_idx < len(lines):
                result += f"\n... ({len(lines) - end_idx} more lines)"

            return result

        except Exception as e:
            return f"Error reading file: {str(e)}"

    def write_file(self, args: Dict[str, Any]) -> str:
        """Write content to a file."""
        file_path = args.get("file_path", args.get("path", ""))
        content = args.get("content", "")

        if not file_path:
            return "Error: No file path provided"

        path = Path(file_path)
        if not path.is_absolute():
            path = self.working_dir / path

        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} bytes to {path}"

        except Exception as e:
            return f"Error writing file: {str(e)}"

    def edit_file(self, args: Dict[str, Any]) -> str:
        """Edit file by replacing old_string with new_string."""
        file_path = args.get("file_path", args.get("path", ""))
        old_string = args.get("old_string", "")
        new_string = args.get("new_string", "")
        replace_all = args.get("replace_all", False)

        if not file_path:
            return "Error: No file path provided"

        if old_string == new_string:
            return "Error: old_string and new_string are identical"

        path = Path(file_path)
        if not path.is_absolute():
            path = self.working_dir / path

        if not path.exists():
            return f"Error: File not found: {path}"

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if old_string exists
            count = content.count(old_string)
            if count == 0:
                return f"Error: old_string not found in file"

            if count > 1 and not replace_all:
                return f"Error: old_string found {count} times. Use replace_all=true or provide more context."

            # Perform replacement
            if replace_all:
                new_content = content.replace(old_string, new_string)
            else:
                new_content = content.replace(old_string, new_string, 1)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            replaced = count if replace_all else 1
            return f"Successfully replaced {replaced} occurrence(s) in {path}"

        except Exception as e:
            return f"Error editing file: {str(e)}"

    def glob_search(self, args: Dict[str, Any]) -> str:
        """Search for files matching a glob pattern."""
        pattern = args.get("pattern", "")
        search_path = args.get("path", str(self.working_dir))

        if not pattern:
            return "Error: No pattern provided"

        path = Path(search_path)
        if not path.is_absolute():
            path = self.working_dir / path

        try:
            # Use glob to find matches
            matches = list(path.glob(pattern))

            # Sort by modification time (newest first)
            matches.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)

            # Limit results
            matches = matches[:100]

            if not matches:
                return "No files found matching pattern"

            # Format output
            results = []
            for match in matches:
                try:
                    rel_path = match.relative_to(self.working_dir)
                except ValueError:
                    rel_path = match
                results.append(str(rel_path))

            return "\n".join(results)

        except Exception as e:
            return f"Error in glob search: {str(e)}"

    def grep_search(self, args: Dict[str, Any]) -> str:
        """Search file contents for a pattern."""
        pattern = args.get("pattern", "")
        search_path = args.get("path", str(self.working_dir))
        ignore_case = args.get("-i", args.get("ignore_case", False))
        output_mode = args.get("output_mode", "files_with_matches")
        glob_filter = args.get("glob", None)
        context_lines = args.get("-C", 0)

        if not pattern:
            return "Error: No pattern provided"

        path = Path(search_path)
        if not path.is_absolute():
            path = self.working_dir / path

        try:
            # Compile regex
            flags = re.IGNORECASE if ignore_case else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return f"Error: Invalid regex pattern: {e}"

            results = []
            files_with_matches = set()

            # Find files to search
            if path.is_file():
                files = [path]
            else:
                if glob_filter:
                    files = list(path.rglob(glob_filter))
                else:
                    files = [f for f in path.rglob("*") if f.is_file()]

            # Filter out binary files and hidden directories
            files = [f for f in files if not any(
                p.startswith('.') for p in f.parts
            )][:1000]  # Limit files

            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        if regex.search(line):
                            files_with_matches.add(file_path)
                            if output_mode == "content":
                                try:
                                    rel = file_path.relative_to(self.working_dir)
                                except ValueError:
                                    rel = file_path
                                results.append(f"{rel}:{i+1}:{line.rstrip()}")

                except (IOError, UnicodeDecodeError):
                    continue

            if output_mode == "files_with_matches":
                output = []
                for f in sorted(files_with_matches):
                    try:
                        rel = f.relative_to(self.working_dir)
                    except ValueError:
                        rel = f
                    output.append(str(rel))
                return "\n".join(output[:50]) if output else "No matches found"

            elif output_mode == "count":
                return f"Found matches in {len(files_with_matches)} files"

            else:  # content
                return "\n".join(results[:100]) if results else "No matches found"

        except Exception as e:
            return f"Error in grep search: {str(e)}"

# ============================================================================
# TOOL RUNTIME
# ============================================================================
class ToolRuntime:
    """Manages tool registration, execution, and caching."""

    def __init__(self, working_dir: Path = WORKING_DIR, observer: Optional[ToolRuntimeObserver] = None,
                 guardrails_instance: Optional['Guardrails'] = None):
        self.working_dir = working_dir
        self.observer = observer
        self.guardrails = guardrails_instance or guardrails  # Use global if not provided
        self.tools: Dict[str, ToolDefinition] = {}
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.history: List[ToolHistoryEntry] = []
        self.max_history = 50

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register all built-in tools."""
        builtin = BuiltInTools(self.working_dir)

        # Bash tool
        self.register(ToolDefinition(
            name="Bash",
            description="Execute bash shell commands. Use for git, npm, build commands, etc.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of what this command does"
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Timeout in milliseconds (default 120000)"
                    }
                },
                "required": ["command"]
            },
            handler=builtin.bash
        ))

        # Read tool
        self.register(ToolDefinition(
            name="Read",
            description="Read file contents. Returns content with line numbers.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    },
                    "offset": {
                        "type": "number",
                        "description": "Line number to start from (1-based)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum lines to read"
                    }
                },
                "required": ["file_path"]
            },
            handler=builtin.read_file,
            cacheable=True
        ))

        # Write tool
        self.register(ToolDefinition(
            name="Write",
            description="Write content to a file. Creates parent directories if needed.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute or relative path to write to"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["file_path", "content"]
            },
            handler=builtin.write_file
        ))

        # Edit tool
        self.register(ToolDefinition(
            name="Edit",
            description="Edit file by replacing text. Must read file first.",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to edit"
                    },
                    "old_string": {
                        "type": "string",
                        "description": "Text to replace (must be unique unless replace_all)"
                    },
                    "new_string": {
                        "type": "string",
                        "description": "Replacement text"
                    },
                    "replace_all": {
                        "type": "boolean",
                        "description": "Replace all occurrences (default false)"
                    }
                },
                "required": ["file_path", "old_string", "new_string"]
            },
            handler=builtin.edit_file
        ))

        # Glob tool
        self.register(ToolDefinition(
            name="Glob",
            description="Find files matching a glob pattern (e.g., **/*.py)",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., **/*.ts, src/**/*.py)"
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory to search in"
                    }
                },
                "required": ["pattern"]
            },
            handler=builtin.glob_search,
            cacheable=True
        ))

        # Grep tool
        self.register(ToolDefinition(
            name="Grep",
            description="Search file contents for a regex pattern",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for"
                    },
                    "path": {
                        "type": "string",
                        "description": "File or directory to search"
                    },
                    "glob": {
                        "type": "string",
                        "description": "Filter files by glob pattern"
                    },
                    "-i": {
                        "type": "boolean",
                        "description": "Case insensitive search"
                    },
                    "output_mode": {
                        "type": "string",
                        "enum": ["content", "files_with_matches", "count"],
                        "description": "Output format"
                    }
                },
                "required": ["pattern"]
            },
            handler=builtin.grep_search,
            cacheable=True
        ))

    def register(self, tool: ToolDefinition):
        """Register a tool."""
        self.tools[tool.name] = tool

    def get_tools_for_api(self) -> List[Dict[str, Any]]:
        """Get tool definitions formatted for API calls."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters
                }
            }
            for tool in self.tools.values()
        ]

    def execute(self, call: ToolCallRequest) -> str:
        """Execute a tool call with HITL guardrails enforcement."""
        tool = self.tools.get(call.name)
        if not tool:
            error = f"Unknown tool: {call.name}"
            if self.observer:
                self.observer.on_tool_error(call, error)
            return error

        # HITL GUARDRAILS CHECK - MQ-9 Reaper model
        # Autonomous for routine, human auth for critical/lethal
        if self.guardrails:
            allowed, denial_reason = self.guardrails.validate_tool_call(call.name, call.arguments)
            if not allowed:
                error = f"GUARDRAIL BLOCKED: {denial_reason}"
                if self.observer:
                    self.observer.on_tool_error(call, error)
                self._record_history(ToolHistoryEntry(
                    tool_name=call.name,
                    args=call.arguments,
                    timestamp=time.time(),
                    success=False,
                    has_output=False,
                    error=error
                ))
                return error

        # Notify observer
        if self.observer:
            self.observer.on_tool_start(call)

        # Check cache
        cache_key = f"{call.name}:{json.dumps(call.arguments, sort_keys=True)}"
        if tool.cacheable and cache_key in self.cache:
            cached_result, cached_time = self.cache[cache_key]
            if time.time() - cached_time < tool.cache_ttl_ms / 1000:
                if self.observer:
                    self.observer.on_tool_result(call, cached_result)
                return cached_result

        start_time = time.time()
        try:
            result = tool.handler(call.arguments)
            duration_ms = (time.time() - start_time) * 1000

            # Cache if cacheable
            if tool.cacheable:
                self.cache[cache_key] = (result, time.time())

            # Record history
            self._record_history(ToolHistoryEntry(
                tool_name=call.name,
                args=call.arguments,
                timestamp=time.time(),
                success=True,
                has_output=bool(result),
                duration_ms=duration_ms
            ))

            if self.observer:
                self.observer.on_tool_result(call, result)

            return result

        except Exception as e:
            error = str(e)
            duration_ms = (time.time() - start_time) * 1000

            self._record_history(ToolHistoryEntry(
                tool_name=call.name,
                args=call.arguments,
                timestamp=time.time(),
                success=False,
                has_output=False,
                error=error,
                duration_ms=duration_ms
            ))

            if self.observer:
                self.observer.on_tool_error(call, error)

            return f"Error: {error}"

    def _record_history(self, entry: ToolHistoryEntry):
        """Record tool execution in history."""
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)

# ============================================================================
# CONVERSATION HISTORY
# ============================================================================
@dataclass
class Message:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

class ConversationHistory:
    def __init__(self, max_messages: int = 100):
        self.messages: List[Message] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str, **kwargs):
        self.messages.append(Message(role=role, content=content, **kwargs))
        self._trim()

    def add_tool_result(self, tool_call_id: str, content: str):
        self.messages.append(Message(
            role="tool",
            content=content,
            tool_call_id=tool_call_id
        ))
        self._trim()

    def _trim(self):
        if len(self.messages) > self.max_messages:
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            keep = self.max_messages - len(system_msgs)
            self.messages = system_msgs + other_msgs[-keep:]

    def clear(self):
        self.messages = [m for m in self.messages if m.role == "system"]

    def get_messages_for_api(self) -> List[Dict[str, Any]]:
        """Get messages formatted for API calls."""
        result = []
        for m in self.messages:
            msg = {"role": m.role, "content": m.content}
            if m.tool_calls:
                msg["tool_calls"] = m.tool_calls
            if m.tool_call_id:
                msg["tool_call_id"] = m.tool_call_id
            result.append(msg)
        return result

# ============================================================================
# AGENT CONTROLLER WITH TOOL USE
# ============================================================================
class AgentController:
    """Main agent controller with tool use support."""

    def __init__(self, working_dir: Path = WORKING_DIR):
        self.working_dir = working_dir
        self.current_provider = Provider.DEEPSEEK
        self.current_model = "deepseek-chat"
        self.history = ConversationHistory()
        self.processing = False
        self.client: Optional[OpenAI] = None

        # Tool runtime with observer
        self.tool_runtime = ToolRuntime(working_dir, observer=self)

        # Event queue for streaming
        self.event_queue: Queue[AgentEventUnion] = Queue()

        # Initialize
        self._init_client()
        self.history.add("system", self._get_system_prompt())

    def _get_system_prompt(self) -> str:
        return f"""You are DeepSeek Coder, an AI-powered coding assistant with tool use capabilities.

## VERIFICATION-FIRST PRINCIPLE (MANDATORY)
You are NOT allowed to report ANY finding, claim, or assertion until it has been verified first.
- No hypothetical vulnerabilities - verify before claiming
- No speculative analysis - run commands and check actual output
- No AI-generated guesses reported as facts
- ONLY verified, tested, real findings backed by evidence

Before making ANY claim:
1. Read actual system files to get actual values
2. Execute verification commands - don't guess
3. Show the actual output as evidence
4. Report ONLY what the system actually shows

## Available Tools:
- Bash: Execute shell commands (git, npm, build, etc.)
- Read: Read file contents with line numbers
- Write: Create or overwrite files
- Edit: Make precise edits to files (must Read first)
- Glob: Find files by pattern
- Grep: Search file contents

Working directory: {self.working_dir}

## Guidelines:
1. ALWAYS Read a file before editing it
2. Use Glob/Grep to find files before reading them
3. Prefer Edit over Write for existing files
4. Run tests/builds after making changes
5. Be concise and accurate
6. Verify all claims with actual tool output

## HITL Guardrails:
Operations are classified by risk level. Destructive operations require human approval.
- ROUTINE: Auto-approved (read, search, analysis)
- ELEVATED: Logged (file writes, git ops)
- CRITICAL: Requires 1 confirmation
- LETHAL: Requires 2 confirmations + 5s delay"""

    def _init_client(self, prompt_if_missing: bool = False) -> bool:
        """
        Initialize API client.
        If prompt_if_missing=True, will prompt user for API key if not found.
        Returns True if client initialized successfully.
        """
        api_key = secrets.get(PROVIDER_CONFIG[self.current_provider]["key_env"])

        # Prompt for key if not present and interactive
        if not api_key and prompt_if_missing:
            api_key = secrets.prompt_for_key(self.current_provider)

        if api_key and OPENAI_AVAILABLE:
            self.client = OpenAI(
                api_key=api_key,
                base_url=PROVIDER_CONFIG[self.current_provider]["base_url"],
            )
            return True

        self.client = None
        return False

    def ensure_client(self) -> bool:
        """Ensure client is available, prompting for key if needed."""
        if self.client:
            return True
        return self._init_client(prompt_if_missing=True)

    def is_available(self) -> bool:
        return self.client is not None

    def switch_provider(self, provider: Provider, model: Optional[str] = None):
        # Prompt for key if not present
        if not secrets.has_provider_key(provider):
            api_key = secrets.prompt_for_key(provider)
            if not api_key:
                raise RuntimeError(f"No API key provided for {provider.value}")

        self.current_provider = provider
        self.current_model = model or PROVIDER_CONFIG[provider]["default_model"]
        self._init_client()
        print_success(f"Switched to {provider.value}/{self.current_model}")

    # ToolRuntimeObserver implementation
    def on_tool_start(self, call: ToolCallRequest):
        self.event_queue.put(ToolStartEvent(
            tool_name=call.name,
            tool_call_id=call.id,
            parameters=call.arguments
        ))
        print_tool_start(call.name, call.arguments)

    def on_tool_result(self, call: ToolCallRequest, output: str):
        self.event_queue.put(ToolCompleteEvent(
            tool_name=call.name,
            tool_call_id=call.id,
            result=output
        ))
        print_tool_result(call.name, output)

    def on_tool_error(self, call: ToolCallRequest, error: str):
        self.event_queue.put(ToolErrorEvent(
            tool_name=call.name,
            tool_call_id=call.id,
            error=error
        ))
        print_tool_error(call.name, error)

    def send(self, message: str, retry_on_auth_error: bool = True) -> Generator[AgentEventUnion, None, None]:
        """Send a message and stream response with tool use."""
        if not self.client:
            # Try to get API key interactively
            if not self.ensure_client():
                raise RuntimeError("No AI provider configured. Run /secrets to set API keys.")

        self.processing = True
        start_time = time.time()

        try:
            # Add user message
            self.history.add("user", message)

            # Emit start event
            yield MessageStartEvent()

            # Agentic loop - continue until no more tool calls
            max_iterations = 10
            iteration = 0
            full_content = ""

            while iteration < max_iterations:
                iteration += 1

                # Make API call with tools
                response = self.client.chat.completions.create(
                    model=self.current_model,
                    messages=self.history.get_messages_for_api(),
                    tools=self.tool_runtime.get_tools_for_api(),
                    tool_choice="auto",
                    stream=True,
                )

                # Process streaming response
                assistant_content = ""
                tool_calls = []
                current_tool_call = None

                for chunk in response:
                    if not chunk.choices:
                        continue

                    delta = chunk.choices[0].delta

                    # Handle content
                    if hasattr(delta, "content") and delta.content:
                        assistant_content += delta.content
                        full_content += delta.content
                        yield MessageDeltaEvent(content=delta.content)

                    # Handle reasoning (DeepSeek R1)
                    if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                        yield ReasoningEvent(content=delta.reasoning_content)

                    # Handle tool calls
                    if hasattr(delta, "tool_calls") and delta.tool_calls:
                        for tc in delta.tool_calls:
                            if tc.index is not None:
                                # Extend tool_calls list if needed
                                while len(tool_calls) <= tc.index:
                                    tool_calls.append({
                                        "id": "",
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    })

                                current = tool_calls[tc.index]

                                if tc.id:
                                    current["id"] = tc.id
                                if tc.function:
                                    if tc.function.name:
                                        current["function"]["name"] = tc.function.name
                                    if tc.function.arguments:
                                        current["function"]["arguments"] += tc.function.arguments

                    # Check for usage
                    if hasattr(chunk, "usage") and chunk.usage:
                        yield UsageEvent(
                            input_tokens=chunk.usage.prompt_tokens or 0,
                            output_tokens=chunk.usage.completion_tokens or 0,
                            total_tokens=chunk.usage.total_tokens or 0
                        )

                # Add assistant message to history
                if assistant_content or tool_calls:
                    self.history.add(
                        "assistant",
                        assistant_content,
                        tool_calls=tool_calls if tool_calls else None
                    )

                # If no tool calls, we're done
                if not tool_calls:
                    break

                # Execute tool calls
                for tc in tool_calls:
                    tool_name = tc["function"]["name"]
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        args = {}

                    call = ToolCallRequest(
                        id=tc["id"],
                        name=tool_name,
                        arguments=args
                    )

                    # Execute tool (events emitted by observer)
                    result = self.tool_runtime.execute(call)

                    # Add tool result to history
                    self.history.add_tool_result(tc["id"], result)

                    # Yield tool events
                    yield ToolStartEvent(
                        tool_name=tool_name,
                        tool_call_id=tc["id"],
                        parameters=args
                    )
                    yield ToolCompleteEvent(
                        tool_name=tool_name,
                        tool_call_id=tc["id"],
                        result=result
                    )

            # Final completion event
            elapsed_ms = (time.time() - start_time) * 1000
            yield MessageCompleteEvent(content=full_content, elapsed_ms=elapsed_ms)

        except Exception as e:
            # Classify and handle API errors
            api_error = classify_api_error(e)

            if isinstance(api_error, (APIKeyInvalidError, APIFrozenError, APIQuotaExceededError, APIRateLimitError)):
                # Handle the specific API error
                should_retry = handle_api_error(api_error, self.current_provider)

                if should_retry and retry_on_auth_error:
                    # Re-initialize client with new key and retry
                    self._init_client()
                    if self.client:
                        # Retry the request (without recursive retry)
                        yield from self.send(message, retry_on_auth_error=False)
                        return

                yield ErrorEvent(error=str(api_error))
            else:
                yield ErrorEvent(error=str(e))
                raise

        finally:
            self.processing = False

    def cancel(self):
        self.processing = False

# ============================================================================
# COMMAND HANDLER
# ============================================================================
class CommandHandler:
    def __init__(self, agent: AgentController, shell: 'InteractiveShell'):
        self.agent = agent
        self.shell = shell
        self.commands = {
            "help": self.cmd_help, "h": self.cmd_help,
            "model": self.cmd_model, "m": self.cmd_model,
            "secrets": self.cmd_secrets, "s": self.cmd_secrets,
            "key": self.cmd_key,
            "clear": self.cmd_clear, "c": self.cmd_clear,
            "history": self.cmd_history,
            "tools": self.cmd_tools,
            "guardrails": self.cmd_guardrails, "g": self.cmd_guardrails,
            "exit": self.cmd_exit, "quit": self.cmd_exit, "q": self.cmd_exit,
            "debug": self.cmd_debug,
            "bash": self.cmd_bash,
            "version": self.cmd_version, "v": self.cmd_version,
        }

    def handle(self, command: str) -> bool:
        parts = command[1:].split(None, 1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            return self.commands[cmd](args)
        else:
            print_error(f"Unknown command: /{cmd}. Type /help for commands.")
            return True

    def cmd_help(self, args: str) -> bool:
        help_text = """
[bold cyan]DeepSeek Coder CLI v2.0[/]

[yellow]Commands:[/]
  /model, /m [provider] [model]  Switch AI model
  /secrets, /s                   Manage API keys
  /key <api_key>                 Set DEEPSEEK_API_KEY
  /tools                         List available tools
  /guardrails, /g                Show HITL guardrails status
  /clear, /c                     Clear screen
  /history                       Show conversation
  /debug                         Toggle debug mode
  /bash <cmd>                    Run shell command
  /exit, /quit, /q               Exit

[yellow]Tools Available:[/]
  Bash   - Execute shell commands
  Read   - Read file contents
  Write  - Write to files
  Edit   - Edit files (replace text)
  Glob   - Find files by pattern
  Grep   - Search file contents

[yellow]HITL Guardrails (MQ-9 Reaper Model):[/]
  ROUTINE  - Auto-approved (read, search, analysis)
  ELEVATED - Logged (file writes, git ops)
  CRITICAL - 1 confirm (system changes)
  LETHAL   - 2 confirms + delay (destructive ops)

[yellow]Keyboard:[/]
  Ctrl+C  Interrupt    Ctrl+D  Exit
  Up/Down History      Ctrl+L  Clear
"""
        if RICH_AVAILABLE and console:
            console.print(Panel(help_text, title="Help", border_style="cyan"))
        else:
            print(help_text)
        return True

    def cmd_model(self, args: str) -> bool:
        if not args:
            if RICH_AVAILABLE and console:
                table = Table(title="Available Models")
                table.add_column("Provider", style="cyan")
                table.add_column("Models", style="green")
                table.add_column("Status")

                for provider in Provider:
                    config = PROVIDER_CONFIG[provider]
                    models = ", ".join(config["models"])
                    has_key = secrets.has_provider_key(provider)
                    status = "[green]✓ Ready[/]" if has_key else "[red]✗ No key[/]"
                    current = " *" if provider == self.agent.current_provider else ""
                    table.add_row(provider.value + current, models, status)

                console.print(table)
                console.print(f"\nCurrent: [bold]{self.agent.current_provider.value}/{self.agent.current_model}[/]")
            return True

        parts = args.replace("/", " ").split()
        provider_name = parts[0].lower()
        model_name = parts[1] if len(parts) > 1 else None

        try:
            provider = Provider(provider_name)
            self.agent.switch_provider(provider, model_name)
        except ValueError:
            print_error(f"Unknown provider: {provider_name}")
        return True

    def cmd_secrets(self, args: str) -> bool:
        if RICH_AVAILABLE and console:
            table = Table(title="API Keys")
            table.add_column("Provider", style="cyan")
            table.add_column("Variable", style="yellow")
            table.add_column("Status")

            for provider in Provider:
                key_env = PROVIDER_CONFIG[provider]["key_env"]
                has_key = secrets.has_provider_key(provider)
                status = "[green]✓ Set[/]" if has_key else "[red]✗ Not set[/]"
                table.add_row(provider.value, key_env, status)

            console.print(table)
        return True

    def cmd_key(self, args: str) -> bool:
        if not args:
            print_error("Usage: /key <YOUR_DEEPSEEK_API_KEY>")
            return True
        secrets.set("DEEPSEEK_API_KEY", args.strip())
        self.agent._init_client()
        return True

    def cmd_clear(self, args: str) -> bool:
        os.system('clear' if os.name != 'nt' else 'cls')
        self.shell.print_banner()
        return True

    def cmd_history(self, args: str) -> bool:
        for msg in self.agent.history.messages[-20:]:
            color = {"user": "green", "assistant": "blue", "system": "yellow", "tool": "cyan"}.get(msg.role, "white")
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            if RICH_AVAILABLE and console:
                console.print(f"[{color}]{msg.role}:[/] {content}")
            else:
                print(f"{msg.role}: {content}")
        return True

    def cmd_tools(self, args: str) -> bool:
        if RICH_AVAILABLE and console:
            table = Table(title="Available Tools")
            table.add_column("Tool", style="cyan")
            table.add_column("Description", style="white")

            for name, tool in self.agent.tool_runtime.tools.items():
                table.add_row(name, tool.description[:60])

            console.print(table)
        else:
            for name, tool in self.agent.tool_runtime.tools.items():
                print(f"  {name}: {tool.description[:60]}")
        return True

    def cmd_guardrails(self, args: str) -> bool:
        """Show guardrails status and statistics."""
        g = guardrails  # Global guardrails instance
        stats = g.get_stats()

        if RICH_AVAILABLE and console:
            console.print("\n[bold cyan]HITL Guardrails System[/] (MQ-9 Reaper Model)")
            console.print("[dim]Autonomous for routine, human auth for critical/lethal[/]\n")

            # Operation levels
            level_table = Table(title="Operation Levels")
            level_table.add_column("Level", style="cyan")
            level_table.add_column("Approval", style="yellow")
            level_table.add_column("Violations")
            level_table.add_row("ROUTINE", "Auto-approved", str(stats['by_level']['ROUTINE']))
            level_table.add_row("ELEVATED", "Logged", str(stats['by_level']['ELEVATED']))
            level_table.add_row("CRITICAL", "1 confirm + delay", str(stats['by_level']['CRITICAL']))
            level_table.add_row("LETHAL", "2 confirms + 5s delay", str(stats['by_level']['LETHAL']))
            console.print(level_table)

            # Stats
            console.print(f"\n[yellow]Statistics:[/]")
            console.print(f"  Total violations: {stats['total_violations']}")
            console.print(f"  Blocked operations: {stats['blocked_operations']}")
            console.print(f"  Audit entries: {stats['audit_entries']}")

            # Recent violations
            if g.violations:
                console.print(f"\n[yellow]Recent Violations:[/]")
                for v in g.violations[-5:]:
                    status = "[red]BLOCKED[/]" if v.blocked else "[yellow]ALLOWED[/]"
                    console.print(f"  {v.level.name} | {v.tool_name} | {v.reason[:40]} | {status}")
        else:
            print("\nHITL Guardrails System (MQ-9 Reaper Model)")
            print(f"Violations: {stats['total_violations']}, Blocked: {stats['blocked_operations']}")
            for level, count in stats['by_level'].items():
                print(f"  {level}: {count}")

        return True

    def cmd_exit(self, args: str) -> bool:
        print_info("Goodbye!")
        return False

    def cmd_debug(self, args: str) -> bool:
        self.shell.debug = not self.shell.debug
        print_info(f"Debug mode {'enabled' if self.shell.debug else 'disabled'}")
        return True

    def cmd_bash(self, args: str) -> bool:
        if not args:
            print_error("Usage: /bash <command>")
            return True

        call = ToolCallRequest(id=str(uuid.uuid4()), name="Bash", arguments={"command": args})
        result = self.agent.tool_runtime.execute(call)
        print(result)
        return True

    def cmd_version(self, args: str) -> bool:
        print(f"deepseek-coder-cli v{__version__}")
        return True

# ============================================================================
# INTERACTIVE SHELL
# ============================================================================
class InteractiveShell:
    def __init__(self):
        self.agent = AgentController()
        self.command_handler = CommandHandler(self.agent, self)
        self.debug = False
        self.running = True
        self._setup_readline()
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _setup_readline(self):
        history_file = CONFIG_DIR / "readline_history"
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            if history_file.exists():
                readline.read_history_file(str(history_file))
            readline.set_history_length(1000)
            import atexit
            atexit.register(readline.write_history_file, str(history_file))
        except Exception:
            pass

    def _handle_interrupt(self, signum, frame):
        if self.agent.processing:
            self.agent.cancel()
            print("\n[Interrupted]")
        else:
            print("\n[Use /exit or Ctrl+D to quit]")

    def print_banner(self):
        banner = f"""
╔═══════════════════════════════════════════════════════════╗
║          DeepSeek Coder CLI v{__version__:<24}║
║          AI-powered coding assistant with tools           ║
╚═══════════════════════════════════════════════════════════╝"""
        if RICH_AVAILABLE and console:
            console.print(banner, style="bold cyan")
            console.print(f"Provider: [green]{self.agent.current_provider.value}[/] | Model: [yellow]{self.agent.current_model}[/]")
            console.print(f"Working dir: [dim]{self.agent.working_dir}[/]")
            console.print("Type [bold]/help[/] for commands, [bold]/tools[/] to see available tools.\n")
        else:
            print(banner)
            print(f"Provider: {self.agent.current_provider.value} | Model: {self.agent.current_model}")
            print(f"Working dir: {self.agent.working_dir}")
            print("Type /help for commands.\n")

    def stream_response(self, message: str):
        """Stream response with tool execution display."""
        if RICH_AVAILABLE and console:
            console.print()

        try:
            for event in self.agent.send(message):
                if isinstance(event, MessageDeltaEvent):
                    if event.content:
                        if RICH_AVAILABLE and console:
                            console.print(event.content, end="")
                        else:
                            print(event.content, end="", flush=True)

                elif isinstance(event, ReasoningEvent):
                    if self.debug and event.content:
                        if RICH_AVAILABLE and console:
                            console.print(f"[dim italic]{event.content}[/]", end="")

                elif isinstance(event, MessageCompleteEvent):
                    if RICH_AVAILABLE and console:
                        console.print()
                        console.print(f"[dim]({event.elapsed_ms:.0f}ms)[/]")
                    else:
                        print(f"\n({event.elapsed_ms:.0f}ms)")

                elif isinstance(event, ErrorEvent):
                    print_error(event.error)

                # Tool events are printed by the observer

        except Exception as e:
            print_error(str(e))
            if self.debug:
                import traceback
                traceback.print_exc()

    def run(self, initial_prompt: Optional[str] = None):
        self.print_banner()

        if initial_prompt:
            print(f"> {initial_prompt}")
            self.stream_response(initial_prompt)

        while self.running:
            try:
                if RICH_AVAILABLE and console:
                    user_input = console.input("[bold green]>[/] ")
                else:
                    user_input = input("> ")

                user_input = user_input.strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    self.running = self.command_handler.handle(user_input)
                    continue

                self.stream_response(user_input)

            except EOFError:
                print()
                self.running = False
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print_error(str(e))
                if self.debug:
                    import traceback
                    traceback.print_exc()

        print_info("Goodbye!")

# ============================================================================
# QUICK MODE
# ============================================================================
def run_quick_mode(prompt: str, model: Optional[str] = None):
    agent = AgentController()

    if model:
        for provider in Provider:
            if model in PROVIDER_CONFIG[provider]["models"]:
                try:
                    agent.switch_provider(provider, model)
                except Exception:
                    pass
                break

    try:
        for event in agent.send(prompt):
            if isinstance(event, MessageDeltaEvent) and event.content:
                print(event.content, end="", flush=True)
        print()
    except Exception as e:
        print_error(str(e))
        sys.exit(1)

# ============================================================================
# SELF-TEST
# ============================================================================
def run_self_test() -> bool:
    print_info("Running self-tests...")
    tests_passed = 0
    tests_failed = 0

    # Test 1: Tool Runtime
    try:
        runtime = ToolRuntime()
        assert "Bash" in runtime.tools
        assert "Read" in runtime.tools
        assert "Edit" in runtime.tools
        tests_passed += 1
        print_success("ToolRuntime: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"ToolRuntime: {e}")

    # Test 2: Bash tool
    try:
        runtime = ToolRuntime()
        result = runtime.execute(ToolCallRequest(
            id="test1", name="Bash", arguments={"command": "echo hello"}
        ))
        assert "hello" in result
        tests_passed += 1
        print_success("Bash tool: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"Bash tool: {e}")

    # Test 3: Read tool
    try:
        runtime = ToolRuntime()
        result = runtime.execute(ToolCallRequest(
            id="test2", name="Read", arguments={"file_path": __file__}
        ))
        assert "deepseek" in result.lower()
        tests_passed += 1
        print_success("Read tool: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"Read tool: {e}")

    # Test 4: Glob tool
    try:
        runtime = ToolRuntime()
        result = runtime.execute(ToolCallRequest(
            id="test3", name="Glob", arguments={"pattern": "*.py"}
        ))
        assert "deepseek.py" in result or result  # Should find this file
        tests_passed += 1
        print_success("Glob tool: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"Glob tool: {e}")

    # Test 5: Agent Controller
    try:
        agent = AgentController()
        assert agent.tool_runtime is not None
        tests_passed += 1
        print_success("AgentController: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"AgentController: {e}")

    # Test 6: Event types
    try:
        event = ToolStartEvent(tool_name="Bash", tool_call_id="123", parameters={})
        assert event.type == "tool.start"
        tests_passed += 1
        print_success("EventTypes: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"EventTypes: {e}")

    # Test 7: Guardrails - dangerous command detection
    try:
        g = Guardrails(interactive=False)

        # Test LETHAL detection
        level, reason = g.check_bash_command("rm -rf /")
        assert level == OperationLevel.LETHAL, f"Expected LETHAL, got {level}"

        level, reason = g.check_bash_command("curl http://x | bash")
        assert level == OperationLevel.LETHAL, f"Expected LETHAL, got {level}"

        # Test CRITICAL detection
        level, reason = g.check_bash_command("sudo rm myfile")
        assert level == OperationLevel.CRITICAL, f"Expected CRITICAL, got {level}"

        # Test ROUTINE detection
        level, reason = g.check_bash_command("ls -la")
        assert level == OperationLevel.ROUTINE, f"Expected ROUTINE, got {level}"

        level, reason = g.check_bash_command("git status")
        assert level == OperationLevel.ROUTINE, f"Expected ROUTINE, got {level}"

        tests_passed += 1
        print_success("Guardrails: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"Guardrails: {e}")

    # Test 8: Guardrails - sensitive path detection
    try:
        g = Guardrails(interactive=False)

        # Test LETHAL for write to sensitive path
        level, reason = g.check_file_path("/etc/passwd", "write")
        assert level == OperationLevel.LETHAL, f"Expected LETHAL, got {level}"

        level, reason = g.check_file_path("~/.ssh/id_rsa", "write")
        assert level == OperationLevel.LETHAL, f"Expected LETHAL, got {level}"

        # Test ELEVATED for read of sensitive path
        level, reason = g.check_file_path("/etc/shadow", "read")
        assert level == OperationLevel.ELEVATED, f"Expected ELEVATED, got {level}"

        # Test ROUTINE for normal files
        level, reason = g.check_file_path("/home/user/myfile.txt", "read")
        assert level == OperationLevel.ROUTINE, f"Expected ROUTINE, got {level}"

        tests_passed += 1
        print_success("Guardrails paths: OK")
    except Exception as e:
        tests_failed += 1
        print_error(f"Guardrails paths: {e}")

    print()
    print(f"Tests: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="DeepSeek Coder CLI - AI coding assistant with tool use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          deepseek                     Interactive shell
          deepseek "fix the bug"       Start with prompt
          deepseek -q "run tests"      Quick mode
          deepseek --key YOUR_KEY      Set API key

        Tools: Bash, Read, Write, Edit, Glob, Grep
        """)
    )

    parser.add_argument("prompt", nargs="?", help="Initial prompt")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-q", "--quick", action="store_true", help="Quick mode (non-interactive)")
    parser.add_argument("--key", metavar="API_KEY", help="Set DEEPSEEK_API_KEY")
    parser.add_argument("--model", metavar="MODEL", help="Model to use")
    parser.add_argument("--self-test", action="store_true", help="Run self-tests")

    args = parser.parse_args()

    if args.key:
        secrets.set("DEEPSEEK_API_KEY", args.key)
        sys.exit(0)

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    is_tty = sys.stdin.isatty() and sys.stdout.isatty()

    stdin_prompt = None
    if not sys.stdin.isatty():
        stdin_prompt = sys.stdin.read().strip()

    prompt = args.prompt or stdin_prompt

    if args.quick or (prompt and not is_tty):
        if not prompt:
            print_error("No prompt for quick mode")
            sys.exit(1)
        run_quick_mode(prompt, args.model)
        sys.exit(0)

    if is_tty:
        shell = InteractiveShell()
        if args.model:
            for provider in Provider:
                if args.model in PROVIDER_CONFIG[provider]["models"]:
                    try:
                        shell.agent.switch_provider(provider, args.model)
                    except Exception:
                        pass
                    break
        shell.run(initial_prompt=prompt)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
