"""

        Core data types for Open Space Toolkit.

        This submodule contains fundamental data types including Integer, Real, String,
        and Sign enumerations that provide enhanced functionality over standard types.
    
"""
from __future__ import annotations
import typing
__all__ = ['Integer', 'Negative', 'NoSign', 'Positive', 'Real', 'Sign', 'String', 'Undefined']
class Integer:
    @staticmethod
    def can_parse(string: String) -> bool:
        """
                        Check if a string can be parsed as an Integer.
        
                        Args:
                            string (str): The string to check.
        
                        Returns:
                            bool: True if the string can be parsed as an Integer, False otherwise.
        
                        Example:
                            >>> Integer.can_parse("42")  # True
                            >>> Integer.can_parse("not_a_number")  # False
        """
    @staticmethod
    def index(index: int) -> Integer:
        """
                        Create an Integer from an index value.
        
                        Args:
                            index: The index value to convert.
        
                        Returns:
                            Integer: An Integer representing the index.
        
                        Example:
                            >>> index_val = Integer.index(42)
        """
    @staticmethod
    def int16(value: int) -> Integer:
        """
                        Create an Integer from a 16-bit signed integer value.
        
                        Args:
                            value (int): The 16-bit signed integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> int16_val = Integer.int16(32767)
        """
    @staticmethod
    def int32(value: int) -> Integer:
        """
                        Create an Integer from a 32-bit signed integer value.
        
                        Args:
                            value (int): The 32-bit signed integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> int32_val = Integer.int32(2147483647)
        """
    @staticmethod
    def int64(value: int) -> Integer:
        """
                        Create an Integer from a 64-bit signed integer value.
        
                        Args:
                            value (int): The 64-bit signed integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> int64_val = Integer.int64(9223372036854775807)
        """
    @staticmethod
    def int8(value: int) -> Integer:
        """
                        Create an Integer from an 8-bit signed integer value.
        
                        Args:
                            value (int): The 8-bit signed integer value (-128 to 127).
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> int8_val = Integer.int8(127)
        """
    @staticmethod
    def negative_infinity() -> Integer:
        """
                        Create an Integer representing negative infinity.
        
                        Returns:
                            Integer: An Integer with value -∞.
        
                        Example:
                            >>> neg_inf = Integer.negative_infinity()
                            >>> neg_inf.is_negative_infinity()  # True
        """
    @staticmethod
    def parse(string: String) -> Integer:
        """
                        Parse a string as an Integer.
        
                        Args:
                            string (str): The string to parse.
        
                        Returns:
                            Integer: The parsed Integer.
        
                        Raises:
                            RuntimeError: If the string cannot be parsed as an Integer.
        
                        Example:
                            >>> integer = Integer.parse("42")
                            >>> integer = Integer.parse("-123")
        """
    @staticmethod
    def positive_infinity() -> Integer:
        """
                        Create an Integer representing positive infinity.
        
                        Returns:
                            Integer: An Integer with value +∞.
        
                        Example:
                            >>> pos_inf = Integer.positive_infinity()
                            >>> pos_inf.is_positive_infinity()  # True
        """
    @staticmethod
    def size(size: int) -> Integer:
        """
                        Create an Integer from a size value.
        
                        Args:
                            size: The size value to convert.
        
                        Returns:
                            Integer: An Integer representing the size.
        
                        Example:
                            >>> size_val = Integer.size(100)
        """
    @staticmethod
    def uint16(value: int) -> Integer:
        """
                        Create an Integer from a 16-bit unsigned integer value.
        
                        Args:
                            value (int): The 16-bit unsigned integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> uint16_val = Integer.uint16(65535)
        """
    @staticmethod
    def uint32(value: int) -> Integer:
        """
                        Create an Integer from a 32-bit unsigned integer value.
        
                        Args:
                            value (int): The 32-bit unsigned integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> uint32_val = Integer.uint32(4294967295)
        """
    @staticmethod
    def uint64(value: int) -> Integer:
        """
                        Create an Integer from a 64-bit unsigned integer value.
        
                        Args:
                            value (int): The 64-bit unsigned integer value.
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> uint64_val = Integer.uint64(18446744073709551615)
        """
    @staticmethod
    def uint8(value: int) -> Integer:
        """
                        Create an Integer from an 8-bit unsigned integer value.
        
                        Args:
                            value (int): The 8-bit unsigned integer value (0 to 255).
        
                        Returns:
                            Integer: An Integer with the specified value.
        
                        Example:
                            >>> uint8_val = Integer.uint8(255)
        """
    @staticmethod
    def undefined() -> Integer:
        """
                        Create an undefined Integer.
        
                        Returns:
                            Integer: An undefined Integer.
        
                        Example:
                            >>> undefined_int = Integer.undefined()
                            >>> undefined_int.is_defined()  # False
        """
    @staticmethod
    def zero() -> Integer:
        """
                        Create an Integer representing zero.
        
                        Returns:
                            Integer: An Integer with value 0.
        
                        Example:
                            >>> zero = Integer.zero()
                            >>> zero.is_zero()  # True
        """
    @typing.overload
    def __add__(self, arg0: Integer) -> Integer:
        """
        Add two Integers.
        """
    @typing.overload
    def __add__(self, arg0: int) -> Integer:
        """
        Add an Integer and a Python int.
        """
    def __eq__(self, arg0: Integer) -> bool:
        """
        Check if two Integers are equal.
        """
    def __ge__(self, arg0: Integer) -> bool:
        """
        Check if this Integer is greater than or equal to another.
        """
    def __gt__(self, arg0: Integer) -> bool:
        """
        Check if this Integer is greater than another.
        """
    def __hash__(self) -> int:
        """
                        Return a hash value for the Integer.
        
                        Returns:
                            int: Hash value of the Integer.
        """
    @typing.overload
    def __iadd__(self, arg0: Integer) -> Integer:
        """
        Add another Integer to this one in-place.
        """
    @typing.overload
    def __iadd__(self, arg0: int) -> Integer:
        """
        Add a Python int to this Integer in-place.
        """
    @typing.overload
    def __imul__(self, arg0: Integer) -> Integer:
        """
        Multiply this Integer by another in-place.
        """
    @typing.overload
    def __imul__(self, arg0: int) -> Integer:
        """
        Multiply this Integer by a Python int in-place.
        """
    def __init__(self, value: int) -> None:
        """
                        Construct an Integer from a numeric value.
        
                        Args:
                            value: An integer value to initialize the Integer.
        
                        Example:
                            >>> integer = Integer(42)
                            >>> integer = Integer(-123)
        """
    def __int__(self) -> int:
        """
                        Convert the Integer to a Python int.
        
                        Returns:
                            int: The numeric value as a Python int.
        
                        Example:
                            >>> integer = Integer(42)
                            >>> int(integer)  # 42
        """
    @typing.overload
    def __isub__(self, arg0: Integer) -> Integer:
        """
        Subtract another Integer from this one in-place.
        """
    @typing.overload
    def __isub__(self, arg0: int) -> Integer:
        """
        Subtract a Python int from this Integer in-place.
        """
    @typing.overload
    def __itruediv__(self, arg0: Integer) -> Integer:
        """
        Divide this Integer by another in-place.
        """
    @typing.overload
    def __itruediv__(self, arg0: int) -> Integer:
        """
        Divide this Integer by a Python int in-place.
        """
    def __le__(self, arg0: Integer) -> bool:
        """
        Check if this Integer is less than or equal to another.
        """
    def __lt__(self, arg0: Integer) -> bool:
        """
        Check if this Integer is less than another.
        """
    @typing.overload
    def __mul__(self, arg0: Integer) -> Integer:
        """
        Multiply two Integers.
        """
    @typing.overload
    def __mul__(self, arg0: int) -> Integer:
        """
        Multiply an Integer by a Python int.
        """
    def __ne__(self, arg0: Integer) -> bool:
        """
        Check if two Integers are not equal.
        """
    def __radd__(self, arg0: int) -> Integer:
        """
        Add a Python int and an Integer.
        """
    def __repr__(self) -> str:
        """
                        Return a string representation of the Integer for debugging.
        
                        Returns:
                            str: String representation of the Integer.
        """
    def __rmul__(self, arg0: int) -> Integer:
        """
        Multiply a Python int by an Integer.
        """
    def __rsub__(self, arg0: int) -> Integer:
        """
        Subtract an Integer from a Python int.
        """
    def __rtruediv__(self, arg0: int) -> Integer:
        """
        Divide a Python int by an Integer.
        """
    def __str__(self) -> str:
        """
                        Return a string representation of the Integer.
        
                        Returns:
                            str: String representation of the Integer.
        """
    @typing.overload
    def __sub__(self, arg0: Integer) -> Integer:
        """
        Subtract two Integers.
        """
    @typing.overload
    def __sub__(self, arg0: int) -> Integer:
        """
        Subtract a Python int from an Integer.
        """
    @typing.overload
    def __truediv__(self, arg0: Integer) -> Integer:
        """
        Divide two Integers.
        """
    @typing.overload
    def __truediv__(self, arg0: int) -> Integer:
        """
        Divide an Integer by a Python int.
        """
    def get_sign(self) -> Sign:
        """
                        Get the sign of the Integer.
        
                        Returns:
                            Sign: The sign (positive, negative, or zero) of the Integer.
        
                        Example:
                            >>> Integer(5).get_sign()  # Sign.Positive
                            >>> Integer(-5).get_sign()  # Sign.Negative
                            >>> Integer(0).get_sign()  # Sign.Zero
        """
    def is_defined(self) -> bool:
        """
                        Check if the Integer is defined (not uninitialized).
        
                        Returns:
                            bool: True if the Integer is defined, False otherwise.
        
                        Example:
                            >>> integer = Integer(42)
                            >>> integer.is_defined()  # True
                            >>> undefined_int = Integer.undefined()
                            >>> undefined_int.is_defined()  # False
        """
    def is_even(self) -> bool:
        """
                        Check if the Integer is even.
        
                        Returns:
                            bool: True if the Integer is divisible by 2, False otherwise.
        
                        Example:
                            >>> Integer(4).is_even()  # True
                            >>> Integer(3).is_even()  # False
        """
    def is_finite(self) -> bool:
        """
                        Check if the Integer is finite (not infinity).
        
                        Returns:
                            bool: True if the Integer is finite, False otherwise.
        
                        Example:
                            >>> Integer(42).is_finite()  # True
                            >>> Integer.positive_infinity().is_finite()  # False
        """
    def is_infinity(self) -> bool:
        """
                        Check if the Integer represents infinity (positive or negative).
        
                        Returns:
                            bool: True if the Integer is infinity, False otherwise.
        
                        Example:
                            >>> Integer.positive_infinity().is_infinity()  # True
                            >>> Integer.negative_infinity().is_infinity()  # True
                            >>> Integer(42).is_infinity()  # False
        """
    def is_negative(self) -> bool:
        """
                        Check if the Integer is negative (<= 0).
        
                        Returns:
                            bool: True if the Integer is negative or zero, False otherwise.
        
                        Example:
                            >>> Integer(-5).is_negative()  # True
                            >>> Integer(0).is_negative()  # True
                            >>> Integer(1).is_negative()  # False
        """
    def is_negative_infinity(self) -> bool:
        """
                        Check if the Integer represents negative infinity.
        
                        Returns:
                            bool: True if the Integer is negative infinity, False otherwise.
        
                        Example:
                            >>> Integer.negative_infinity().is_negative_infinity()  # True
                            >>> Integer.positive_infinity().is_negative_infinity()  # False
        """
    def is_odd(self) -> bool:
        """
                        Check if the Integer is odd.
        
                        Returns:
                            bool: True if the Integer is not divisible by 2, False otherwise.
        
                        Example:
                            >>> Integer(3).is_odd()  # True
                            >>> Integer(4).is_odd()  # False
        """
    def is_positive(self) -> bool:
        """
                        Check if the Integer is positive (>= 0).
        
                        Returns:
                            bool: True if the Integer is positive or zero, False otherwise.
        
                        Example:
                            >>> Integer(5).is_positive()  # True
                            >>> Integer(0).is_positive()  # True
                            >>> Integer(-1).is_positive()  # False
        """
    def is_positive_infinity(self) -> bool:
        """
                        Check if the Integer represents positive infinity.
        
                        Returns:
                            bool: True if the Integer is positive infinity, False otherwise.
        
                        Example:
                            >>> Integer.positive_infinity().is_positive_infinity()  # True
                            >>> Integer.negative_infinity().is_positive_infinity()  # False
        """
    def is_strictly_negative(self) -> bool:
        """
                        Check if the Integer is strictly negative (< 0).
        
                        Returns:
                            bool: True if the Integer is less than zero, False otherwise.
        
                        Example:
                            >>> Integer(-5).is_strictly_negative()  # True
                            >>> Integer(0).is_strictly_negative()  # False
                            >>> Integer(1).is_strictly_negative()  # False
        """
    def is_strictly_positive(self) -> bool:
        """
                        Check if the Integer is strictly positive (> 0).
        
                        Returns:
                            bool: True if the Integer is greater than zero, False otherwise.
        
                        Example:
                            >>> Integer(5).is_strictly_positive()  # True
                            >>> Integer(0).is_strictly_positive()  # False
                            >>> Integer(-1).is_strictly_positive()  # False
        """
    def is_zero(self) -> bool:
        """
                        Check if the Integer is exactly zero.
        
                        Returns:
                            bool: True if the Integer equals zero, False otherwise.
        
                        Example:
                            >>> Integer(0).is_zero()  # True
                            >>> Integer(5).is_zero()  # False
        """
    def to_string(self) -> String:
        """
                        Convert the Integer to a string representation.
        
                        Returns:
                            str: String representation of the Integer.
        
                        Example:
                            >>> Integer(42).to_string()  # "42"
                            >>> Integer(-123).to_string()  # "-123"
        """
