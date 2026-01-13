#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
# ]
# ///
"""
SpecLite CLI - Setup tool for SpecLite projects

Usage:
    uvx speclite-cli install
    uvx speclite-cli install --ai claude,codex
    uvx speclite-cli check

Deprecated (compatibility with GitHub SpecKit):
    uvx speclite-cli init
"""

import os
import subprocess
import sys
import tempfile
import shutil
import shlex
import json
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import typer
from importlib import resources
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar

# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
    },
    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
    },
    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    },
    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },
    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    },
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

BANNER = """
███████╗██████╗ ███████╗ ██████╗██╗     ██╗████████╗███████╗
██╔════╝██╔══██╗██╔════╝██╔════╝██║     ██║╚══██╔══╝██╔════╝
███████╗██████╔╝█████╗  ██║     ██║     ██║   ██║   █████╗
╚════██║██╔═══╝ ██╔══╝  ██║     ██║     ██║   ██║   ██╔══╝
███████║██║     ███████╗╚██████╗███████╗██║   ██║   ███████╗
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚══════╝╚═╝   ╚═╝   ╚══════╝
"""

TAGLINE = "SpecLite - Spec-Driven Development Toolkit"

SLASH_COMMAND_DESCRIPTIONS: dict[str, str] = {
    "constitution": "Establish project principles",
    "specify": "Create baseline specification",
    "plan": "Create implementation plan",
    "tasks": "Generate actionable tasks",
    "implement": "Execute implementation",
    "clarify": "Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/sl.plan[/] if used)",
    "analyze": "Cross-artifact consistency & alignment report (after [cyan]/sl.tasks[/], before [cyan]/sl.implement[/])",
    "checklist": "Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/sl.plan[/])",
    "review": "Review the implementation for the current feature (after [cyan]/sl.implement[/], ideally with a different AI agent)",
    "taskstoissues": "Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature",
}

SLASH_COMMANDS_NEXT_STEPS = ["constitution", "specify", "plan", "tasks", "implement"]
SLASH_COMMANDS_OPTIONAL = ["clarify", "analyze", "checklist", "review", "taskstoissues"]

def _format_slash_command(command: str) -> str:
    return f"[cyan]/sl.{command}[/]"

def _format_slash_command_optional_line(command: str) -> str:
    return f"○ {_format_slash_command(command)} [bright_black](optional)[/bright_black] - {SLASH_COMMAND_DESCRIPTIONS[command]}"

def _print_slash_commands_help() -> None:
    console.print()
    console.print("[bold]Slash Commands[/bold] (run these in your AI agent):")
    console.print("[dim]Generated into your agent folder by running [cyan]speclite-cli install[/cyan].[/dim]")
    console.print()
    console.print("[bold]Core[/bold]")
    for command in SLASH_COMMANDS_NEXT_STEPS:
        console.print(f"  {_format_slash_command(command)} - {SLASH_COMMAND_DESCRIPTIONS[command]}")
    console.print()
    console.print("[bold]Optional[/bold]")
    for command in SLASH_COMMANDS_OPTIONAL:
        console.print(f"  {_format_slash_command(command)} - {SLASH_COMMAND_DESCRIPTIONS[command]}")
