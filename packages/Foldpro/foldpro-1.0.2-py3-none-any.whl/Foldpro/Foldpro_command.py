# This module contains the bussines logic of Foldpro for copying, inspecting, and manipulating user folders


from pathlib import Path
import shutil
from typing import Tuple, Literal, Optional
import os
import re
from .FoldproHelpers import pretty_unique_path, PartiallyOrganizedError, NonAtomicMoveError

# Used by organize_files and organize_symlinks functions, respectively:
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".webp", ".cr2", ".nef", ".arw", ".dng", ".svg"
}

CODE_EXTENSIONS = {
    ".py", ".pyw", ".ipynb",
    ".js", ".ts", ".jsx", ".tsx",
    ".java", ".class",
    ".c", ".cpp", ".cxx", ".h",
    ".cs",
    ".rb",
    ".php", ".php3", ".php4", ".php5",
    ".go",
    ".swift",
    ".kt", ".kts",
    ".scala",
    ".m", ".mm",
    ".rs",
    ".ksh",
    ".r",
    ".pl", ".pm",
    ".sql",
    ".xml", ".json", ".yaml", ".yml"
}



# Only used by downloads from terminal function:
MULTI_EXTS = [".tar.gz", ".tgz"]
SINGLE_EXTS = {".sh", ".bash", ".zsh", ".zip", ".deb", ".rpm", ".pkg", ".out", ".log", ".whl"}

class HelperFunctions():

    @staticmethod
    def move(src: Path, dest: Path, dest_type: str) -> None:
        """
        Moves a file or symlink to the destination folder.
        Uses pretty_unique_path to avoid name collisions.
        """
        # determine workspace (parent directory of the user_folder_copy)
        try:
            # Workspace is /tmp/Foldpro-Workspace* and dest is always /tmp/Foldpro-Workspace*/<user_given_folder_copy>/<a_subfolder>
            # so therefore we can derive the workspace by getting the second parent of dest:
            workspace = dest.parents[1]
            dest = pretty_unique_path(p=(dest / src.name), type=dest_type)
            shutil.move(src, dest)
        except Exception as e:
            raise PartiallyOrganizedError(error_cause = e)


    @staticmethod
    def is_download_from_terminal(p: Path) -> bool:
        if str(p).lower().endswith(tuple(MULTI_EXTS)):
            return True
        if p.suffix.lower() in SINGLE_EXTS:
            return True

        PACKAGE_MANAGER_PATHS = [
            Path("/usr/local/bin"),
            Path("/opt/homebrew/bin"),
            Path.home() / ".cargo" / "bin",
            Path.home() / ".npm",
            Path.home() / ".local" / "bin",
        ]

        HIDDEN_CONFIG_FOLDERS = [
            Path.home() / ".cache",
            Path.home() / ".pip",
            Path.home() / ".npm",
            Path.home() / ".cargo",
            Path.home() / ".config",
        ]

        def is_in_known_dirs(p: Path) -> bool:
            for folder in PACKAGE_MANAGER_PATHS + HIDDEN_CONFIG_FOLDERS:
                if folder in p.parents or folder == p:
                    return True
            return False

        return is_in_known_dirs(p)

    @staticmethod
    def categorize_files_and_symlinks(user_folder_copy: Path) -> Tuple[list[Path], list[Path]]:
        """
        Walk through `user_folder_copy` and return:
        - symlinks
        - regular files

        Directories are ignored.
        """

        symlinks = []
        regular_files = []

        for root, dirs, files in os.walk(user_folder_copy, followlinks=False):
            root_path = Path(root)

            # prevent descending into symlinked directories but store for later reference
            symlinked_dirs = [d for d in dirs if (root_path / d).is_symlink()]
            dirs[:] = [d for d in dirs if d not in symlinked_dirs]

            for name in dirs + files + symlinked_dirs:
                entry = root_path / name

                if entry.is_symlink():
                    symlinks.append(entry)
                    continue

                if entry.is_file():
                    regular_files.append(entry)

        return symlinks, regular_files
    
    
    @staticmethod
    def make_folders(*, folder_names: list[str], parent_path: Path) -> list[Path]:
        '''
        Create the folders Foldpro is going to be organinzing into. Append digits if neccary for making unique path
        '''
        created_paths = []
        for folder_name in folder_names:
            folder_path = pretty_unique_path(p=(parent_path / folder_name), type='folder')
            folder_path.mkdir()
            created_paths.append(folder_path)

        return created_paths




def categorize_item(item: Path, mode: Literal['all', 'c_only', 'd_only', 'p_only', 'o_only'], subfolders: list[Path]) -> Optional[Path]:
    """
    Determine the destination folder for an item based on its extension and the mode.
    Returns None if the item shouldn't be moved in the current mode.
    
    Args:
        item: The file or symlink target to categorize
        mode: The organization mode
        subfolders: [PICTURES, CODE_FILES, DOWNLOADS_FROM_TERMINAL, OTHERS]
    
    Returns:
        Destination Path or None if item shouldn't be moved
    """
    PICTURES, CODE_FILES, DOWNLOADS_FROM_TERMINAL, OTHERS = subfolders
    ALL_EXTENSIONS = IMAGE_EXTENSIONS | CODE_EXTENSIONS
    
    suffix = item.suffix.lower()
    is_image = suffix in IMAGE_EXTENSIONS
    is_code = suffix in CODE_EXTENSIONS
    is_download = HelperFunctions.is_download_from_terminal(item)
    is_other = suffix not in ALL_EXTENSIONS and not is_download
    
    # Mode-specific filtering and categorization
    if mode == 'all':
        if is_image:
            return PICTURES
        elif is_code:
            return CODE_FILES
        elif is_download:
            return DOWNLOADS_FROM_TERMINAL
        else:
            return OTHERS
    
    elif mode == 'p_only':
        return PICTURES if is_image else None
    
    elif mode == 'c_only':
        return CODE_FILES if is_code else None
    
    elif mode == 'd_only':
        return DOWNLOADS_FROM_TERMINAL if is_download else None
    
    elif mode == 'o_only':
        return OTHERS if is_other else None
    
    return None


