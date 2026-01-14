"""

        File system operations and utilities for Open Space Toolkit.

        This submodule provides classes for working with files, directories, paths,
        and permission sets, enabling cross-platform file system operations.
    
"""
from __future__ import annotations
import ostk.core.type
import typing
__all__ = ['Directory', 'File', 'Path', 'PermissionSet']
class Directory:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def path(path: Path) -> Directory:
        """
                        Create a Directory from a path.
        
                        Args:
                            path (Path): The path to the directory.
        
                        Returns:
                            Directory: A Directory object representing the specified path.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> path = Path.parse("/home/user")
                            >>> directory = Directory.path(path)
        """
    @staticmethod
    def root() -> Directory:
        """
                        Get the root directory of the filesystem.
        
                        Returns:
                            Directory: The root directory ("/" on Unix systems).
        
                        Example:
                            >>> root = Directory.root()
                            >>> root.get_name()  # "/"
        """
    @staticmethod
    def undefined() -> Directory:
        """
                        Create an undefined Directory.
        
                        Returns:
                            Directory: An undefined Directory object.
        
                        Example:
                            >>> undefined_dir = Directory.undefined()
                            >>> undefined_dir.is_defined()  # False
        """
    def __eq__(self, arg0: Directory) -> bool:
        """
        Check if two Directories are equal.
        """
    def __ne__(self, arg0: Directory) -> bool:
        """
        Check if two Directories are not equal.
        """
    def __repr__(self) -> str:
        """
        Return string representation of the Directory for debugging.
        """
    def __str__(self) -> str:
        """
        Return string representation of the Directory.
        """
    def contains_file_with_name(self, name: ostk.core.type.String) -> bool:
        """
                        Check if the Directory contains a file with the specified name.
        
                        Args:
                            name (str): The name of the file to search for.
        
                        Returns:
                            bool: True if a file with the given name exists in the directory.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user"))
                            >>> directory.contains_file_with_name("document.txt")  # True/False
        """
    def create(self, owner_permissions: PermissionSet = ..., group_permissions: PermissionSet = ..., other_permissions: PermissionSet = ...) -> None:
        """
                        Create the Directory on the filesystem.
        
                        Creates the directory and any necessary parent directories.
        
                        Args:
                            owner_permissions (PermissionSet, optional): Permissions for the owner.
                                Defaults to PermissionSet.rwx().
                            group_permissions (PermissionSet, optional): Permissions for the group.
                                Defaults to PermissionSet.rx().
                            other_permissions (PermissionSet, optional): Permissions for others.
                                Defaults to PermissionSet.rx().
        
                        Raises:
                            RuntimeError: If the directory cannot be created.
        
                        Example:
                            >>> from ostk.core.filesystem import Path, PermissionSet
                            >>> directory = Directory.path(Path.parse("/tmp/new_directory"))
                            >>> directory.create()  # Uses default permissions
                            >>> directory.create(PermissionSet.rwx(), PermissionSet.rx(), PermissionSet.none())
        """
    def exists(self) -> bool:
        """
                        Check if the Directory exists on the filesystem.
        
                        Returns:
                            bool: True if the directory exists, False otherwise.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home"))
                            >>> directory.exists()  # True (usually)
        """
    def get_directories(self) -> list[Directory]:
        """
                        Get all subdirectories in this Directory.
        
                        Returns:
                            list[Directory]: A list of subdirectories.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user"))
                            >>> subdirs = directory.get_directories()
        """
    def get_name(self) -> ostk.core.type.String:
        """
                        Get the name of the Directory.
        
                        Returns:
                            str: The directory name (last component of the path).
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user/Documents"))
                            >>> directory.get_name()  # "Documents"
        """
    def get_parent_directory(self) -> Directory:
        """
                        Get the parent directory of this Directory.
        
                        Returns:
                            Directory: The parent directory.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user/Documents"))
                            >>> parent = directory.get_parent_directory()
                            >>> parent.get_name()  # "user"
        """
    def get_path(self) -> Path:
        """
                        Get the full path of the Directory.
        
                        Returns:
                            Path: The complete path to the directory.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user"))
                            >>> path = directory.get_path()
                            >>> str(path)  # "/home/user"
        """
    def is_defined(self) -> bool:
        """
                        Check if the Directory is defined.
        
                        Returns:
                            bool: True if the Directory is defined, False otherwise.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user"))
                            >>> directory.is_defined()  # True
        """
    def is_empty(self) -> bool:
        """
                        Check if the Directory is empty.
        
                        Returns:
                            bool: True if the directory contains no files or subdirectories, False otherwise.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/tmp"))
                            >>> directory.is_empty()  # Depends on contents
        """
    def remove(self) -> None:
        """
                        Remove the Directory from the filesystem.
        
                        Removes the directory and all its contents recursively.
        
                        Raises:
                            RuntimeError: If the directory cannot be removed.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/tmp/temp_directory"))
                            >>> directory.remove()
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Convert the Directory to a string representation.
        
                        Returns:
                            str: String representation of the directory path.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> directory = Directory.path(Path.parse("/home/user"))
                            >>> directory.to_string()  # "/home/user"
        """