class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """
    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {"pending": 0, "running": 1, "done": 2, "error": 3, "skipped": 4}
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label, "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append({"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree

def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return 'up'
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return 'down'

    if key == readchar.key.ENTER:
        return 'enter'

    if key == readchar.key.ESC:
        return 'escape'

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key

def select_with_arrows(options: dict, prompt_text: str = "Select an option", default_key: str = None) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with
        
    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row("", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key

def select_multiple_with_arrows(options: dict, prompt_text: str = "Select options", default_selected: set[str] | None = None) -> list[str]:
    """
    Interactive multi-select using arrow keys with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_selected: Set of option keys to pre-select
        
    Returns:
        List of selected option keys (in display order)
    """
    option_keys = list(options.keys())
    selected_index = 0
    selected_keys = set(default_selected or [])
    warning_text = ""

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            pointer = "▶" if i == selected_index else " "
            check = "[x]" if key in selected_keys else "[ ]"
            label = Text.assemble(
                (check, "white"),
                " ",
                (key, "cyan"),
                " ",
                (f"({options[key]})", "dim"),
            )
            table.add_row(Text(pointer, style="cyan"), label)

        table.add_row("", "")
        table.add_row("", "[dim]Use ↑/↓ to navigate, Space to toggle, Enter to confirm, Esc to cancel[/dim]")
        if warning_text:
            table.add_row("", warning_text)

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_index, warning_text
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == ' ':
                        current_key = option_keys[selected_index]
                        if current_key in selected_keys:
                            selected_keys.remove(current_key)
                        else:
                            selected_keys.add(current_key)
                        warning_text = ""
                    elif key == 'enter':
                        if selected_keys:
                            break
                        warning_text = "[yellow]Select at least one agent to continue[/yellow]"
                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()
    return [key for key in option_keys if key in selected_keys]

def parse_ai_assistants(ai_assistant: str) -> list[str]:
    raw_items = [item.strip() for item in ai_assistant.split(",")]
    candidates = [item for item in raw_items if item]
    seen = set()
    selected = []
    for item in candidates:
        if item not in seen:
            seen.add(item)
            selected.append(item)
    return selected

console = Console()

class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)
        _print_slash_commands_help()


app = typer.Typer(
    name="speclite-cli",
    help="Install or update SpecLite in an existing project",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)

def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()

@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]Run 'speclite-cli --help' for usage information[/dim]"))
        console.print()

def run_command(cmd: list[str], check_return: bool = True, capture: bool = False, shell: bool = False) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(cmd, check=check_return, capture_output=True, text=True, shell=shell)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None

def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.
    
    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results
        
    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI after `claude migrate-installer`
    # See: https://github.com/github/spec-kit/issues/123
    # The migrate-installer command REMOVES the original executable from PATH
    # and creates an alias at ~/.claude/local/claude instead
    # This path should be prioritized over other claude executables in PATH
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True
    
    found = shutil.which(tool) is not None
    
    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")
    
    return found

def handle_vscode_settings(sub_item, dest_file, rel_path, verbose=False, tracker=None) -> None:
    """Handle merging or copying of .vscode/settings.json files."""
    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    try:
        with open(sub_item, 'r', encoding='utf-8') as f:
            new_settings = json.load(f)

        if dest_file.exists():
            merged = merge_json_files(dest_file, new_settings, verbose=verbose and not tracker)
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=4)
                f.write('\n')
            log("Merged:", "green")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge, copying instead: {e}", "yellow")
        shutil.copy2(sub_item, dest_file)

def merge_json_files(existing_path: Path, new_content: dict, verbose: bool = False) -> dict:
    """Merge new JSON content into existing JSON file.

    Performs a deep merge where:
    - New keys are added
    - Existing keys are preserved unless overwritten by new content
    - Nested dictionaries are merged recursively
    - Lists and other values are replaced (not merged)

    Args:
        existing_path: Path to existing JSON file
        new_content: New JSON content to merge in
        verbose: Whether to print merge details

    Returns:
        Merged JSON content as dict
    """
    try:
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, just use new content
        return new_content

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge update dict into base dict."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = deep_merge(result[key], value)
            else:
                # Add new key or replace existing value
                result[key] = value
        return result

    merged = deep_merge(existing_content, new_content)

    if verbose:
        console.print(f"[cyan]Merged JSON file:[/cyan] {existing_path.name}")

    return merged

@contextmanager
def _resource_root_path() -> Path:
    """Return filesystem path to bundled resources, falling back to repo root in dev."""
    packaged_root = resources.files("speclite_cli")
    if (packaged_root / "templates").is_dir():
        with resources.as_file(packaged_root) as root_path:
            yield root_path
        return
    yield Path(__file__).resolve().parents[2]

def _require_resource_dir(root: Path, name: str) -> Path:
    path = root / name
    if not path.is_dir():
        raise FileNotFoundError(f"Missing bundled resource directory: {path}")
    return path

def _strip_frontmatter_sections(text: str) -> str:
    lines = text.split("\n")
    out = []
    dash_count = 0
    in_frontmatter = False
    skip_section = False
    for line in lines:
        if line == "---":
            out.append(line)
            dash_count += 1
            in_frontmatter = dash_count == 1
            if dash_count >= 2:
                in_frontmatter = False
            continue
        if in_frontmatter:
            if line == "scripts:" or line == "agent_scripts:":
                skip_section = True
                continue
            if skip_section and re.match(r"^[A-Za-z]", line):
                skip_section = False
            if skip_section and re.match(r"^[ \t]", line):
                continue
        out.append(line)
    return "\n".join(out)

def _extract_description(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""

def _extract_script_command(text: str, script_variant: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(script_variant)}:\s*(.*)$")
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return ""

def _extract_agent_script_command(text: str, script_variant: str) -> str:
    pattern = re.compile(rf"^\s*{re.escape(script_variant)}:\s*(.*)$")
    in_agent_scripts = False
    for line in text.splitlines():
        if line == "agent_scripts:":
            in_agent_scripts = True
            continue
        if in_agent_scripts:
            match = pattern.match(line)
            if match:
                return match.group(1).strip()
            if re.match(r"^[A-Za-z]", line):
                in_agent_scripts = False
    return ""

def _generate_commands(templates_dir: Path, output_dir: Path, *, agent: str, ext: str, arg_format: str, script_variant: str) -> int:
    commands_dir = templates_dir / "commands"
    if not commands_dir.is_dir():
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for template in sorted(commands_dir.glob("*.md")):
        file_content = template.read_text(encoding="utf-8").replace("\r", "")
        description = _extract_description(file_content)
        script_command = _extract_script_command(file_content, script_variant)
        if not script_command:
            script_command = f"(Missing script command for {script_variant})"
        agent_script_command = _extract_agent_script_command(file_content, script_variant)

        body = file_content.replace("{SCRIPT}", script_command)
        if agent_script_command:
            body = body.replace("{AGENT_SCRIPT}", agent_script_command)
        body = _strip_frontmatter_sections(body)
        body = body.replace("{ARGS}", arg_format).replace("__AGENT__", agent)

        if ext == "toml":
            body = body.replace("\\", "\\\\").rstrip("\n")
            output = f'description = "{description}"\n\nprompt = """\n{body}\n"""\n'
        else:
            output = body.rstrip("\n") + "\n"

        output_path = output_dir / f"sl.{template.stem}.{ext}"
        output_path.write_text(output, encoding="utf-8")
        count += 1
    return count

def _generate_copilot_prompts(agents_dir: Path, prompts_dir: Path) -> int:
    prompts_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for agent_file in sorted(agents_dir.glob("sl.*.agent.md")):
        basename = agent_file.name[:-len(".agent.md")]
        prompt_file = prompts_dir / f"{basename}.prompt.md"
        prompt_file.write_text(f"---\nagent: {basename}\n---\n", encoding="utf-8")
        count += 1
    return count

def _copy_dir_contents(src: Path, dest: Path) -> None:
    if not src.is_dir():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)

def _full_suffix(path: Path) -> str:
    """Return the concatenated suffix string for a path.

    Example:
        >>> 'clarify.default.md' -> '.default.md'
    """
    return "".join(path.suffixes)

def _stem_without_full_suffix(path: Path) -> str:
    """Return the filename with all suffixes removed.

    Example:
        >>> 'clarify.default.md' -> 'clarify'
    """
    suffix = _full_suffix(path)
    return path.name[:-len(suffix)] if suffix else path.name

def _defaulted_path_for_live(path: Path) -> Path:
    """Return the `.default` baseline path for a live template path.

    Example:
        >>> 'plan-template.md' -> 'plan-template.default.md'
    """
    # Example: `plan-template.md` -> `plan-template.default.md`
    if path.suffixes and path.suffixes[0] == ".default":
        return path
    suffix = _full_suffix(path)
    stem = path.name[:-len(suffix)] if suffix else path.name
    return path.with_name(f"{stem}.default{suffix}")

def _prev_default_path(default_path: Path) -> Path:
    """Return the backup path for a `.default` template.

    Example:
        >>> 'plan-template.default.md' -> 'plan-template.default.prev.md'
    """
    return default_path.with_name(f"{default_path.stem}.prev{default_path.suffix}")

def _read_bytes_or_none(path: Path) -> bytes | None:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None

def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)

def _format_path_for_display(path: Path, *, project_root: Path | None = None) -> str:
    """Format a path for console output (prefers repo-relative, colored)."""
    return f"[cyan]{_format_path_for_copy(path, project_root=project_root)}[/cyan]"

def _format_path_for_copy(path: Path, *, project_root: Path | None = None) -> str:
    """Format a path for copy/paste output (prefers repo-relative, no markup)."""
    if project_root is not None:
        try:
            return path.relative_to(project_root).as_posix()
        except ValueError:
            pass
    # Fallback: shorten to `.speclite/...` when possible.
    parts = list(path.parts)
    if ".speclite" in parts:
        idx = parts.index(".speclite")
        return Path(*parts[idx:]).as_posix()
    return path.as_posix()

def _find_pending_default_backups(templates_root: Path) -> list[Path]:
    """Find pending `.default.prev.md` backups that indicate a required manual merge."""
    if not templates_root.is_dir():
        return []
    return sorted(templates_root.rglob("*.default.prev.md"))

def _template_merge_triplet_from_prev(prev_default_path: Path) -> tuple[Path, Path, Path] | None:
    """Return (live, new_default, prev_default) paths from a `.default.prev.md` backup."""
    name = prev_default_path.name
    if not name.endswith(".default.prev.md"):
        return None
    base = name[: -len(".default.prev.md")]
    live = prev_default_path.with_name(base + ".md")
    new_default = prev_default_path.with_name(base + ".default.md")
    return (live, new_default, prev_default_path)

def _render_template_merge_required_notice(prev_default_paths: list[Path], *, project_root: Path) -> str:
    items: list[tuple[Path, Path, Path]] = []
    for prev_path in prev_default_paths:
        triplet = _template_merge_triplet_from_prev(prev_path)
        if triplet is not None:
            items.append(triplet)

    if not items:
        return ""

    live_list = "\n".join(f"  - {_format_path_for_display(live, project_root=project_root)}" for live, _, _ in items)
    lines: list[str] = [
        f"[yellow]Merge required:[/yellow] {len(items)} template(s) you customized have updated defaults.",
        live_list,
        "",
        "Suggested 3-way merge per template (requires git installed, but does not require a git repo):",
        "",
    ]

    for live, new_default, prev_default in items:
        live_copy = _format_path_for_copy(live, project_root=project_root)
        default_copy = _format_path_for_copy(new_default, project_root=project_root)
        prev_copy = _format_path_for_copy(prev_default, project_root=project_root)
        label_width = max(
            len("Live (custom):"),
            len("New default:"),
            len("Previous default:"),
        )

        lines.extend(
            [
                f"[yellow]{live.name}[/yellow]",
                f"{'Live (custom):':<{label_width}} {_format_path_for_display(live, project_root=project_root)}",
                f"{'New default:':<{label_width}} {_format_path_for_display(new_default, project_root=project_root)}",
                f"{'Previous default:':<{label_width}} {_format_path_for_display(prev_default, project_root=project_root)}",
                f"1. [cyan]git merge-file '{live_copy}' '{prev_copy}' '{default_copy}'[/cyan]",
                "2. Search for conflict markers and resolve if present.",
                f"3. Delete previous default when done: {_format_path_for_display(prev_default, project_root=project_root)}",
                "",
            ]
        )

    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)

def _render_pending_template_merges_error(prev_default_paths: list[Path], *, project_root: Path) -> str:
    body = _render_template_merge_required_notice(prev_default_paths, project_root=project_root)
    if not body:
        return ""
    # Recolor the output to red and add a stronger preamble.
    body = body.replace("[yellow]", "[red]").replace("[/yellow]", "[/red]")
    lines = body.splitlines()
    if lines:
        lines[0] = lines[0].replace("[red]Merge required:[/red]", "[red]Unresolved merges:[/red]")

    return "\n".join(
        [
            "[red]You still have unresolved template merges from a previous SpecLite install. You must resolve them first before installing again.[/red]",
            "",
            "\n".join(lines),
            "",
            "After resolving and deleting the previous default file(s), re-run speclite-cli install.",
        ]
    )

def _sync_defaulted_file(
    *,
    new_default_content: bytes,
    live_path: Path,
    default_path: Path,
    notices: list[str] | None = None,
    project_root: Path | None = None,
) -> None:
    """Sync a live file alongside a `.default` baseline.

    Rules:
    - If live is missing OR live exactly equals baseline, update both to new.
    - If live differs from baseline:
      - If baseline is unchanged, keep both contents (touch baseline).
      - If baseline changes, back up old baseline and update baseline; keep live.
    """
    existing_live = _read_bytes_or_none(live_path)
    existing_default = _read_bytes_or_none(default_path)

    if existing_live is None:
        _write_bytes(default_path, new_default_content)
        _write_bytes(live_path, new_default_content)
        return

    if existing_default is None:
        # Baseline missing. Create baseline and preserve user edits if any.
        _write_bytes(default_path, new_default_content)
        if existing_live == new_default_content:
            _write_bytes(live_path, new_default_content)
        elif notices is not None:
            notices.append(
                "[yellow]Created missing default template.[/yellow]\n"
                f"Default: {_format_path_for_display(default_path, project_root=project_root)}\n"
                f"Live (unchanged): {_format_path_for_display(live_path, project_root=project_root)}\n"
                "Verify your live file still matches the latest default with any intended customizations applied."
            )
        return

    if existing_live == existing_default:
        _write_bytes(default_path, new_default_content)
        _write_bytes(live_path, new_default_content)
        return

    # Customized live file: keep it stable.
    if new_default_content == existing_default:
        # No default change; touch the file so installs reflect an update.
        os.utime(default_path, None)
        return

    backup_path = _prev_default_path(default_path)
    if backup_path.exists():
        raise FileExistsError(
            f"Previous default backup already exists: {backup_path}. "
            "Merge and delete .default.prev.md files then restart the install."
        )
    default_path.rename(backup_path)
    _write_bytes(default_path, new_default_content)
    # Merge guidance is rendered once at the end of `speclite-cli install` by scanning for `*.default.prev.md` files.

def _stage_templates(templates_dir: Path, dest_dir: Path) -> None:
    """Stage bundled templates into dest_dir (no `.default` variants).

    `.default` baselines are handled during the apply/merge step so upgrades can
    compare the incoming (staged) template against the existing live+default pair.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    for path in templates_dir.rglob("*"):
        if path.is_dir():
            continue
        rel_path = path.relative_to(templates_dir)
        if rel_path.name == "vscode-settings.json":
            continue
        if ".default" in path.suffixes:
            raise ValueError(
                "Bundled templates must not include `.default` variants; "
                f"found: {rel_path}"
            )
        out_path = dest_dir / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out_path)