def organize_symlinks(mode: Literal['all', 'c_only', 'd_only', 'p_only', 'o_only'], symlinks: list[Path], subfolders: list[Path]) -> None:
    """
    Organize symlinks into appropriate folders based on their target's type.
    Broken/non-existent/directory symlinks are treated as 'others'.
    """
    if not symlinks:
        return
    
    PICTURES, CODE_FILES, DOWNLOADS_FROM_TERMINAL, OTHERS = subfolders
    
    # Categorize symlinks
    organizable_symlinks = []  # List of (target, symlink) tuples
    non_organizable = []  # Broken, non-existent, or directory symlinks
    
    for symlink in symlinks:
        try:
            raw_target = Path(os.readlink(symlink))
            target = raw_target if raw_target.is_absolute() else symlink.parent / raw_target
        except (PermissionError, OSError):
            non_organizable.append(symlink)
            continue
        
        try:
            exists = target.exists()
        except OSError:
            exists = False
        
        if target.is_dir() or not exists:
            non_organizable.append(symlink)
        else:
            organizable_symlinks.append((target, symlink))
    
    # Organize symlinks based on their target
    for target, symlink in organizable_symlinks:
        dest = categorize_item(target, mode, subfolders)
        if dest is not None:
            HelperFunctions.move(symlink, dest, 'symlink')
    
    # Handle non-organizable symlinks (only in 'all' or 'o_only' mode)
    if mode in {'all', 'o_only'}:
        for symlink in non_organizable:
            HelperFunctions.move(symlink, OTHERS, 'symlink')


def organize_files(mode: Literal['all', 'c_only', 'd_only', 'p_only', 'o_only'], files: list[Path], subfolders: list[Path]) -> None:
    """
    Organize regular files into appropriate folders based on their extension.
    """
    if not files:
        return
    
    for file in files:
        dest = categorize_item(file, mode, subfolders)
        if dest is not None:
            HelperFunctions.move(src = file, dest = dest, dest_type ='file')


def finalize_state(*, mode: Literal['all', 'c_only', 'd_only', 'p_only', 'o_only'], user_folder_copy: Path, subfolders: list[Optional[Path]]) -> Path:
    '''
    This function does the following:
    - Reverts all modified file names back to their orginal form (or however close to it can without causing collisons)
    - If mode == all, it deletes all empty folders except for the newly created ones(e.g.'Pictures')
    - Moves the now organized folder into its final destination(~/Foldpro-Copies).
    '''
    
    # Delete non-Foldpro folders in 'all' mode
    if mode == 'all':
        keep_names = {f.name for f in subfolders if f}
        for item in user_folder_copy.iterdir():
            if item.is_dir() and item.name not in keep_names:
                shutil.rmtree(item)
    
    # Find or create destination folder
    pattern = re.compile(r'^Foldpro Copies(\d+)?$')
    foldpro_copies = next(
        (f for f in Path.home().iterdir() 
         if f.is_dir() and pattern.match(f.name) and (f / '.YOUFOUNDME').exists()),
        None
    )    

    if not foldpro_copies:
        foldpro_copies = pretty_unique_path(p = (Path.home() / 'Foldpro Copies'), type='folder')
        foldpro_copies.mkdir()
        (foldpro_copies / '.YOUFOUNDME').touch()

    # Move to final destination
    dest = pretty_unique_path((foldpro_copies / user_folder_copy.name), 'folder')  
    try:       
        shutil.move(user_folder_copy, dest)     
    except Exception as e:
        raise NonAtomicMoveError(error_cause=e, dest=dest)
    return dest

MODE_FOLDERS = {
    'all': ['Pictures', 'Code Files', 'Downloads from Terminal', 'Others'],
    'p_only': ['Pictures'],
    'c_only': ['Code Files'],
    'd_only': ['Downloads from Terminal'],
    'o_only': ['Others']
}

def Foldpro_command(*, mode: Literal['all', 'c_only', 'd_only', 'p_only', 'o_only'], user_folder_copy: Path) -> Path:
    '''
    This is a wrapper function that wraps all the functionality for creating a organized folder copy of the user's folder.
    Everything that is executed before it(in in main.py file where it's used), is a prelude to this function.
    '''
    
    # Create folders and pad with None values
    created = HelperFunctions.make_folders(
        folder_names=MODE_FOLDERS[mode],
        parent_path=user_folder_copy
    )
    
    # Unpack with defaults - creates dict and extracts in one go
    folder_names = ['Pictures', 'Code Files', 'Downloads from Terminal', 'Others']
    folder_dict = dict(zip(MODE_FOLDERS[mode], created))
    subfolders = [folder_dict.get(name) for name in folder_names]
    
    # Organize
    symlinks, files = HelperFunctions.categorize_files_and_symlinks(user_folder_copy)
    organize_symlinks(mode, symlinks, subfolders)
    organize_files(mode, files, subfolders)

    # Finalize
    return finalize_state(
        mode=mode,
        user_folder_copy=user_folder_copy,
        subfolders=subfolders
    )
