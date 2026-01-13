""" Data container for File Change information.

**Properties:**
 - before_path (str?): The initial path of the file.
 - before_dir (bool?): Whether the initial file is a directory.
 - after_path (str?): The final path of the file.
 - after_dir (bool?): Whether the final path is a directory.
"""
from collections import namedtuple


FileChange = namedtuple(
    'FileChange',
    field_names=(
        'before_path',
        'before_dir',
        'after_path',
        'after_dir'
    ),
    defaults=(
        None, None, None, None
    ),
)


def create_fc(file_path_str: str) -> FileChange:
    """ Build a FC tuple for a created file.
 - Created File Path is stored in the after_path attribute.

**Parameters:**
 - file_path_str (str): To be stored in FileChange.

**Returns:**
 FileChange - The tuple representing a Created FileChange.
    """
    return FileChange(None, None, file_path_str, False)


def update_fc(file_path_str: str) -> FileChange:
    """ Build a FC tuple for an updated file.
 - Updated Files contain a before and after path. If they don't match, it's a move-update.

**Parameters:**
 - file_path_str (str): To be stored in FileChange.

**Returns:**
 FileChange - The tuple representing an Update FileChange.
    """
    return FileChange(file_path_str, False, file_path_str, False)


def delete_fc(file_path_str: str) -> FileChange:
    """ Build a FC tuple for a deleted file.
 - Deleted File Path is stored in the before_path attribute.

**Parameters:**
 - file_path_str (str): To be stored in FileChange.

**Returns:**
 FileChange - The tuple representing a Delete FileChange.
    """
    return FileChange(file_path_str, False, None, None)


def move_fc(before: str, after: str) -> FileChange:
    """ Build a FC tuple for a moved file.
 - Move Files contain a before and after path.

**Parameters:**
 - before (str): Initial file path string to be stored in FileChange.
 - after (str): Updated file path string to be stored in FileChange.

**Returns:**
 FileChange - The tuple representing a Moved FileChange.
    """
    return FileChange(before, False, after, False)