def _is_speclite_templates_path(project_path: Path, dest_file: Path) -> bool:
    try:
        rel = dest_file.relative_to(project_path)
    except ValueError:
        return False
    return len(rel.parts) >= 2 and rel.parts[0] == ".speclite" and rel.parts[1] == "templates"

def _apply_template_tree(
    source_dir: Path,
    project_path: Path,
    is_current_dir: bool,
    *,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    notices: list[str] | None = None,
) -> None:
    project_path.mkdir(parents=True, exist_ok=True)

    for sub_item in source_dir.rglob("*"):
        if sub_item.is_dir():
            continue

        rel_path = sub_item.relative_to(source_dir)
        dest_file = project_path / rel_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":
            handle_vscode_settings(sub_item, dest_file, rel_path, verbose, tracker)
            continue

        if _is_speclite_templates_path(project_path, dest_file) and dest_file.suffix.lower() == ".md" and ".default" not in dest_file.suffixes:
            _sync_defaulted_file(
                new_default_content=sub_item.read_bytes(),
                live_path=dest_file,
                default_path=_defaulted_path_for_live(dest_file),
                notices=notices,
                project_root=project_path,
            )
            continue

        if dest_file.exists() and verbose and not tracker and is_current_dir:
            console.print(f"[yellow]Overwriting file:[/yellow] {rel_path}")
        shutil.copy2(sub_item, dest_file)

