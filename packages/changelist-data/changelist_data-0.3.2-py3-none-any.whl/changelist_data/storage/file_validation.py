""" File Validation Methods.
"""
from pathlib import Path

from changelist_data.storage.storage_type import StorageType, get_default_path


_FILE_SIZE_LIMIT = 8 * 1024**2 # 8 MB
_FILE_SIZE_LIMIT_EXCEEDED_MSG = "Input File was larger than 8 MB."


def file_exists(
    path: Path,
) -> bool:
    """ Determines if Path exists and is_file.

**Parameters:**
 - path (Path): The path to check.

**Returns:**
 bool - Whether the file exists.
    """
    return path.exists() and path.is_file()


def check_if_default_file_exists(
    option: StorageType,
) -> Path | None:
    """ Return the Path to the default file for this storage option iff it exists.

**Parameters:**
 - option (StorageType): The StorageType option to check.

**Returns:**
 Path? - The Path to the Default Storage File, or None if the path is not a file that exists.
    """
    if file_exists(file_path := get_default_path(option)):
        return file_path
    return None


def validate_file_input_text(
    file_path: Path,
) -> str:
    """ Ensure that the File Exists, and is within reasonable size parameters.
 - Read the File and return its string contents.
 - Refuses to read files larger than 8 MB.

**Parameters:**
 - file_path (Path): The Path to the Input File.

**Returns:**
 str - The Text Contents of the Input File.

**Raises:**
 SystemExit - When any of the validation conditions fails, or the file operation fails.
    """
    try:
        if not file_path.exists():
            exit("File did not exist.")
        if not file_path.is_file():
            exit("Given Path was not a file.")
        if file_path.stat().st_size > _FILE_SIZE_LIMIT:
            exit(_FILE_SIZE_LIMIT_EXCEEDED_MSG)
        return file_path.read_text()
    except UnicodeError:
        exit("File is not valid text. Unicode error.")
    except OSError:
        exit("OSError occurred while reading Input File.")
    except Exception as e:
        exit(f"Unexpected Exception while reading InputFile(name={file_path.name}) Exception=({e}).")
