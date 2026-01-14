"""Shell history analyzer for Terminal Wrapped."""

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class WrappedStats:
    """Statistics computed from shell history."""

    total_commands: int = 0
    top_commands: list[tuple[str, int]] = field(default_factory=list)
    top_cd_targets: list[tuple[str, int]] = field(default_factory=list)
    top_z_targets: list[tuple[str, int]] = field(default_factory=list)
    commands_by_day: dict[str, int] = field(default_factory=dict)
    most_piped_commands: list[tuple[str, int]] = field(default_factory=list)
    git_subcommands: list[tuple[str, int]] = field(default_factory=list)
    commands_by_hour: dict[int, int] = field(default_factory=dict)
    unique_commands: int = 0
    pipe_count: int = 0
    sudo_count: int = 0
    avg_command_length: float = 0.0
    useless_cat_count: int = 0
    useless_cat_examples: list[str] = field(default_factory=list)
    typos: list[tuple[str, int]] = field(default_factory=list)
    date_range: tuple[datetime, datetime] | None = None


@dataclass
class HistoryEntry:
    """A single history entry."""

    timestamp: datetime | None
    command: str


def parse_zsh_history(path: Path) -> list[HistoryEntry]:
    """Parse zsh history file.

    Zsh extended history format: `: timestamp:0;command`
    """
    entries = []
    pattern = re.compile(r"^: (\d+):\d+;(.+)$")

    try:
        with open(path, "r", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                match = pattern.match(line)
                if match:
                    try:
                        ts = datetime.fromtimestamp(int(match.group(1)))
                        cmd = match.group(2)
                        entries.append(HistoryEntry(ts, cmd))
                    except (ValueError, OSError):
                        entries.append(HistoryEntry(None, line))
                else:
                    entries.append(HistoryEntry(None, line))
    except (IOError, OSError):
        pass

    return entries


def parse_bash_history(path: Path) -> list[HistoryEntry]:
    """Parse bash history file (typically no timestamps)."""
    entries = []

    try:
        with open(path, "r", errors="replace") as f:
            for line in f:
                cmd = line.strip()
                if cmd and not cmd.startswith("#"):
                    entries.append(HistoryEntry(None, cmd))
    except (IOError, OSError):
        pass

    return entries


def extract_base_command(cmd: str) -> str:
    """Extract the base command from a full command line."""
    cmd = cmd.strip()

    prefixes = ["sudo", "env", "time", "nice", "nohup"]
    parts = cmd.split()

    while parts and parts[0] in prefixes:
        parts = parts[1:]
        while parts and "=" in parts[0]:
            parts = parts[1:]

    if not parts:
        return cmd.split()[0] if cmd.split() else cmd

    first_cmd = parts[0]
    first_cmd = first_cmd.lstrip("(").lstrip("$").lstrip("{")

    return first_cmd


def extract_cd_target(cmd: str) -> str | None:
    """Extract directory from cd command."""
    cmd = cmd.strip()
    if cmd.startswith("cd ") or cmd == "cd":
        parts = cmd.split(maxsplit=1)
        if len(parts) > 1:
            target = parts[1].strip()
            if (target.startswith('"') and target.endswith('"')) or (
                target.startswith("'") and target.endswith("'")
            ):
                target = target[1:-1]
            return target
        return "~"
    return None


def extract_z_target(cmd: str) -> str | None:
    """Extract target from z/zoxide command."""
    cmd = cmd.strip()
    if cmd.startswith("z ") or cmd.startswith("zoxide "):
        parts = cmd.split(maxsplit=1)
        if len(parts) > 1:
            return parts[1].strip()
    return None


KNOWN_TYPOS = {
    "gti": "git",
    "got": "git",
    "gir": "git",
    "gi": "git",
    "sl": "ls",
    "lls": "ls",
    "sls": "ls",
    "pyhton": "python",
    "pytohn": "python",
    "pyton": "python",
    "pythno": "python",
    "ptyhon": "python",
    "cd..": "cd ..",
    "cd~": "cd ~",
    "claer": "clear",
    "clera": "clear",
    "cler": "clear",
    "celar": "clear",
    "grpe": "grep",
    "grrp": "grep",
    "gerp": "grep",
    "mkdri": "mkdir",
    "mkdr": "mkdir",
    "mdkir": "mkdir",
    "nmp": "npm",
    "nppm": "npm",
    "nom": "npm",
    "pnm": "npm",
    "dcoker": "docker",
    "dokcer": "docker",
    "docekr": "docker",
    "suod": "sudo",
    "sduo": "sudo",
    "sodu": "sudo",
    "eixt": "exit",
    "exti": "exit",
    "eit": "exit",
    "vmi": "vim",
    "cim": "vim",
    "bim": "vim",
    "nano": "nano",
    "nanao": "nano",
    "sssh": "ssh",
    "shh": "ssh",
}


def is_useless_cat(cmd: str) -> bool:
    """Check if command is a useless use of cat."""
    useless_patterns = [
        r"cat\s+\S+\s*\|\s*grep",
        r"cat\s+\S+\s*\|\s*head",
        r"cat\s+\S+\s*\|\s*tail",
        r"cat\s+\S+\s*\|\s*wc",
        r"cat\s+\S+\s*\|\s*sort",
        r"cat\s+\S+\s*\|\s*uniq",
        r"cat\s+\S+\s*\|\s*awk",
        r"cat\s+\S+\s*\|\s*sed",
        r"cat\s+\S+\s*\|\s*cut",
        r"cat\s+\S+\s*\|\s*less",
        r"cat\s+\S+\s*\|\s*more",
    ]
    for pattern in useless_patterns:
        if re.search(pattern, cmd):
            return True
    return False


def extract_git_subcommand(cmd: str) -> str | None:
    """Extract git subcommand from a git command."""
    cmd = cmd.strip()
    if cmd.startswith("git "):
        parts = cmd.split()
        if len(parts) >= 2:
            idx = 1
            while idx < len(parts) and parts[idx].startswith("-"):
                idx += 1
                if idx < len(parts) and not parts[idx].startswith("-"):
                    idx += 1
            if idx < len(parts):
                return parts[idx]
    return None


def analyze_history(entries: list[HistoryEntry]) -> WrappedStats:
    """Compute all statistics from history entries."""
    if not entries:
        return WrappedStats()

    command_counter: Counter[str] = Counter()
    cd_counter: Counter[str] = Counter()
    z_counter: Counter[str] = Counter()
    day_counter: Counter[str] = Counter()
    hour_counter: Counter[int] = Counter()
    git_counter: Counter[str] = Counter()

    timestamps = []
    unique_cmds: set[str] = set()
    pipe_count = 0
    pipe_rich_commands: list[tuple[str, int]] = []
    sudo_count = 0
    total_length = 0
    useless_cat_count = 0
    useless_cat_examples: list[str] = []
    typo_counter: Counter[str] = Counter()

    for entry in entries:
        cmd = entry.command

        if entry.timestamp:
            timestamps.append(entry.timestamp)
            day_name = entry.timestamp.strftime("%A")
            day_counter[day_name] += 1
            hour_counter[entry.timestamp.hour] += 1

        unique_cmds.add(cmd)
        total_length += len(cmd)

        pipe_instances = cmd.count("|")
        if pipe_instances:
            pipe_count += 1
            pipe_rich_commands.append((cmd, pipe_instances))
        if cmd.startswith("sudo ") or " sudo " in cmd:
            sudo_count += 1

        if is_useless_cat(cmd):
            useless_cat_count += 1
            if len(useless_cat_examples) < 5:
                useless_cat_examples.append(cmd)

        first_word = cmd.split()[0] if cmd.split() else ""
        if first_word in KNOWN_TYPOS:
            typo_counter[first_word] += 1

        base_cmd = extract_base_command(cmd)
        if base_cmd:
            command_counter[base_cmd] += 1

        git_sub = extract_git_subcommand(cmd)
        if git_sub:
            git_counter[git_sub] += 1

        cd_target = extract_cd_target(cmd)
        if cd_target:
            cd_counter[cd_target] += 1

        z_target = extract_z_target(cmd)
        if z_target:
            z_counter[z_target] += 1

    date_range = None
    if timestamps:
        date_range = (min(timestamps), max(timestamps))

    seen_pipe_cmds: set[str] = set()
    most_piped_commands: list[tuple[str, int]] = []
    for cmd, count in sorted(
        pipe_rich_commands,
        key=lambda item: (item[1], len(item[0])),
        reverse=True,
    ):
        if cmd not in seen_pipe_cmds:
            seen_pipe_cmds.add(cmd)
            most_piped_commands.append((cmd, count))
            if len(most_piped_commands) >= 3:
                break

    return WrappedStats(
        total_commands=len(entries),
        top_commands=command_counter.most_common(10),
        top_cd_targets=cd_counter.most_common(10),
        top_z_targets=z_counter.most_common(10),
        commands_by_day=dict(day_counter),
        most_piped_commands=most_piped_commands,
        git_subcommands=git_counter.most_common(10),
        commands_by_hour=dict(hour_counter),
        unique_commands=len(unique_cmds),
        pipe_count=pipe_count,
        sudo_count=sudo_count,
        avg_command_length=total_length / len(entries) if entries else 0,
        useless_cat_count=useless_cat_count,
        useless_cat_examples=useless_cat_examples,
        typos=typo_counter.most_common(10),
        date_range=date_range,
    )


def load_history() -> WrappedStats:
    """Load shell history and return stats."""
    zsh_path = Path.home() / ".zsh_history"
    bash_path = Path.home() / ".bash_history"

    entries = []

    if zsh_path.exists():
        entries = parse_zsh_history(zsh_path)
    elif bash_path.exists():
        entries = parse_bash_history(bash_path)

    return analyze_history(entries)