def download_and_extract_template(
    project_path: Path,
    ai_assistants: list[str],
    script_type: str,
    *,
    is_current_dir: bool = False,
    is_update: bool = False,
    verbose: bool = True,
    tracker: StepTracker | None = None,
    notices: list[str] | None = None,
) -> Path:
    """Generate templates from bundled resources and apply them to the project."""
    if tracker:
        tracker.start("bundle", "loading bundled templates")

    try:
        with _resource_root_path() as resource_root:
            templates_dir = _require_resource_dir(resource_root, "templates")
            scripts_dir = _require_resource_dir(resource_root, "scripts")
            memory_dir = resource_root / "memory"

            if tracker:
                tracker.complete("bundle", "ready")

            with tempfile.TemporaryDirectory() as temp_dir:
                # Stage *all* SpecLite files into a temporary directory first, then merge/copy
                # them into the final destination. This keeps behavior consistent for both:
                # - first-time installs, and
                # - upgrades into an existing repo,
                # and avoids partially-updated repos if an error occurs mid-generation.
                staging_root = Path(temp_dir)
                spec_dir = staging_root / ".speclite"
                spec_dir.mkdir(parents=True, exist_ok=True)

                memory_dest = spec_dir / "memory"
                memory_dest.mkdir(parents=True, exist_ok=True)
                if memory_dir.is_dir():
                    _copy_dir_contents(memory_dir, memory_dest)
                # Scripts are installed under `.speclite/scripts/`.
                scripts_dest = spec_dir / "scripts"
                _copy_dir_contents(scripts_dir / "bash", scripts_dest)
                _copy_dir_contents(scripts_dir / "powershell", scripts_dest)

                # Templates live under `.speclite/templates/` with a `.default` baseline alongside.
                _stage_templates(templates_dir, spec_dir / "templates")

                if tracker:
                    tracker.start("generate", "rendering commands")
                command_count = 0

                # Agent command files are generated into the same staging tree so the apply step
                # can update everything in one pass.
                for ai_assistant in ai_assistants:
                    if ai_assistant == "claude":
                        command_count += _generate_commands(
                            templates_dir,
                            staging_root / ".claude" / "commands",
                            agent=ai_assistant,
                            ext="md",
                            arg_format="$ARGUMENTS",
                            script_variant=script_type,
                        )
                    elif ai_assistant == "gemini":
                        command_count += _generate_commands(
                            templates_dir,
                            staging_root / ".gemini" / "commands",
                            agent=ai_assistant,
                            ext="toml",
                            arg_format="{{args}}",
                            script_variant=script_type,
                        )
                        gemini_notice = resource_root / "agent_templates" / "gemini" / "GEMINI.md"
                        if gemini_notice.is_file():
                            shutil.copy2(gemini_notice, staging_root / "GEMINI.md")
                            command_count += 1
                    elif ai_assistant == "copilot":
                        agents_dir = staging_root / ".github" / "agents"
                        command_count += _generate_commands(
                            templates_dir,
                            agents_dir,
                            agent=ai_assistant,
                            ext="agent.md",
                            arg_format="$ARGUMENTS",
                            script_variant=script_type,
                        )
                        command_count += _generate_copilot_prompts(
                            agents_dir,
                            staging_root / ".github" / "prompts",
                        )
                        vscode_settings = templates_dir / "vscode-settings.json"
                        if vscode_settings.is_file():
                            vscode_dir = staging_root / ".vscode"
                            vscode_dir.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(vscode_settings, vscode_dir / "settings.json")
                            command_count += 1
                    elif ai_assistant == "cursor-agent":
                        command_count += _generate_commands(
                            templates_dir,
                            staging_root / ".cursor" / "commands",
                            agent=ai_assistant,
                            ext="md",
                            arg_format="$ARGUMENTS",
                            script_variant=script_type,
                        )
                    elif ai_assistant == "codex":
                        command_count += _generate_commands(
                            templates_dir,
                            staging_root / ".codex" / "prompts",
                            agent=ai_assistant,
                            ext="md",
                            arg_format="$ARGUMENTS",
                            script_variant=script_type,
                        )

                if tracker:
                    tracker.complete("generate", f"{command_count} file(s)")

                if tracker:
                    tracker.start("apply", "writing templates")
                # Apply the staged tree to the destination project directory (copy or merge),
                # including template default/live sync behavior under `.speclite/templates/`.
                _apply_template_tree(
                    staging_root,
                    project_path,
                    is_current_dir,
                    verbose=verbose,
                    tracker=tracker,
                    notices=notices,
                )
                if tracker:
                    tracker.complete("apply", "written")

        if tracker:
            tracker.complete("cleanup", "temporary files removed")
        return project_path
    except Exception as e:
        if tracker:
            tracker.error("apply", str(e))
        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise


