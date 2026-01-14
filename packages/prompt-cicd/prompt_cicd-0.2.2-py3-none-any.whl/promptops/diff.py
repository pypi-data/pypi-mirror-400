"""Module for computing diffs between prompt strings or files."""

import difflib
import sys
from typing import List, Optional, Any

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, attrs=None):
        return text

def diff_prompts(old: str, new: str, mode: str = "unified", color: bool = False) -> str:
    """
    Compute a diff between two prompt strings.
    mode: 'unified', 'side-by-side', or 'inline'
    color: colorize output if True
    """
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    if mode == "unified":
        diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
        return _colorize_diff(diff, color)
    elif mode == "side-by-side":
        return side_by_side_diff(old_lines, new_lines, color)
    elif mode == "inline":
        return inline_diff(old_lines, new_lines, color)
    else:
        raise ValueError(f"Unknown diff mode: {mode}")

def side_by_side_diff(old_lines: List[str], new_lines: List[str], color: bool = False) -> str:
    """Show a side-by-side diff of two lists of lines."""
    sm = difflib.SequenceMatcher(None, old_lines, new_lines)
    result = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        for i in range(max(i2 - i1, j2 - j1)):
            left = old_lines[i1 + i] if i1 + i < i2 else ""
            right = new_lines[j1 + i] if j1 + i < j2 else ""
            if tag == 'replace':
                l = colored(left, 'red') if color else left
                r = colored(right, 'green') if color else right
            elif tag == 'delete':
                l = colored(left, 'red', attrs=['bold']) if color else left
                r = ""
            elif tag == 'insert':
                l = ""
                r = colored(right, 'green', attrs=['bold']) if color else right
            else:
                l = left
                r = right
            result.append(f"{l:<50} | {r}")
    return "\n".join(result)

def inline_diff(old_lines: List[str], new_lines: List[str], color: bool = False) -> str:
    """Show an inline diff (with +/- markers)."""
    diff = list(difflib.ndiff(old_lines, new_lines))
    lines = []
    for line in diff:
        if line.startswith("- "):
            lines.append(colored(line, 'red') if color else line)
        elif line.startswith("+ "):
            lines.append(colored(line, 'green') if color else line)
        elif line.startswith("? "):
            lines.append(colored(line, 'yellow') if color else line)
        else:
            lines.append(line)
    return "\n".join(lines)

def _colorize_diff(diff: List[str], color: bool) -> str:
    if not color:
        return "\n".join(diff)
    lines = []
    for line in diff:
        if line.startswith("+") and not line.startswith("+++ "):
            lines.append(colored(line, 'green'))
        elif line.startswith("-") and not line.startswith("--- "):
            lines.append(colored(line, 'red'))
        else:
            lines.append(line)
    return "\n".join(lines)

def diff_summary(old: str, new: str) -> dict:
    """Return a summary of changes: lines added, removed, changed."""
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    diff = list(difflib.ndiff(old_lines, new_lines))
    added = sum(1 for l in diff if l.startswith('+ '))
    removed = sum(1 for l in diff if l.startswith('- '))
    changed = sum(1 for l in diff if l.startswith('? '))
    return {"added": added, "removed": removed, "changed": changed}

def diff_files(old_path: str, new_path: str, mode: str = "unified", color: bool = False) -> str:
    """Diff two files by path."""
    with open(old_path) as f1, open(new_path) as f2:
        old = f1.read()
        new = f2.read()
    return diff_prompts(old, new, mode=mode, color=color)

def diff_objects(obj1: Any, obj2: Any, mode: str = "unified", color: bool = False) -> str:
    """Diff two objects by their string representations."""
    return diff_prompts(str(obj1), str(obj2), mode=mode, color=color)