class Real:
    @staticmethod
    def can_parse(string: String) -> Real:
        """
                        Check if a string can be parsed as a Real number.
        
                        Args:
                            string (str): The string to check.
        
                        Returns:
                            bool: True if the string can be parsed as a Real, False otherwise.
        
                        Example:
                            >>> Real.can_parse("3.14159")  # True
                            >>> Real.can_parse("not_a_number")  # False
                            >>> Real.can_parse("inf")  # True
        """
    @staticmethod
    def epsilon() -> Real:
        """
                        Create a Real number representing machine epsilon.
        
                        Returns:
                            Real: A Real number with the smallest representable positive value.
        
                        Example:
                            >>> eps = Real.epsilon()
                            >>> print(eps)  # Very small positive number
        """
    @staticmethod
    def half_pi() -> Real:
        """
                        Create a Real number representing π/2 (half pi).
        
                        Returns:
                            Real: A Real number with value π/2 ≈ 1.57079632679489662.
        
                        Example:
                            >>> half_pi = Real.half_pi()
                            >>> print(half_pi)  # 1.57079632679489662
        """
    @staticmethod
    def integer(integer: Integer) -> Real:
        """
                        Create a Real number from an Integer.
        
                        Args:
                            integer (Integer): The Integer value to convert.
        
                        Returns:
                            Real: A Real number with the integer's value.
        
                        Example:
                            >>> integer_val = Integer(42)
                            >>> real_val = Real.integer(integer_val)
                            >>> real_val.is_integer()  # True
        """
    @staticmethod
    def negative_infinity() -> Real:
        """
                        Create a Real number representing negative infinity.
        
                        Returns:
                            Real: A Real number with value -∞.
        
                        Example:
                            >>> neg_inf = Real.negative_infinity()
                            >>> neg_inf.is_negative_infinity()  # True
        """
    @staticmethod
    def parse(string: String) -> Real:
        """
                        Parse a string as a Real number.
        
                        Args:
                            string (str): The string to parse.
        
                        Returns:
                            Real: The parsed Real number.
        
                        Raises:
                            RuntimeError: If the string cannot be parsed as a Real number.
        
                        Example:
                            >>> real = Real.parse("3.14159")
                            >>> real = Real.parse("-42.5")
                            >>> real = Real.parse("inf")  # positive infinity
        """
    @staticmethod
    def pi() -> Real:
        """
                        Create a Real number representing π (pi).
        
                        Returns:
                            Real: A Real number with value π ≈ 3.14159265358979324.
        
                        Example:
                            >>> pi = Real.pi()
                            >>> print(pi)  # 3.14159265358979324
        """
    @staticmethod
    def positive_infinity() -> Real:
        """
                        Create a Real number representing positive infinity.
        
                        Returns:
                            Real: A Real number with value +∞.
        
                        Example:
                            >>> pos_inf = Real.positive_infinity()
                            >>> pos_inf.is_positive_infinity()  # True
        """
    @staticmethod
    def two_pi() -> Real:
        """
                        Create a Real number representing 2π (two pi).
        
                        Returns:
                            Real: A Real number with value 2π ≈ 6.28318530717958648.
        
                        Example:
                            >>> two_pi = Real.two_pi()
                            >>> print(two_pi)  # 6.28318530717958648
        """
    @staticmethod
    def undefined() -> Real:
        """
                        Create an undefined Real number.
        
                        Returns:
                            Real: An undefined Real number (NaN).
        
                        Example:
                            >>> undefined_real = Real.undefined()
                            >>> undefined_real.is_defined()  # False
        """
    @staticmethod
    def zero() -> Real:
        """
                        Create a Real number representing zero.
        
                        Returns:
                            Real: A Real number with value 0.0.
        
                        Example:
                            >>> zero = Real.zero()
                            >>> zero.is_zero()  # True
        """
    @typing.overload
    def __add__(self, arg0: Real) -> Real:
        """
        Add two Real numbers.
        """
    @typing.overload
    def __add__(self, arg0: float) -> Real:
        """
        Add a Real number and a double.
        """
    def __eq__(self, arg0: Real) -> bool:
        """
        Check if two Real numbers are equal.
        """
    def __float__(self) -> float:
        """
                        Convert the Real number to a Python float.
        
                        Returns:
                            float: The numeric value as a Python float.
        
                        Example:
                            >>> real = Real(3.14159)
                            >>> float(real)  # 3.14159
        """
    def __ge__(self, arg0: Real) -> bool:
        """
        Check if this Real number is greater than or equal to another.
        """
    def __gt__(self, arg0: Real) -> bool:
        """
        Check if this Real number is greater than another.
        """
    def __hash__(self) -> int:
        """
                        Return a hash value for the Real number.
        
                        Returns:
                            int: Hash value of the Real number.
        """
    @typing.overload
    def __iadd__(self, arg0: Real) -> Real:
        """
        Add another Real number to this one in-place.
        """
    @typing.overload
    def __iadd__(self, arg0: float) -> Real:
        """
        Add a double to this Real number in-place.
        """
    @typing.overload
    def __imul__(self, arg0: Real) -> Real:
        """
        Multiply this Real number by another in-place.
        """
    @typing.overload
    def __imul__(self, arg0: float) -> Real:
        """
        Multiply this Real number by a double in-place.
        """
    def __init__(self, value: float) -> None:
        """
                        Construct a Real number from a numeric value.
        
                        Args:
                            value: A numeric value (int, float, or double) to initialize the Real number.
        
                        Example:
                            >>> real = Real(3.14159)
                            >>> real = Real(42)
        """
    @typing.overload
    def __isub__(self, arg0: Real) -> Real:
        """
        Subtract another Real number from this one in-place.
        """
    @typing.overload
    def __isub__(self, arg0: float) -> Real:
        """
        Subtract a double from this Real number in-place.
        """
    @typing.overload
    def __itruediv__(self, arg0: Real) -> Real:
        """
        Divide this Real number by another in-place.
        """
    @typing.overload
    def __itruediv__(self, arg0: float) -> Real:
        """
        Divide this Real number by a double in-place.
        """
    def __le__(self, arg0: Real) -> bool:
        """
        Check if this Real number is less than or equal to another.
        """
    def __lt__(self, arg0: Real) -> bool:
        """
        Check if this Real number is less than another.
        """
    @typing.overload
    def __mul__(self, arg0: Real) -> Real:
        """
        Multiply two Real numbers.
        """
    @typing.overload
    def __mul__(self, arg0: float) -> Real:
        """
        Multiply a Real number by a double.
        """
    def __ne__(self, arg0: Real) -> bool:
        """
        Check if two Real numbers are not equal.
        """
    def __radd__(self, arg0: float) -> Real:
        """
        Add a double and a Real number.
        """
    def __repr__(self) -> str:
        """
                        Return a string representation of the Real number for debugging.
        
                        Returns:
                            str: String representation of the Real number.
        """
    def __rmul__(self, arg0: float) -> Real:
        """
        Multiply a double by a Real number.
        """
    def __rsub__(self, arg0: float) -> Real:
        """
        Subtract a Real number from a double.
        """
    def __rtruediv__(self, arg0: float) -> Real:
        """
        Divide a double by a Real number.
        """
    def __str__(self) -> str:
        """
                        Return a string representation of the Real number.
        
                        Returns:
                            str: String representation of the Real number.
        """
    @typing.overload
    def __sub__(self, arg0: Real) -> Real:
        """
        Subtract two Real numbers.
        """
    @typing.overload
    def __sub__(self, arg0: float) -> Real:
        """
        Subtract a double from a Real number.
        """
    @typing.overload
    def __truediv__(self, arg0: Real) -> Real:
        """
        Divide two Real numbers.
        """
    @typing.overload
    def __truediv__(self, arg0: float) -> Real:
        """
        Divide a Real number by a double.
        """
    def abs(self) -> Real:
        """
                        Get the absolute value of the Real number.
        
                        Returns:
                            Real: The absolute value of the Real number.
        
                        Example:
                            >>> Real(-5.5).abs()  # Real(5.5)
                            >>> Real(3.2).abs()  # Real(3.2)
        """
    def floor(self) -> Integer:
        """
                        Get the floor (largest integer <= value) of the Real number.
        
                        Returns:
                            Real: The floor of the Real number.
        
                        Example:
                            >>> Real(3.7).floor()  # Real(3.0)
                            >>> Real(-2.3).floor()  # Real(-3.0)
        """
    def get_sign(self) -> Sign:
        """
                        Get the sign of the Real number.
        
                        Returns:
                            Sign: The sign (positive, negative, or zero) of the Real number.
        
                        Example:
                            >>> Real(5.0).get_sign()  # Sign.Positive
                            >>> Real(-5.0).get_sign()  # Sign.Negative
                            >>> Real(0.0).get_sign()  # Sign.Zero
        """
    def is_defined(self) -> bool:
        """
                        Check if the Real number is defined (not NaN or uninitialized).
        
                        Returns:
                            bool: True if the Real number is defined, False otherwise.
        
                        Example:
                            >>> real = Real(3.14)
                            >>> real.is_defined()  # True
                            >>> undefined_real = Real.undefined()
                            >>> undefined_real.is_defined()  # False
        """
    def is_finite(self) -> bool:
        """
                        Check if the Real number is finite (not infinity or NaN).
        
                        Returns:
                            bool: True if the Real number is finite, False otherwise.
        
                        Example:
                            >>> Real(42.0).is_finite()  # True
                            >>> Real.positive_infinity().is_finite()  # False
        """
    def is_infinity(self) -> bool:
        """
                        Check if the Real number represents infinity (positive or negative).
        
                        Returns:
                            bool: True if the Real number is infinity, False otherwise.
        
                        Example:
                            >>> Real.positive_infinity().is_infinity()  # True
                            >>> Real.negative_infinity().is_infinity()  # True
                            >>> Real(42.0).is_infinity()  # False
        """
    def is_integer(self) -> bool:
        """
                        Check if the Real number represents an integer value.
        
                        Returns:
                            bool: True if the Real number has no fractional part, False otherwise.
        
                        Example:
                            >>> Real(42.0).is_integer()  # True
                            >>> Real(42.5).is_integer()  # False
        """
    def is_near(self, other: Real, tolerance: Real) -> bool:
        """
                        Check if the Real number is near another value within a tolerance.
        
                        Args:
                            other (Real): The value to compare against.
                            tolerance (Real): The tolerance for comparison.
        
                        Returns:
                            bool: True if the values are within tolerance, False otherwise.
        
                        Example:
                            >>> real1 = Real(3.14159)
                            >>> real2 = Real(3.14160)
                            >>> real1.is_near(real2, Real(1e-4))  # True
        """
    def is_negative(self) -> bool:
        """
                        Check if the Real number is negative (<= 0).
        
                        Returns:
                            bool: True if the Real number is negative or zero, False otherwise.
        
                        Example:
                            >>> Real(-5.0).is_negative()  # True
                            >>> Real(0.0).is_negative()  # True
                            >>> Real(1.0).is_negative()  # False
        """
    def is_negative_infinity(self) -> bool:
        """
                        Check if the Real number represents negative infinity.
        
                        Returns:
                            bool: True if the Real number is negative infinity, False otherwise.
        
                        Example:
                            >>> Real.negative_infinity().is_negative_infinity()  # True
                            >>> Real.positive_infinity().is_negative_infinity()  # False
        """
    def is_positive(self) -> bool:
        """
                        Check if the Real number is positive (>= 0).
        
                        Returns:
                            bool: True if the Real number is positive or zero, False otherwise.
        
                        Example:
                            >>> Real(5.0).is_positive()  # True
                            >>> Real(0.0).is_positive()  # True
                            >>> Real(-1.0).is_positive()  # False
        """
    def is_positive_infinity(self) -> bool:
        """
                        Check if the Real number represents positive infinity.
        
                        Returns:
                            bool: True if the Real number is positive infinity, False otherwise.
        
                        Example:
                            >>> Real.positive_infinity().is_positive_infinity()  # True
                            >>> Real.negative_infinity().is_positive_infinity()  # False
        """
    def is_strictly_negative(self) -> bool:
        """
                        Check if the Real number is strictly negative (< 0).
        
                        Returns:
                            bool: True if the Real number is less than zero, False otherwise.
        
                        Example:
                            >>> Real(-5.0).is_strictly_negative()  # True
                            >>> Real(0.0).is_strictly_negative()  # False
                            >>> Real(1.0).is_strictly_negative()  # False
        """
    def is_strictly_positive(self) -> bool:
        """
                        Check if the Real number is strictly positive (> 0).
        
                        Returns:
                            bool: True if the Real number is greater than zero, False otherwise.
        
                        Example:
                            >>> Real(5.0).is_strictly_positive()  # True
                            >>> Real(0.0).is_strictly_positive()  # False
                            >>> Real(-1.0).is_strictly_positive()  # False
        """
    def is_zero(self) -> bool:
        """
                        Check if the Real number is exactly zero.
        
                        Returns:
                            bool: True if the Real number equals zero, False otherwise.
        
                        Example:
                            >>> Real(0.0).is_zero()  # True
                            >>> Real(1e-15).is_zero()  # False
        """
    def sqrt(self) -> Real:
        """
                        Get the square root of the Real number.
        
                        Returns:
                            Real: The square root of the Real number.
        
                        Raises:
                            RuntimeError: If the Real number is negative.
        
                        Example:
                            >>> Real(25.0).sqrt()  # Real(5.0)
                            >>> Real(2.0).sqrt()  # Real(1.41421...)
        """
    def to_integer(self) -> Integer:
        """
                        Convert the Real number to an Integer.
        
                        Returns:
                            Integer: The Real number converted to an Integer (truncated).
        
                        Raises:
                            RuntimeError: If the Real number is undefined or infinity.
        
                        Example:
                            >>> Real(3.7).to_integer()  # Integer(3)
                            >>> Real(-2.9).to_integer()  # Integer(-2)
        """
