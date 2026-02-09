# Copyright (c) 2026 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


class Utils:
    """Utility functions for common string conversions."""

    @staticmethod
    def StrToBool(s: str) -> bool:
        """
        Convert a string to a boolean value.

        Args:
            s: String to convert (accepts: true/on/yes/y or false/off/no/n, case-insensitive).

        Returns:
            True or False based on the string value.

        Raises:
            ValueError: If the string is not a recognized boolean value.
        """
        s = s.lower()
        if s in ["true", "on", "yes", "y"]:
            res = True
        elif s in ["false", "off", "no", "n"]:
            res = False
        else:
            raise ValueError("Invalid string")
        return res

    @staticmethod
    def StrToInt(s: str) -> int:
        """
        Convert a string to an integer.

        Args:
            s: String to convert.

        Returns:
            Integer value.

        Raises:
            ValueError: If the string cannot be converted to an integer.
        """
        return int(s)

    @staticmethod
    def StrToFloat(s: str) -> float:
        """
        Convert a string to a float.

        Args:
            s: String to convert.

        Returns:
            Float value.

        Raises:
            ValueError: If the string cannot be converted to a float.
        """
        return float(s)