class File:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def path(path: Path) -> File:
        """
                        Create a File from a file path.
        
                        Args:
                            path (Path): The path to the file.
        
                        Returns:
                            File: A File object representing the specified path.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> path = Path.parse("/home/user/document.txt")
                            >>> file = File.path(path)
                            >>> file.get_name()  # "document.txt"
        """
    @staticmethod
    def undefined() -> File:
        """
                        Create an undefined File.
        
                        Returns:
                            File: An undefined File object.
        
                        Example:
                            >>> undefined_file = File.undefined()
                            >>> undefined_file.is_defined()  # False
        """
    def __eq__(self, arg0: File) -> bool:
        """
        Check if two Files are equal.
        """
    def __ne__(self, arg0: File) -> bool:
        """
        Check if two Files are not equal.
        """
    def __repr__(self) -> str:
        """
        Return string representation of the File for debugging.
        """
    def __str__(self) -> str:
        """
        Return string representation of the File.
        """
    def create(self, owner_permissions: PermissionSet = ..., group_permissions: PermissionSet = ..., other_permissions: PermissionSet = ...) -> None:
        """
                        Create the File on the filesystem.
        
                        Creates the file if it doesn't exist, including any necessary parent directories.
        
                        Args:
                            owner_permissions (PermissionSet, optional): Permissions for the owner.
                                Defaults to PermissionSet.rw().
                            group_permissions (PermissionSet, optional): Permissions for the group.
                                Defaults to PermissionSet.r().
                            other_permissions (PermissionSet, optional): Permissions for others.
                                Defaults to PermissionSet.r().
        
                        Raises:
                            RuntimeError: If the file cannot be created.
        
                        Example:
                            >>> from ostk.core.filesystem import Path, PermissionSet
                            >>> file = File.path(Path.parse("/tmp/new_file.txt"))
                            >>> file.create()  # Uses default permissions
                            >>> file.create(PermissionSet.rw(), PermissionSet.r(), PermissionSet.none())
        """
    def exists(self) -> bool:
        """
                        Check if the File exists on the filesystem.
        
                        Returns:
                            bool: True if the file exists, False otherwise.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/etc/passwd"))
                            >>> file.exists()  # True (on Unix systems)
                            >>> nonexistent = File.path(Path.parse("/nonexistent/file.txt"))
                            >>> nonexistent.exists()  # False
        """
    def get_contents(self) -> ostk.core.type.String:
        """
                        Get the contents of the File as a string.
        
                        Returns:
                            str: The file contents.
        
                        Raises:
                            RuntimeError: If the file cannot be read or doesn't exist.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/path/to/text_file.txt"))
                            >>> content = file.get_contents()
                            >>> print(content)  # File contents as string
        """
    def get_extension(self) -> ostk.core.type.String:
        """
                        Get the file extension.
        
                        Returns:
                            str: The file extension (without the dot).
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/path/to/document.pdf"))
                            >>> file.get_extension()  # "pdf"
                            >>> file_no_ext = File.path(Path.parse("/path/to/README"))
                            >>> file_no_ext.get_extension()  # ""
        """
    def get_name(self, with_extension: bool = True) -> ostk.core.type.String:
        """
                        Get the name of the File.
        
                        Args:
                            with_extension (bool, optional): Whether to include the file extension. Defaults to True.
        
                        Returns:
                            str: The file name, with or without extension.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/path/to/document.pdf"))
                            >>> file.get_name()  # "document.pdf"
                            >>> file.get_name(with_extension=False)  # "document"
        """
    def get_parent_directory(self) -> Directory:
        """
                        Get the parent directory of the File.
        
                        Returns:
                            Directory: The parent directory containing this file.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/home/user/document.txt"))
                            >>> parent = file.get_parent_directory()
                            >>> str(parent.get_path())  # "/home/user"
        """
    def get_path(self) -> Path:
        """
                        Get the full path of the File.
        
                        Returns:
                            Path: The complete path to the file.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/home/user/document.txt"))
                            >>> path = file.get_path()
                            >>> str(path)  # "/home/user/document.txt"
        """
    def get_permissions(self) -> PermissionSet:
        """
                        Get the file permissions.
        
                        Returns:
                            PermissionSet: The permission set for the file.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/etc/passwd"))
                            >>> permissions = file.get_permissions()
        """
    def is_defined(self) -> bool:
        """
                        Check if the File is defined.
        
                        Returns:
                            bool: True if the File is defined, False otherwise.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/path/to/file.txt"))
                            >>> file.is_defined()  # True
                            >>> undefined_file = File.undefined()
                            >>> undefined_file.is_defined()  # False
        """
    def move_to_directory(self, directory: Directory) -> None:
        """
                        Move the File to a different directory.
        
                        Args:
                            directory (Directory): The target directory to move the file to.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/tmp/document.txt"))
                            >>> target_dir = Directory.path(Path.parse("/home/user/Documents"))
                            >>> file.move_to_directory(target_dir)
        """
    def remove(self) -> None:
        """
                        Remove the File from the filesystem.
        
                        Deletes the file if it exists.
        
                        Raises:
                            RuntimeError: If the file cannot be removed.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/tmp/temp_file.txt"))
                            >>> file.remove()
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Convert the File to a string representation.
        
                        Returns:
                            str: String representation of the file path.
        
                        Example:
                            >>> from ostk.core.filesystem import Path
                            >>> file = File.path(Path.parse("/home/user/document.txt"))
                            >>> file.to_string()  # "/home/user/document.txt"
        """