class Sign:
    """
    
            Enumeration representing the sign of a number.
    
            The Sign enum indicates whether a value is positive, negative, or has no sign (zero).
        
    
    Members:
    
      Undefined : 
                Undefined sign state.
    
                Example:
                    >>> sign = Sign.Undefined
            
    
      Positive : 
                Positive sign (> 0).
    
                Example:
                    >>> sign = Sign.Positive
            
    
      Negative : 
                Negative sign (< 0).
    
                Example:
                    >>> sign = Sign.Negative
            
    
      NoSign : 
                No sign (= 0).
    
                Example:
                    >>> sign = Sign.NoSign
            
    """
    Negative: typing.ClassVar[Sign]  # value = <Sign.Negative: 2>
    NoSign: typing.ClassVar[Sign]  # value = <Sign.NoSign: 3>
    Positive: typing.ClassVar[Sign]  # value = <Sign.Positive: 1>
    Undefined: typing.ClassVar[Sign]  # value = <Sign.Undefined: 0>
    __members__: typing.ClassVar[dict[str, Sign]]  # value = {'Undefined': <Sign.Undefined: 0>, 'Positive': <Sign.Positive: 1>, 'Negative': <Sign.Negative: 2>, 'NoSign': <Sign.NoSign: 3>}
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
class String:
    @staticmethod
    def boolean(value: bool) -> String:
        """
                        Create a String from a boolean value.
        
                        Args:
                            value (bool): The boolean value to convert.
        
                        Returns:
                            String: A String containing "True" or "False".
        
                        Example:
                            >>> String.boolean(True)  # String("True")
                            >>> String.boolean(False)  # String("False")
        """
    @staticmethod
    def char(character: str) -> String:
        """
                        Create a String from a single character.
        
                        Args:
                            character (str): A single character.
        
                        Returns:
                            String: A String containing the single character.
        
                        Example:
                            >>> String.char('A')  # String("A")
        """
    @staticmethod
    def empty() -> String:
        """
                        Create an empty String.
        
                        Returns:
                            String: An empty String.
        
                        Example:
                            >>> empty_str = String.empty()
                            >>> empty_str.is_empty()  # True
        """
    @staticmethod
    def replicate(string: String, count: int) -> String:
        """
                        Create a String by replicating another String multiple times.
        
                        Args:
                            string (String): The String to replicate.
                            count (int): The number of times to replicate.
        
                        Returns:
                            String: A new String containing the repeated content.
        
                        Example:
                            >>> String.replicate(String("ab"), 3)  # String("ababab")
                            >>> String.replicate(String("x"), 5)  # String("xxxxx")
        """
    @typing.overload
    def __add__(self, arg0: String) -> str:
        """
        Concatenate two Strings.
        """
    @typing.overload
    def __add__(self, arg0: String) -> str:
        """
        Concatenate a String with another String.
        """
    def __eq__(self, arg0: String) -> bool:
        """
        Check if two Strings are equal.
        """
    def __hash__(self) -> int:
        """
                        Return a hash value for the String.
        
                        Returns:
                            int: Hash value of the String.
        """
    @typing.overload
    def __iadd__(self, arg0: String) -> str:
        """
        Append another String to this one in-place.
        """
    @typing.overload
    def __iadd__(self, arg0: str) -> str:
        """
        Append a standard string to this String in-place.
        """
    def __init__(self, value: str) -> None:
        """
                        Construct a String from a standard string.
        
                        Args:
                            value (str): A string value to initialize the String.
        
                        Example:
                            >>> string = String("Hello, World!")
                            >>> string = String("")
        """
    def __ne__(self, arg0: String) -> bool:
        """
        Check if two Strings are not equal.
        """
    def __radd__(self, arg0: str) -> str:
        """
        Concatenate a standard string with a String.
        """
    def __repr__(self) -> str:
        """
                        Return a string representation for debugging.
        
                        Returns:
                            str: The string content.
        """
    def __str__(self) -> str:
        """
                        Return the string value.
        
                        Returns:
                            str: The string content.
        """
    def get_first(self) -> str:
        """
                        Get the first character of the String.
        
                        Returns:
                            str: The first character.
        
                        Raises:
                            RuntimeError: If the String is empty.
        
                        Example:
                            >>> String("hello").get_first()  # "h"
        """
    def get_head(self, count: int) -> String:
        """
                        Get the first n characters of the String.
        
                        Args:
                            count (int): The number of characters to get from the beginning.
        
                        Returns:
                            String: A new String containing the first n characters.
        
                        Example:
                            >>> String("hello").get_head(3)  # String("hel")
        """
    def get_last(self) -> str:
        """
                        Get the last character of the String.
        
                        Returns:
                            str: The last character.
        
                        Raises:
                            RuntimeError: If the String is empty.
        
                        Example:
                            >>> String("hello").get_last()  # "o"
        """
    def get_length(self) -> int:
        """
                        Get the length of the String.
        
                        Returns:
                            int: The number of characters in the String.
        
                        Example:
                            >>> String("hello").get_length()  # 5
                            >>> String("").get_length()  # 0
        """
    def get_substring(self, start_index: int, length: int) -> String:
        """
                        Get a substring from the String.
        
                        Args:
                            start_index (int): The starting position (0-based).
                            length (int): The number of characters to extract.
        
                        Returns:
                            String: A new String containing the substring.
        
                        Example:
                            >>> String("hello").get_substring(1, 3)  # String("ell")
        """
    def get_tail(self, count: int) -> String:
        """
                        Get the last n characters of the String.
        
                        Args:
                            count (int): The number of characters to get from the end.
        
                        Returns:
                            String: A new String containing the last n characters.
        
                        Example:
                            >>> String("hello").get_tail(3)  # String("llo")
        """
    def is_empty(self) -> bool:
        """
                        Check if the String is empty.
        
                        Returns:
                            bool: True if the String has zero length, False otherwise.
        
                        Example:
                            >>> String("").is_empty()  # True
                            >>> String("hello").is_empty()  # False
        """
    def is_lowercase(self) -> bool:
        """
                        Check if all alphabetic characters in the String are lowercase.
        
                        Returns:
                            bool: True if all letters are lowercase, False otherwise.
        
                        Example:
                            >>> String("hello").is_lowercase()  # True
                            >>> String("Hello").is_lowercase()  # False
                            >>> String("123").is_lowercase()  # True (no letters)
        """
    def is_uppercase(self) -> bool:
        """
                        Check if all alphabetic characters in the String are uppercase.
        
                        Returns:
                            bool: True if all letters are uppercase, False otherwise.
        
                        Example:
                            >>> String("HELLO").is_uppercase()  # True
                            >>> String("Hello").is_uppercase()  # False
                            >>> String("123").is_uppercase()  # True (no letters)
        """
    def match(self, pattern: str) -> bool:
        """
                        Check if the String matches a regular expression pattern using boost::regex.
        
                        Args:
                            pattern (str): The regular expression pattern to match against.
        
                        Returns:
                            bool: True if the String matches the pattern, False otherwise.
        
                        Example:
                            >>> String("hello123").match(r"^[a-z]+\\d+$")  # True
                            >>> String("HELLO").match(r"^[a-z]+$")  # False
        """
Negative: Sign  # value = <Sign.Negative: 2>
NoSign: Sign  # value = <Sign.NoSign: 3>
Positive: Sign  # value = <Sign.Positive: 1>
Undefined: Sign  # value = <Sign.Undefined: 0>
