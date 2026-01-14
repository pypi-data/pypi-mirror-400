"""

        Container classes and data structures for Open Space Toolkit.

        This submodule provides generic container classes including Object, Dictionary,
        and Array types for storing and manipulating structured data.
    
"""
from __future__ import annotations
import ostk.core.filesystem
import ostk.core.type
import typing
__all__ = ['Dictionary', 'Object', 'get_double_array', 'get_int_array', 'get_integer_array', 'get_real_array', 'get_string_array', 'set_double_array', 'set_int_array', 'set_integer_array', 'set_real_array', 'set_string_array']
class Dictionary:
    class ConstIterator:
        __hash__: typing.ClassVar[None] = None
        def __eq__(self, arg0: Dictionary.ConstIterator) -> bool:
            ...
        def __ne__(self, arg0: Dictionary.ConstIterator) -> bool:
            ...
        def access_key(self) -> ostk.core.type.String:
            ...
        def access_value(self) -> Object:
            ...
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def empty() -> Dictionary:
        ...
    @staticmethod
    def parse(string: ostk.core.type.String, format: Object.Format) -> Dictionary:
        ...
    def __bool__(self) -> bool:
        ...
    def __contains__(self, arg0: ostk.core.type.String) -> bool:
        ...
    def __eq__(self, arg0: Dictionary) -> bool:
        ...
    def __getitem__(self, arg0: ostk.core.type.String) -> Object:
        ...
    def __init__(self, arg0: dict) -> None:
        ...
    def __iter__(self) -> typing.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: Dictionary) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def add_value_for_key(self, value: Object, key: ostk.core.type.String) -> None:
        ...
    def get_size(self) -> int:
        ...
    def has_value_for_key(self, key: ostk.core.type.String) -> bool:
        ...
    def is_empty(self) -> bool:
        ...