class Path:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def current() -> Path:
        """
                        Get the current working directory path.
        
                        Returns:
                            Path: The current working directory.
        
                        Example:
                            >>> current = Path.current()
                            >>> print(current)  # Current working directory
        """
    @staticmethod
    def parse(path_string: ostk.core.type.String) -> Path:
        """
                        Parse a string as a Path.
        
                        Args:
                            path_string (str): The path string to parse.
        
                        Returns:
                            Path: The parsed Path object.
        
                        Example:
                            >>> path = Path.parse("/home/user/documents")
                            >>> path = Path.parse("relative/path")
        """
    @staticmethod
    def root() -> Path:
        """
                        Get the root path of the filesystem.
        
                        Returns:
                            Path: The root path ("/" on Unix systems).
        
                        Example:
                            >>> root = Path.root()
                            >>> str(root)  # "/"
        """
    @staticmethod
    def undefined() -> Path:
        """
                        Create an undefined Path.
        
                        Returns:
                            Path: An undefined Path object.
        
                        Example:
                            >>> undefined_path = Path.undefined()
                            >>> undefined_path.is_defined()  # False
        """
    def __add__(self, arg0: Path) -> Path:
        """
        Concatenate two Paths.
        """
    def __eq__(self, arg0: Path) -> bool:
        """
        Check if two Paths are equal.
        """
    def __iadd__(self, arg0: Path) -> Path:
        """
        Append another Path to this one in-place.
        """
    def __ne__(self, arg0: Path) -> bool:
        """
        Check if two Paths are not equal.
        """
    def __repr__(self) -> str:
        """
        Return string representation of the Path for debugging.
        """
    def __str__(self) -> str:
        """
        Return string representation of the Path.
        """
    def get_absolute_path(self, base_path: Path = ...) -> Path:
        """
                        Get an absolute version of the Path.
        
                        Args:
                            base_path (Path, optional): The base path to resolve against. Defaults to current directory.
        
                        Returns:
                            Path: The absolute path.
        
                        Example:
                            >>> relative_path = Path.parse("documents/file.txt")
                            >>> absolute = relative_path.get_absolute_path()
        """
    def get_last_element(self) -> ostk.core.type.String:
        """
                        Get the last element (filename or directory name) of the path.
        
                        Returns:
                            str: The last component of the path.
        
                        Example:
                            >>> path = Path.parse("/home/user/document.txt")
                            >>> path.get_last_element()  # "document.txt"
        """
    def get_normalized_path(self) -> Path:
        """
                        Get a normalized version of the Path.
        
                        Resolves "." and ".." components and removes redundant separators.
        
                        Returns:
                            Path: The normalized path.
        
                        Example:
                            >>> path = Path.parse("/home/user/../user/./documents")
                            >>> normalized = path.get_normalized_path()
                            >>> str(normalized)  # "/home/user/documents"
        """
    def get_parent_path(self) -> Path:
        """
                        Get the parent path.
        
                        Returns:
                            Path: The parent path.
        
                        Example:
                            >>> path = Path.parse("/home/user/documents")
                            >>> parent = path.get_parent_path()
                            >>> str(parent)  # "/home/user"
        """
    def is_absolute(self) -> bool:
        """
                        Check if the Path is absolute.
        
                        Returns:
                            bool: True if the path is absolute (starts from root), False otherwise.
        
                        Example:
                            >>> Path.parse("/home/user").is_absolute()  # True
                            >>> Path.parse("user/documents").is_absolute()  # False
        """
    def is_defined(self) -> bool:
        """
                        Check if the Path is defined.
        
                        Returns:
                            bool: True if the Path is defined, False otherwise.
        
                        Example:
                            >>> path = Path.parse("/home/user")
                            >>> path.is_defined()  # True
        """
    def is_relative(self) -> bool:
        """
                        Check if the Path is relative.
        
                        Returns:
                            bool: True if the path is relative, False otherwise.
        
                        Example:
                            >>> Path.parse("user/documents").is_relative()  # True
                            >>> Path.parse("/home/user").is_relative()  # False
        """
    def to_string(self) -> ostk.core.type.String:
        """
                        Convert the Path to a string representation.
        
                        Returns:
                            str: String representation of the path.
        
                        Example:
                            >>> path = Path.parse("/home/user")
                            >>> path.to_string()  # "/home/user"
        """