def ensure_executable_scripts(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Ensure POSIX .sh scripts under `.speclite/scripts/` have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".speclite" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat(); mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400: new_mode |= 0o100
            if mode & 0o040: new_mode |= 0o010
            if mode & 0o004: new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (f", {len(failures)} failed" if failures else "")
        tracker.add("chmod", "Set script permissions recursively")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]")
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")

def _install_impl(
    *,
    ai_assistant: str | None,
    script_type: str | None,
    ignore_agent_tools: bool,
    force: bool,
    debug: bool,
) -> None:
    project_path = Path.cwd()

    speclite_dir = project_path / ".speclite"
    git_dir = project_path / ".git"

    if speclite_dir.is_dir():
        is_update = True
    elif git_dir.is_dir() or force:
        is_update = False
    else:
        console.print()
        console.print(
            Panel(
                "No [cyan].speclite/[/cyan] or [cyan].git/[/cyan] directory found in the current working directory.\n\n"
                "SpecLite installs into an existing project. Run from:\n"
                "- your project root (contains [cyan].git/[/cyan]), or\n"
                "- a project that already has SpecLite (contains [cyan].speclite/[/cyan]).\n\n"
                "If you truly want a local install in this directory (without Git), re-run with:\n"
                "[cyan]speclite-cli install --force[/cyan]",
                title="[red]Not a Project Directory[/red]",
                border_style="red",
                padding=(1, 2),
            )
        )
        raise typer.Exit(1)

    if is_update:
        pending_backups = _find_pending_default_backups(speclite_dir / "templates")
        if pending_backups:
            body = _render_pending_template_merges_error(pending_backups, project_root=project_path)
            console.print()
            console.print(
                Panel(
                    body,
                    title="[red]Pending Template Merges[/red]",
                    border_style="red",
                    padding=(1, 2),
                )
            )
            raise typer.Exit(1)

    setup_title = "Updating SpecLite" if is_update else "Installing SpecLite"
    setup_lines = [
        f"[cyan]{setup_title}[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Path':<15} [dim]{project_path}[/dim]",
    ]

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    if ai_assistant:
        selected_agents = parse_ai_assistants(ai_assistant)
        if not selected_agents:
            console.print("[red]Error:[/red] --ai must include at least one assistant (comma-separated)")
            raise typer.Exit(1)
        invalid_agents = [agent for agent in selected_agents if agent not in AGENT_CONFIG]
        if invalid_agents:
            console.print(f"[red]Error:[/red] Invalid AI assistant(s): {', '.join(invalid_agents)}. Choose from: {', '.join(AGENT_CONFIG.keys())}")
            raise typer.Exit(1)
    else:
        if not sys.stdin.isatty():
            console.print("[red]Error:[/red] --ai is required when not running interactively (comma-separated list).")
            raise typer.Exit(1)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_agents = select_multiple_with_arrows(
            ai_choices, 
            "Choose your AI assistant(s):",
            default_selected=set()
        )

    if not ignore_agent_tools:
        missing_agents = []
        for agent in selected_agents:
            agent_config = AGENT_CONFIG.get(agent)
            if agent_config and agent_config["requires_cli"]:
                if not check_tool(agent):
                    missing_agents.append(agent)
        if missing_agents:
            missing_lines = ["The following required AI agent tools were not found:"]
            for agent in missing_agents:
                agent_config = AGENT_CONFIG[agent]
                missing_lines.append(
                    f"  • {agent} ({agent_config['name']}): {agent_config['install_url']}"
                )
            missing_lines.append("")
            missing_lines.append("Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check")
            error_panel = Panel(
                "\n".join(missing_lines),
                title="[red]Agent Detection Error[/red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(SCRIPT_TYPE_CHOICES, "Choose script type (or press Enter)", default_script)
        else:
            selected_script = default_script

    console.print(f"[cyan]Selected AI assistants:[/cyan] {', '.join(selected_agents)}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    tracker = StepTracker("Install SpecLite")

    sys._speclite_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistants")
    tracker.complete("ai-select", ", ".join(selected_agents))
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    for key, label in [
        ("bundle", "Load bundled templates"),
        ("generate", "Generate agent commands"),
        ("apply", "Write templates"),
        ("chmod", "Ensure scripts executable"),
        ("cleanup", "Cleanup"),
        ("final", "Finalize")
    ]:
        tracker.add(key, label)

    template_notices: list[str] = []

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            download_and_extract_template(
                project_path,
                selected_agents,
                selected_script,
                is_current_dir=True,
                is_update=is_update,
                verbose=False,
                tracker=tracker,
                notices=template_notices,
            )

            ensure_executable_scripts(project_path, tracker=tracker)

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Install failed: {e}", title="Failure", border_style="red"))
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]" for k, v in _env_pairs]
                console.print(Panel("\n".join(env_lines), title="Debug Environment", border_style="magenta"))
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())

    note_sections: list[str] = []
    prev_defaults = _find_pending_default_backups(project_path / ".speclite" / "templates")
    merge_note = _render_template_merge_required_notice(prev_defaults, project_root=project_path)
    if merge_note:
        note_sections.append(merge_note)
    note_sections.extend(template_notices)

    if note_sections:
        console.print()
        console.print(
            Panel(
                "\n\n".join(note_sections),
                title="[yellow]Template Merge Required[/yellow]",
                border_style="yellow",
                padding=(1, 2),
            )
        )
    
    if not is_update:
        steps_lines = []
        step_num = 1

        # Add Codex-specific setup step if needed
        if "codex" in selected_agents:
            codex_path = project_path / ".codex"
            quoted_path = shlex.quote(str(codex_path))
            if os.name == "nt":  # Windows
                cmd = f"setx CODEX_HOME {quoted_path}"
            else:  # Unix-like systems
                cmd = f"export CODEX_HOME={quoted_path}"
            
            steps_lines.append(f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]")
            step_num += 1

        steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

        for idx, command in enumerate(SLASH_COMMANDS_NEXT_STEPS, start=1):
            steps_lines.append(f"   {step_num}.{idx} {_format_slash_command(command)} - {SLASH_COMMAND_DESCRIPTIONS[command]}")

        steps_panel = Panel("\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1,2))
        console.print()
        console.print(steps_panel)

        enhancement_lines = [
            "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
            "",
            _format_slash_command_optional_line("clarify"),
            _format_slash_command_optional_line("analyze"),
            _format_slash_command_optional_line("checklist"),
            _format_slash_command_optional_line("review"),
        ]
        enhancements_panel = Panel("\n".join(enhancement_lines), title="Enhancement Commands", border_style="cyan", padding=(1,2))
        console.print()
        console.print(enhancements_panel)

@app.command(name="install", help="Install or update SpecLite in the current project")
def install(
    ai_assistant: str = typer.Option(None, "--ai", help="AI assistant(s) to use (comma-separated): claude, gemini, copilot, cursor-agent, or codex"),
    script_type: str = typer.Option(None, "--script", help="Script type to use: sh or ps"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="Skip checks for AI agent tools like Claude Code"),
    force: bool = typer.Option(False, "--force", help="Force a local install even if .git/ and .speclite/ are missing in the current directory"),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output for installation failures"),
):
    """
    Install or update SpecLite in the current project.

    Run from inside an existing project directory. SpecLite will generate slash
    commands for your agent(s), install `.speclite/` scripts and templates, and
    preserve customized templates during upgrades.
    """
    show_banner()
    _install_impl(
        ai_assistant=ai_assistant,
        script_type=script_type,
        ignore_agent_tools=ignore_agent_tools,
        force=force,
        debug=debug,
    )

@app.command(name="init", hidden=True)
def init(
    ai_assistant: str = typer.Option(None, "--ai", help="AI assistant(s) to use (comma-separated): claude, gemini, copilot, cursor-agent, or codex"),
    script_type: str = typer.Option(None, "--script", help="Script type to use: sh or ps"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="Skip checks for AI agent tools like Claude Code"),
    force: bool = typer.Option(False, "--force", help="Force a local install even if .git/ and .speclite/ are missing in the current directory"),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output for installation failures"),
):
    """Deprecated alias for `speclite-cli install` (kept for compatibility with GitHub SpecKit)."""
    show_banner()
    console.print(
        Panel(
            "[yellow]`speclite-cli init` is deprecated.[/yellow]\n"
            "Use [cyan]speclite-cli install[/cyan] instead.",
            title="[yellow]Deprecation Notice[/yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    _install_impl(
        ai_assistant=ai_assistant,
        script_type=script_type,
        ignore_agent_tools=ignore_agent_tools,
        force=force,
        debug=debug,
    )

@app.command()
def check():
    """Check tool availability and template customization status."""
    show_banner()
    
    tracker = StepTracker("Available Tools Check")

    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_name = agent_config["name"]
        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:
            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
        else:
            # IDE-based agent - skip CLI check and mark as optional
            tracker.skip(agent_key, "IDE-based, no CLI check")
            agent_results[agent_key] = False  # Don't count IDE agents as "found"

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    code_ok = check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    code_insiders_ok = check_tool("code-insiders", tracker=tracker)

    console.print(tracker.render())

    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")

    # Report customized templates (live `.md` differs from `.default.md`).
    cwd = Path.cwd()
    templates_root = cwd / ".speclite" / "templates"
    overridden: list[Path] = []
    if templates_root.is_dir():
        for default_path in sorted(templates_root.rglob("*.default.md")):
            name = default_path.name
            if not name.endswith(".default.md"):
                continue
            live_path = default_path.with_name(name[: -len(".default.md")] + ".md")
            if not live_path.is_file():
                continue
            try:
                if live_path.read_bytes() != default_path.read_bytes():
                    overridden.append(live_path)
            except Exception:
                # Ignore unreadable files (permissions, transient filesystem errors, etc.)
                continue

    console.print()
    if overridden:
        overrides_tree = Tree(f"[cyan]Customized Templates ({len(overridden)})[/cyan]", guide_style="grey50")
        overrides_tree.add("[bright_black]Diff .md vs .default.md to review changes.[/bright_black]")
        for path in overridden:
            try:
                rel = path.relative_to(cwd).as_posix()
            except ValueError:
                rel = path.as_posix()
            overrides_tree.add(f"[yellow]●[/yellow] [white]{path.name}[/white] [bright_black]({rel})[/bright_black]")
        console.print(overrides_tree)
    else:
        detail = (
            "None (all templates match defaults)"
            if templates_root.is_dir()
            else "None (no .speclite/templates directory found)"
        )
        console.print("[cyan]Customized Templates (0)[/cyan]")
        console.print(f"[bright_black]{detail}[/bright_black]")

@app.command()
def version():
    """Display version and system information."""
    import platform
    import importlib.metadata
    
    show_banner()
    
    # Get CLI version from package metadata
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("speclite-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml if running from source
        try:
            import tomllib
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass
    
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="cyan", justify="right")
    info_table.add_column("Value", style="white")

    info_table.add_row("Version", cli_version)
    info_table.add_row("", "")
    info_table.add_row("Python", platform.python_version())
    info_table.add_row("Platform", platform.system())
    info_table.add_row("Architecture", platform.machine())
    info_table.add_row("OS Version", platform.version())

    panel = Panel(
        info_table,
        title="[bold cyan]SpecLite CLI Information[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )

    console.print(panel)
    console.print()

def main():
    app()

if __name__ == "__main__":
    main()
