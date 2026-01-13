# This module contains functions classes and variables that two or more other modules of the program will use

import random
import re
from pathlib import Path
import unicodedata


FILENAME_PATTERN = re.compile(r'^(?P<hidden>\.?)(?P<stem>.+?)(?P<suffix>(?:\.[^.]+)+)?$')

class Formatter:
    '''
    A class that formats messages for Foldpro to print to the user.
    What it does:
    - Takes a header string when initialized
    - Has a method called format that takes in any number of lines as arguments
    - The format method returns a formatted string with the header and lines formatted nicely
    - The header is surrounded by '=' signs to make it stand out
    - The header is colored based on the header_color attribute
    - Each line is bolded for emphasis
    - The formatted string is ready to be printed using rich's print function
    - Automatically strips all unintended hidden characters (zero-width spaces, etc.)
    '''
    def __init__(self, *, header, header_color):
        self.header = header
        self.header_color = header_color

    @staticmethod
    def _strip_hidden_chars(text: str) -> str:
        """
        Remove all invisible/unintended unicode characters.
        Keeps regular spaces and common whitespace; removes zero-width chars, non-breaking spaces, etc.
        """
        result = []
        for char in text:
            # Keep regular ASCII space, tab, newline, carriage return
            if char in ' \t\n\r':
                result.append(char)
                continue
            
            category = unicodedata.category(char)
            # Skip invisible separators (except regular space), line/para separators, control chars, and format chars
            if category in ('Zs', 'Zl', 'Zp', 'Cf') or (category == 'Cc' and char not in '\n\r\t '):
                continue
            result.append(char)
        return ''.join(result)

    def format(self, *lines):
        # Strip hidden chars from all input lines
        cleaned_lines = [self._strip_hidden_chars(line) for line in lines]
        
        # Determine amount of = to put on each side
        base_amount = 83
        amount_on_each_side = (base_amount - len(self.header))

        # Add one if odd:
        if amount_on_each_side % 2 != 0:
            amount_on_each_side += 1
        # Account for two space in between header words and paranthesis:
        amount_on_each_side -= 2
        
        paranthesis = '=' * (amount_on_each_side // 2)
        formatted_message = [f"[bold {self.header_color}]{paranthesis} {self.header} {paranthesis}[/bold {self.header_color}]\n"]
        for line in cleaned_lines:
            formatted_message.append(f"[bold]{line}[/bold]\n")
        return ( "".join(formatted_message).rstrip())
    
    


# User options that Foldpro will use for memebership checks:
YES = {'yes', 'yep', 'yup', 'y', 'yrp', 'mhmm'}
NO = {'no', 'n', 'nope', 'nah', 'nahh'}
EXIT = {'e', 'exit', 'q', 'quit'}




# Makes however many random digits you tell it too:
def mk_random(amount_of_digits: int) -> str:
    digits = []
    for i in range(amount_of_digits):
        digits.append(str(random.randint(0,9)))
    digits = ''.join(digits)
    return digits





def is_fold(path: Path) -> bool:
    '''
    Foldpros version of pathlibs path.is_dir() that doesnt follow symlinks.
    '''
    is_a_symlink = path.is_symlink()
    is_directory = path.is_dir()
    if is_a_symlink:
        return False
    return is_directory

def exists(p: Path) -> bool:
    '''
    Foldpros version of pathlibs path.exists() that doesnt follow symlinks.
    '''
    if p.is_symlink():
        return True
    return p.exists()

def is_file(path: Path) -> bool:
    '''
    Foldpros version of pathlibs path.is_file() that doesnt follow symlinks.
    '''
    is_a_symlink = path.is_symlink()
    is_a_file = path.is_file()
    if is_a_symlink:
        return False
    return is_a_file



def get_unique_path_components(p: Path, type: str) -> tuple[str, str, Path]:
    '''
    Helper for pretty_unique_path to get the stem, suffix and parent of a path while dealing with multi, sindgle suffix files, hidden files and any mixture of those.'''
    match = FILENAME_PATTERN.match(p.name)
    if type == 'file' and match:
        stem = match.group('hidden') + match.group('stem')
        suffix = match.group('suffix') if match.group('suffix') else ''
        parent = p.parent
    else:
        stem, suffix, parent = p.stem, p.suffix, p.parent
    return stem, suffix, parent




def pretty_unique_path(p: Path, type: str) -> Path:
    '''
    Helper used whenever we wanna get a unique path with minimal number appending.
    '''
    stem, suffix, parent = get_unique_path_components(p, type)
    i = 0
    candidate = p
    while exists(candidate):
        candidate = parent / f"{stem}{i}{suffix}"
        i += 1
    return candidate







# The following custom errors are used to help code in Foldpro to communciate clearly with code in @clean_exit()
# Example:
# preflight_operations() may raise AtomicCopyError if it fails to copy everythign in user given folder atomiclly which tells clean_exit that it needs to clean up any workspace folders left behind from the failed copy attempt.

class AtomicCopyError(Exception):
    '''
    Raised when preflight_operations fails to copy everything in user given folder atomiclly.
    '''
    def __init__(self, error_cause: Exception, user_folder_copy: Path):
        self.error_cause = error_cause
        self.user_folder_copy = user_folder_copy
        

class PartiallyOrganizedError(Exception):
    '''
    Raised when Foldpro_command has organized at least one file/folder but runs into an unexpected error before finishing.
    '''
    def __init__(self, error_cause: Exception, src: Path, dest: Path):
        self.error_cause = error_cause


class NonAtomicMoveError(Exception):
    '''
    Raised when Foldpro fails to move all files to final location(~/Foldpro Copies*).
    P.S. It's called “NonAtomic” because shutil.move does not guarantee atomicity; an error during execution can occur mid-operation, resulting in a partial move.
    '''
    def __init__(self, error_cause: Exception, dest: Path):
        self.error_cause = error_cause
        self.dest = dest

class WantsToExit(Exception):
    '''
    Raised when user wants to exit Foldpro gracefully.
    '''
    pass
class WrongOSError(Exception):
    '''
    Raised when the user is not running Foldpro on macOS.
    '''
    pass