class PermissionSet:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def none() -> PermissionSet:
        """
                        Create a PermissionSet with no permissions.
        
                        Returns:
                            PermissionSet: A permission set with no permissions granted.
        
                        Example:
                            >>> perm = PermissionSet.none()
                            >>> perm.is_none()  # True
        """
    @staticmethod
    def r() -> PermissionSet:
        """
                        Create a PermissionSet with read permission only.
        
                        Returns:
                            PermissionSet: A permission set with read permission.
        
                        Example:
                            >>> perm = PermissionSet.r()
                            >>> perm.can_read()  # True
                            >>> perm.can_write()  # False
        """
    @staticmethod
    def rw() -> PermissionSet:
        """
                        Create a PermissionSet with read and write permissions.
        
                        Returns:
                            PermissionSet: A permission set with read and write permissions.
        
                        Example:
                            >>> perm = PermissionSet.rw()
                            >>> perm.can_read()  # True
                            >>> perm.can_write()  # True
                            >>> perm.can_execute()  # False
        """
    @staticmethod
    def rwx() -> PermissionSet:
        """
                        Create a PermissionSet with all permissions (read, write, execute).
        
                        Returns:
                            PermissionSet: A permission set with all permissions.
        
                        Example:
                            >>> perm = PermissionSet.rwx()
                            >>> perm.is_all()  # True
        """
    @staticmethod
    def rx() -> PermissionSet:
        """
                        Create a PermissionSet with read and execute permissions.
        
                        Returns:
                            PermissionSet: A permission set with read and execute permissions.
        
                        Example:
                            >>> perm = PermissionSet.rx()
                            >>> perm.can_read()  # True
                            >>> perm.can_execute()  # True
                            >>> perm.can_write()  # False
        """
    @staticmethod
    def w() -> PermissionSet:
        """
                        Create a PermissionSet with write permission only.
        
                        Returns:
                            PermissionSet: A permission set with write permission.
        
                        Example:
                            >>> perm = PermissionSet.w()
                            >>> perm.can_write()  # True
        """
    @staticmethod
    def x() -> PermissionSet:
        """
                        Create a PermissionSet with execute permission only.
        
                        Returns:
                            PermissionSet: A permission set with execute permission.
        
                        Example:
                            >>> perm = PermissionSet.x()
                            >>> perm.can_execute()  # True
        """
    def __add__(self, arg0: PermissionSet) -> PermissionSet:
        """
        Combine two PermissionSets (union of permissions).
        """
    def __eq__(self, arg0: PermissionSet) -> bool:
        """
        Check if two PermissionSets are equal.
        """
    def __init__(self, can_read: bool, can_write: bool, can_execute: bool) -> None:
        """
                        Construct a PermissionSet with specific read, write, and execute permissions.
        
                        Args:
                            can_read (bool): Whether read permission is granted.
                            can_write (bool): Whether write permission is granted.
                            can_execute (bool): Whether execute permission is granted.
        
                        Example:
                            >>> perm = PermissionSet(True, False, True)  # read and execute only
                            >>> perm.can_read()  # True
                            >>> perm.can_write()  # False
        """
    def __ne__(self, arg0: PermissionSet) -> bool:
        """
        Check if two PermissionSets are not equal.
        """
    def __repr__(self) -> str:
        """
        Return string representation of the PermissionSet for debugging.
        """
    def __str__(self) -> str:
        """
        Return string representation of the PermissionSet.
        """
    def __sub__(self, arg0: PermissionSet) -> PermissionSet:
        """
        Remove permissions (subtract permissions).
        """
    def can_execute(self) -> bool:
        """
                        Check if execute permission is granted.
        
                        Returns:
                            bool: True if execute permission is granted.
        
                        Example:
                            >>> perm = PermissionSet.x()
                            >>> perm.can_execute()  # True
        """
    def can_read(self) -> bool:
        """
                        Check if read permission is granted.
        
                        Returns:
                            bool: True if read permission is granted.
        
                        Example:
                            >>> perm = PermissionSet.r()
                            >>> perm.can_read()  # True
        """
    def can_write(self) -> bool:
        """
                        Check if write permission is granted.
        
                        Returns:
                            bool: True if write permission is granted.
        
                        Example:
                            >>> perm = PermissionSet.w()
                            >>> perm.can_write()  # True
        """
    def is_all(self) -> bool:
        """
                        Check if all permissions are granted.
        
                        Returns:
                            bool: True if all permissions (read, write, execute) are granted.
        
                        Example:
                            >>> perm = PermissionSet.rwx()
                            >>> perm.is_all()  # True
        """
    def is_none(self) -> bool:
        """
                        Check if no permissions are granted.
        
                        Returns:
                            bool: True if no permissions (read, write, execute) are granted.
        
                        Example:
                            >>> perm = PermissionSet.none()
                            >>> perm.is_none()  # True
        """
