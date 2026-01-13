import os
import re

DEFAULT_STOP_SEARCH = {"tests", "build", ".venv", ".terragrunt-cache"}
SB_FILENAME = ".sb.yaml"

from fastmcp import FastMCP

app = FastMCP()

@app.tool()
def find_path_in_parent(start_dir: str, target_pattern: str = ".sb.yaml") -> str:
    """Ascend from start_dir until a file matching target_pattern is found or raise."""
    pattern = re.compile(target_pattern)
    current = os.path.dirname(os.path.abspath(start_dir))
    while True:
        for entry in os.listdir(current):
            if pattern.fullmatch(entry):
                candidate = os.path.join(current, entry)
                if os.path.isfile(candidate):
                    return candidate
        parent = os.path.dirname(current)
        if parent == current:
            raise FileNotFoundError(
                f"Could not find file matching pattern '{target_pattern}' from '{start_dir}'"
            )
        current = parent


def find_child_files(
    start_dir: str,
    target_pattern: str = SB_FILENAME,
    stop_search_items: list[str] | None = None,
    skip_initial_stop: bool = True,
    relative: bool = False,
    base_dir: bool = False,
) -> list[str]:
    stop_search_set = set(stop_search_items or []) | DEFAULT_STOP_SEARCH
    pattern = re.compile(target_pattern)

    matches: list[str] = []
    start_dir = os.path.abspath(start_dir)

    for root, dirs, files in os.walk(start_dir, topdown=True):
        is_base_level = os.path.abspath(root) == start_dir

        if not (skip_initial_stop and is_base_level):
            if stop_search_set.intersection(files):
                dirs.clear()
                continue

        dirs[:] = [d for d in dirs if d not in stop_search_set]

        for name in files:
            if pattern.fullmatch(name):
                full_path = os.path.join(root, name)
                if base_dir:
                    result = root
                else:
                    result = full_path
                if relative:
                    result = os.path.relpath(result, start_dir)
                matches.append(result)

    return matches


def get_file_dirs_from_path(
    path: str,
    file_name: str = SB_FILENAME,
    stop_dirs: set[str] | list[str] | None = None,
    include_pattern: str | None = None,
) -> list[str]:
    """Return all directory paths under `path` containing a file matching `file_name`."""
    output = []
    stop_dirs = DEFAULT_STOP_SEARCH | set(stop_dirs or [])
    include_re = re.compile(include_pattern) if include_pattern else None

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in list(stop_dirs)]

        if include_re and not include_re.search(os.path.basename(root)):
            dirs[:] = []
            continue

        for f in files:
            if file_name in f:
                output.append(root)
    return output
