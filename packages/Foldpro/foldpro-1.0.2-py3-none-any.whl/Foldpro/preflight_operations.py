# This module performs the following tasks:
# 1. Finds or makes Foldpro's workspace in /tmp
# 2. Prompts user for folder path and validates it
# 3. Atomically copies user's folder to workspace(/tmp/.Foldpro-Workspace*)

from pathlib import Path
import re
from typing import Union, Optional
from .FoldproHelpers import Formatter, YES, NO, EXIT, is_fold, AtomicCopyError, WantsToExit, mk_random, pretty_unique_path
import os
import time
import shutil
from rich import print

SETUP_FORMATTER = Formatter(header="Setup", header_color="yellow")

# Constants
ICLOUD_ROOT = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
LIBRARY_ROOT = Path.home() / "Library"
MAX_DISPLAY_LENGTH = 83
SIZE_LIMIT_GB = 1.0
SIZE_CHECK_TIMEOUT = 10.0



# ============================================================================
# WORKSPACE SETUP
# ============================================================================

def get_workspace() -> Path:
    """
    Create or find Foldpro's workspace in /tmp.
    Returns workspace path.
    """
    # Check if workspace already exists
    pattern = re.compile(r"^\.Foldpro-Workspace(\d{10})?$")
    existing = next(
        (p for p in Path("/tmp").iterdir() if is_fold(p) and pattern.match(p.name)),
        None
    )
    
    if existing:
        return existing
    
    # Create new workspace
    workspace = Path('/tmp/.Foldpro-Workspace')
    base_name = workspace.name
    while workspace.exists():
        workspace = workspace.parent / f"{base_name}{mk_random(10)}"
    workspace.mkdir()
    return workspace



# ============================================================================
# PATH VALIDATION
# ============================================================================

def display_path(path_str: str) -> str:
    """Truncate long paths for display."""
    if len(path_str) > MAX_DISPLAY_LENGTH:
        return f"{path_str[:5]}...{path_str[-5:]}"
    return path_str


def canonical_version(path: str, header: Formatter) -> Union[Path, str]:
    """
    Convert user path to canonical absolute Path.
    Returns Path on success, error string on failure.
    """
    path = Path(path)
    
    # Remove invisible characters and expand ~
    path = Path(re.sub(r'[\u200b\u00a0]', '', str(path))).expanduser()
    
    # Resolve symlinks
    if path.is_symlink():
        try:
            target = Path(os.readlink(path))
        except PermissionError:
            return header.format(
                f"Foldpro doesn't have permission to access {path}'s target. "
                "Please provide another path or grant access and try again."
            )
        
        # Resolve relative targets
        if not target.is_absolute():
            target = path.parent / target
        return target
    
    # Convert relative paths to absolute
    if not path.is_absolute():
        path = Path.cwd() / path
    
    return path


def calculate_folder_size_gb(path: Path, timeout: float = SIZE_CHECK_TIMEOUT) -> float:
    """Calculate folder size in GB with timeout."""
    start_time = time.time()
    total_size = 0
    check_interval = 100  # Check timeout every N files for performance
    file_count = 0
    
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                file_path = Path(root) / file
                total_size += file_path.stat().st_size
                
                # Check timeout periodically instead of every file
                file_count += 1
                if file_count % check_interval == 0 and time.time() - start_time > timeout:
                    return total_size / 1024**3
                    
            except (FileNotFoundError, PermissionError):
                pass
    
    return total_size / 1024**3


def confirm_large_folder(path: Path, header: Formatter) -> Optional[str]:
    """Confirm user wants to copy folder over 1GB. Returns error string or None."""
    size_gb = calculate_folder_size_gb(path)
    
    if size_gb <= SIZE_LIMIT_GB:
        return None
    
    print(header.format(
        f"{path.name} is {size_gb:.1f}GB in size. "
        "Are you sure you want to make an organized copy? (y/n)"
    ))
    
    while True:
        answer = input('>').strip().lower()
        if answer in EXIT:
            raise WantsToExit
        elif answer in YES:
            return None
        elif answer in NO:
            return header.format("Please enter another path.")
        
        print(header.format("Input not understood. Reply 'y' to confirm or 'n' to cancel."))


def validate_path(path: Path, header: Formatter) -> Optional[str]:
    """
    Validate path meets all requirements.
    Returns None if valid, error message string if invalid.
    """
    # Check existence
    if not path.exists():
        return header.format(
            f"The path '{display_path(str(path))}' does not exist. Enter a valid path."
        )
    
    # Check if directory
    if not path.is_dir():
        return header.format(
            f"The path '{display_path(str(path))}' is not a folder. Enter a folder path."
        )
    
    # Check under home directory
    if Path.home() not in path.parents and path != Path.home():
        return header.format(
            "FoldPro can only operate on folders within your home directory. "
            "Please enter a valid path."
        )
    
    # Check not in iCloud
    if ICLOUD_ROOT in path.parents or path == ICLOUD_ROOT:
        return header.format(
            f"FoldPro cannot operate on folders stored in iCloud. "
            f"Please move '{display_path(str(path))}' locally or enter another path."
        )
    
    # Check not in Library
    if LIBRARY_ROOT in path.parents or path == LIBRARY_ROOT:
        return header.format(
            "Foldpro cannot operate on folders under ~/Library. "
            "Please enter another path."
        )
    
    return None


def get_good_path_and_confirm(header: Formatter) -> Path:
    """Prompt user until they provide a valid folder path."""
    print(header.format("Enter the path to the folder you would like to organize."))
    
    while True:
        raw_path = input('>').strip()
        if raw_path.lower() in EXIT:
            raise WantsToExit
        
        # Convert to canonical path
        path = canonical_version(raw_path, header)
        if isinstance(path, str):  # Error occurred
            print(path)
            continue
        
        # Validate path
        error = validate_path(path, header)
        if error:
            print(error)
            continue
        
        # Check size if over 1GB
        size_error = confirm_large_folder(path, header)
        if size_error:
            print(size_error)
            continue
        
        return path


# ============================================================================
# FOLDER COPYING & WRAPPER
# ============================================================================

def mk_copy(workspace: Path, source_folder: Path) -> Path:
    """
    Copy source folder to workspace with unique name.
    Returns path to the copy.
    """
    dest = pretty_unique_path(p=(workspace / source_folder.name), type='folder')
    
    try:
        shutil.copytree(source_folder, dest, symlinks=True)
    except Exception as e:
        raise AtomicCopyError(error_cause=e, user_folder_copy=source_folder)
    
    return dest


def preflight_operations(mode_header: Formatter) -> Path:
    """
    Perform all preflight operations and make sure users OS is macOS.
    Returns path to user's folder copy in workspace.
    """
    workspace = get_workspace()
    user_folder_path = get_good_path_and_confirm(mode_header)
    user_folder_copy = mk_copy(workspace=workspace, source_folder=user_folder_path)
    return user_folder_copy