class Object:
    class Format:
        """
        
                Enumeration of Object serialization formats.
        
                Defines the supported formats for serializing/deserializing Objects.
            
        
        Members:
        
          Undefined : Undefined format
        
          JSON : JSON format
        
          YAML : YAML format
        """
        JSON: typing.ClassVar[Object.Format]  # value = <Format.JSON: 1>
        Undefined: typing.ClassVar[Object.Format]  # value = <Format.Undefined: 0>
        YAML: typing.ClassVar[Object.Format]  # value = <Format.YAML: 2>
        __members__: typing.ClassVar[dict[str, Object.Format]]  # value = {'Undefined': <Format.Undefined: 0>, 'JSON': <Format.JSON: 1>, 'YAML': <Format.YAML: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class Type:
        """
        
                Enumeration of Object types.
        
                Defines the different types that an Object can represent.
            
        
        Members:
        
          Undefined : Undefined object type
        
          Boolean : Boolean object type
        
          Integer : Integer object type
        
          Real : Real number object type
        
          String : String object type
        
          Dictionary : Dictionary object type
        
          Array : Array object type
        """
        Array: typing.ClassVar[Object.Type]  # value = <Type.Array: 6>
        Boolean: typing.ClassVar[Object.Type]  # value = <Type.Boolean: 1>
        Dictionary: typing.ClassVar[Object.Type]  # value = <Type.Dictionary: 5>
        Integer: typing.ClassVar[Object.Type]  # value = <Type.Integer: 2>
        Real: typing.ClassVar[Object.Type]  # value = <Type.Real: 3>
        String: typing.ClassVar[Object.Type]  # value = <Type.String: 4>
        Undefined: typing.ClassVar[Object.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Object.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Boolean': <Type.Boolean: 1>, 'Integer': <Type.Integer: 2>, 'Real': <Type.Real: 3>, 'String': <Type.String: 4>, 'Dictionary': <Type.Dictionary: 5>, 'Array': <Type.Array: 6>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def array(array: list[Object]) -> Object:
        """
                        Create an Object containing an array.
        
                        Args:
                            array (Array): The array.
        
                        Returns:
                            Object: An object containing the array.
        """
    @staticmethod
    def boolean(boolean: bool) -> Object:
        """
                        Create an Object containing a boolean value.
        
                        Args:
                            boolean (bool): The boolean value.
        
                        Returns:
                            Object: An object containing the boolean.
        """
    @staticmethod
    def dictionary(dictionary: Dictionary) -> Object:
        """
                        Create an Object containing a dictionary.
        
                        Args:
                            dictionary (Dictionary): The dictionary.
        
                        Returns:
                            Object: An object containing the dictionary.
        """
    @staticmethod
    def integer(integer: ostk.core.type.Integer) -> Object:
        """
                        Create an Object containing an integer value.
        
                        Args:
                            integer (Integer): The integer value.
        
                        Returns:
                            Object: An object containing the integer.
        """
    @staticmethod
    def load(file: ostk.core.filesystem.File, format: Object.Format) -> Object:
        """
                        Load an Object from a file.
        
                        Args:
                            file (File): The file to load from.
                            format (Object.Format): The format of the file content.
        
                        Returns:
                            Object: The loaded object.
        
                        Raises:
                            RuntimeError: If the file cannot be loaded or parsed.
        """
    @staticmethod
    def parse(string: ostk.core.type.String, format: Object.Format) -> Object:
        """
                        Parse a string as an Object.
        
                        Args:
                            string (str): The string to parse.
                            format (Object.Format): The format of the string (JSON or YAML).
        
                        Returns:
                            Object: The parsed object.
        
                        Raises:
                            RuntimeError: If the string cannot be parsed.
        """
    @staticmethod
    def real(real: ostk.core.type.Real) -> Object:
        """
                        Create an Object containing a real number value.
        
                        Args:
                            real (Real): The real number value.
        
                        Returns:
                            Object: An object containing the real number.
        """
    @staticmethod
    def string(string: ostk.core.type.String) -> Object:
        """
                        Create an Object containing a string value.
        
                        Args:
                            string (String): The string value.
        
                        Returns:
                            Object: An object containing the string.
        """
    @staticmethod
    def string_from_type(type: Object.Type) -> ostk.core.type.String:
        """
                        Get string representation of an Object type.
        
                        Args:
                            type (Object.Type): The object type.
        
                        Returns:
                            str: String representation of the type.
        """
    @staticmethod
    def type_from_string(string: ostk.core.type.String) -> Object.Type:
        """
                        Get Object type from string representation.
        
                        Args:
                            string (str): String representation of the type.
        
                        Returns:
                            Object.Type: The object type.
        """
    @staticmethod
    def undefined() -> Object:
        """
                        Create an undefined Object.
        
                        Returns:
                            Object: An undefined object.
        """
    def __eq__(self, arg0: Object) -> bool:
        """
        Check if two Objects are equal.
        """
    @typing.overload
    def __getitem__(self, key: ostk.core.type.String) -> Object:
        """
                        Access object element by string key (for dictionaries).
        
                        Args:
                            key (str): The key to access.
        
                        Returns:
                            Object: The object at the specified key.
        """
    @typing.overload
    def __getitem__(self, index: int) -> Object:
        """
                        Access object element by index (for arrays).
        
                        Args:
                            index (int): The index to access.
        
                        Returns:
                            Object: The object at the specified index.
        """
    def __ne__(self, arg0: Object) -> bool:
        """
        Check if two Objects are not equal.
        """
    def __repr__(self) -> str:
        """
                        Return JSON string representation of the Object for debugging.
        
                        Returns:
                            str: JSON representation of the object.
        """
    def __str__(self) -> str:
        """
                        Return JSON string representation of the Object.
        
                        Returns:
                            str: JSON representation of the object.
        """
    def get_array(self) -> list[Object]:
        """
                        Get the array from the Object.
        
                        Returns:
                            Array: The array value.
        
                        Raises:
                            RuntimeError: If the object is not an array.
        """
    def get_boolean(self) -> bool:
        """
                        Get the boolean value from the Object.
        
                        Returns:
                            bool: The boolean value.
        
                        Raises:
                            RuntimeError: If the object is not a boolean.
        """
    def get_dictionary(self) -> Dictionary:
        """
                        Get the dictionary from the Object.
        
                        Returns:
                            Dictionary: The dictionary value.
        
                        Raises:
                            RuntimeError: If the object is not a dictionary.
        """
    def get_integer(self) -> ostk.core.type.Integer:
        """
                        Get the integer value from the Object.
        
                        Returns:
                            Integer: The integer value.
        
                        Raises:
                            RuntimeError: If the object is not an integer.
        """
    def get_real(self) -> ostk.core.type.Real:
        """
                        Get the real number value from the Object.
        
                        Returns:
                            Real: The real number value.
        
                        Raises:
                            RuntimeError: If the object is not a real number.
        """
    def get_string(self) -> ostk.core.type.String:
        """
                        Get the string value from the Object.
        
                        Returns:
                            String: The string value.
        
                        Raises:
                            RuntimeError: If the object is not a string.
        """
    def get_type(self) -> Object.Type:
        """
                        Get the type of the Object.
        
                        Returns:
                            Object.Type: The type of the object.
        """
    def is_array(self) -> bool:
        """
                        Check if the Object contains an array.
        
                        Returns:
                            bool: True if the object is an array, False otherwise.
        """
    def is_boolean(self) -> bool:
        """
                        Check if the Object contains a boolean value.
        
                        Returns:
                            bool: True if the object is a boolean, False otherwise.
        """
    def is_defined(self) -> bool:
        """
                        Check if the Object is defined.
        
                        Returns:
                            bool: True if the object is defined, False otherwise.
        """
    def is_dictionary(self) -> bool:
        """
                        Check if the Object contains a dictionary.
        
                        Returns:
                            bool: True if the object is a dictionary, False otherwise.
        """
    def is_integer(self) -> bool:
        """
                        Check if the Object contains an integer value.
        
                        Returns:
                            bool: True if the object is an integer, False otherwise.
        """
    def is_real(self) -> bool:
        """
                        Check if the Object contains a real number value.
        
                        Returns:
                            bool: True if the object is a real number, False otherwise.
        """
    def is_string(self) -> bool:
        """
                        Check if the Object contains a string value.
        
                        Returns:
                            bool: True if the object is a string, False otherwise.
        """
    def to_string(self, format: Object.Format) -> ostk.core.type.String:
        """
                        Convert the Object to a string representation.
        
                        Args:
                            format (Object.Format): The output format (JSON or YAML).
        
                        Returns:
                            str: String representation of the object.
        """
def get_double_array() -> list[float]:
    ...
def get_int_array() -> list[int]:
    ...
def get_integer_array() -> list[ostk.core.type.Integer]:
    ...
def get_real_array() -> list[ostk.core.type.Real]:
    ...
def get_string_array() -> list[ostk.core.type.String]:
    ...
def set_double_array(arg0: list[float]) -> None:
    ...
def set_int_array(arg0: list[int]) -> None:
    ...
def set_integer_array(arg0: list[ostk.core.type.Integer]) -> None:
    ...
def set_real_array(arg0: list[ostk.core.type.Real]) -> None:
    ...
def set_string_array(arg0: list[ostk.core.type.String]) -> None:
    ...
