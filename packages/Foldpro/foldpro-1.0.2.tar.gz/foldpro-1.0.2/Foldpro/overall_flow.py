from pathlib import Path
from .FoldproHelpers import (Formatter, EXIT, WantsToExit, AtomicCopyError, 
                            PartiallyOrganizedError, NonAtomicMoveError, WrongOSError)
import sys
from typing import Optional, Tuple
import shutil
import re
from rich import print
import platform

# ============================================================================
# MODE HEADERS
# ============================================================================

MODE_HEADERS = {
    'all': Formatter(header="Everything", header_color="yellow"),
    'p_only': Formatter(header="Photos", header_color="blue"),
    'c_only': Formatter(header="Code Files", header_color="red"),
    'd_only': Formatter(header="Downloads From Terminal", header_color="red"),
    'o_only': Formatter(header="Others", header_color="red")
}

HOME_HEADER = Formatter(header="Home", header_color="cyan")


# ============================================================================
# ERROR HANDLING
# ============================================================================

ERROR_MESSAGES = {
    PartiallyOrganizedError: lambda e: (
        f"Foldpro ran into a {e.error_cause.__class__.__name__} while organizing your files."),
    NonAtomicMoveError: lambda e: (
        f"Foldpro ran into a {e.error_cause.__class__.__name__} while moving {str(e.dest)} to final destination.",
    ),
    AtomicCopyError: lambda e: (
        f"Foldpro ran into a {e.error_cause.__class__.__name__} while copying {e.user_folder_copy}.",
    )
}


def format_error_message(description: str, commands: list[str], is_special: bool = False) -> str:
    """Format error message with optional cleanup commands."""
    lines = []
    
    # Header
    if is_special:
        return ("\n[bold]Foldpro Exited.[/bold]")
    else:
        lines.append("[red]------ An Error Occurred ------[/red]")

    # Description
    lines.append(description)
    
    # Cleanup commands
    if commands:
        lines.append("To avoid issues in future runs, please run the following commands:")
        lines.append((" && ".join(commands) if len(commands) > 1 else commands[0]) + "\n")

    # Append Most common fixes if not special case
    if not is_special:
        lines.extend([
            "[cyan]Most Common Fixes:[/cyan]\n",
            "1. Go to: System Settings → Privacy & Security → Full Disk Access\n",
            "2. Turn the button for terminal on: [⚪────] --> [────🟢]\n",
            "3. IF the folder is in iCloud Drive, follow the steps here to store it locally on your mac: https://www.youtube.com/watch?v=wfX4rfVHY7s\n",
            "4. Restart Foldpro and try again."
        ])
    return ('\n'.join(f"[bold]{line}[/bold]" for line in lines)).rstrip()


def find_workspace() -> Optional[Path]:
    """Find workspace in /tmp. Returns None if not found or permission error."""
    try:
        pattern = re.compile(r"^\.Foldpro-Workspace(\d{10})?$")
        return next(
            (p for p in Path("/tmp").iterdir() if p.is_dir() and pattern.match(p.name)),
            None
        )
    except (Exception, KeyboardInterrupt, SystemExit):
        return None


def cleanup_workspace(workspace: Optional[Path]) -> bool:
    """Clean workspace contents. Returns True if successful."""
    if not workspace:
        return True
    
    try:
        for item in workspace.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
        return True
    except (Exception, KeyboardInterrupt, SystemExit):
        return False


def get_error_info(exc: Exception) -> Tuple[str, str]:
    """Get error description for exception."""
    for error_type, handler in ERROR_MESSAGES.items():
        if isinstance(exc, error_type):
            return handler(exc)
    
    return (f"Foldpro ran into an unexpected {exc.__class__.__name__}.")


def clean_exit(func):
    """Handle all errors and ensure clean shutdown."""
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except WantsToExit:
            print("[bold]Foldpro Exited.[/bold]")
            sys.exit(0)
        except WrongOSError:
            print(
                "[red]------ An Error Occurred ------[/red]\n"
                "[bold]Foldpro can only run on macOS.[/bold]"
                )
            sys.exit(1)
        except (Exception, KeyboardInterrupt, SystemExit) as exc:
            # Determine if special case (KeyboardInterrupt)
            is_special = isinstance(exc, KeyboardInterrupt)
            
            # Get error description
            error_desc = get_error_info(exc)
            
            # Collect cleanup commands
            commands = []
            
            # Handle NonAtomicMoveError - try to delete partial move
            if isinstance(exc, NonAtomicMoveError):
                try:
                    if exc.dest.exists():
                        shutil.rmtree(exc.dest)
                except (Exception, KeyboardInterrupt, SystemExit):
                    commands.append(f"rm -rf {str(exc.dest)}")
            
            # Clean workspace
            workspace = find_workspace()
            if not cleanup_workspace(workspace):
                if workspace:
                    commands.append(f"rm -rf {workspace}")
                else:
                    commands.append("rm -rf /tmp/.Foldpro-Workspace*")
            
            # Print error message
            message = format_error_message(
                error_desc if not is_special else "",
                commands,
                is_special
            )
            print(message)
            
            sys.exit(1)
    
    return wrapper


# ============================================================================
# USER INTERACTION
# ============================================================================

def determine_mode() -> str:
    """Get organization mode from user."""
    print(HOME_HEADER.format(
        "How would you like to organize your folders?",
        "* Into all categories (Code Files, Photos, Downloads, Others): all",
        "* Into one subcategory (e.g. Photos): sub"
    ))
    
    while True:
        mode = input('>').strip().lower()
        
        if mode in EXIT:
            raise WantsToExit
        
        if mode == 'all':
            return 'all'
        
        if mode == 'sub':
            return get_subcategory()
        
        print(HOME_HEADER.format(
            "Invalid input. Please enter:",
            "* all - for all categories",
            "* sub - for one subcategory"
        ))


def get_subcategory() -> str:
    """Get specific subcategory from user."""
    print(HOME_HEADER.format(
        "Which category?",
        "* Photos: (p)",
        "* Code Files: (c)",
        "* Downloads From Terminal: (d)",
        "* Others: (o)",
        "* All categories: (all)"
    ))

    subcategory_map = {('p', 'photos'): 'p_only', ('c', 'code files'): 'c_only', ('d', 'downloads from terminal'): 'd_only', ('o', 'others'): 'o_only', ('all', 'all categories'): 'all'}

    
    while True:
        choice = input('>').strip().lower()
        
        if choice in EXIT:
            raise WantsToExit

        for key, value in subcategory_map.items():
            if choice in key or choice == value:
                return value

        
        print(HOME_HEADER.format(
            "Invalid input. Enter: p, c, d, o, or all"
        ))


def after_organization_decision(final_dest: Path, mode_header: Formatter) -> str:
    """Ask user what to do after organization completes."""
    print(mode_header.format(
        f"Folder '{final_dest.name}' has been organized and is now in ~/{final_dest.parent.name}.",
        "What would you like to do next?",
        "* Organize another folder in current mode: (repeat)",
        "* Choose different mode: (change)",
        "* Exit Foldpro: (exit)"
    ))

    valid_choices = ['repeat', 'r', 'change', 'c', 'exit']

    while True:
        decision = input('>').strip().lower()
        
        if decision in EXIT:
            return 'exit'

        if decision in valid_choices:
            return decision
        
        print(mode_header.format(
            "Invalid input. Enter: repeat, change, or exit"
        ))


def is_macOS() -> None:
    '''Does nothing if the OS is macOS, raises WrongOSError otherwise.'''
    if platform.system() != 'Darwin':
        raise WrongOSError()

