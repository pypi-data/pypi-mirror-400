#!/usr/bin/env python3
"""
big.py

A small, easy-to-use wrapper around Python's Decimal.

- Arbitrary precision decimal arithmetic
- Configurable DP (decimal places) and RM (rounding mode)
"""
from __future__ import annotations
from decimal import (
    Decimal,
    getcontext,
    localcontext,
    ROUND_DOWN,
    ROUND_HALF_UP,
    ROUND_HALF_EVEN,
    ROUND_UP,
)

class Big:

    # Default decimal places for division, sqrt, etc.
    DP: int = 20

    # Rounding mode: 0..3 just like big.js
    # 0: ROUND_DOWN
    # 1: ROUND_HALF_UP
    # 2: ROUND_HALF_EVEN
    # 3: ROUND_UP
    RM: int = 1

    _ROUND_MAP = {
        0: ROUND_DOWN,
        1: ROUND_HALF_UP,
        2: ROUND_HALF_EVEN,
        3: ROUND_UP,
    }

    def __init__(self, value):
        if isinstance(value, Big):
            self._d = value._d
        elif isinstance(value, Decimal):
            self._d = value
        else:
            # Accept int, float, str, etc.
            self._d = Decimal(str(value))

    # ------------ configuration ------------

    @classmethod
    def config(cls, DP: int | None = None, RM: int | None = None) -> None:
        """
        Configure global defaults, DP: int | None = None, RM: int | None = None
        """
        if DP is not None:
            if not isinstance(DP, int) or DP < 0:
                raise ValueError("Big.DP must be a non-negative integer")
            cls.DP = DP

        if RM is not None:
            if RM not in cls._ROUND_MAP:
                raise ValueError("Big.RM must be one of 0, 1, 2, 3")
            cls.RM = RM

    @classmethod
    def _local_ctx(cls):
        """
        Return a context manager with the desired precision and rounding.
        """
        ctx = getcontext().copy()
        # A few extra guard digits to reduce rounding noise before quantize
        ctx.prec = cls.DP + 8
        ctx.rounding = cls._ROUND_MAP[cls.RM]
        return localcontext(ctx)

    def _wrap(self, d: Decimal) -> Big:
        """
        Wrap a Decimal into a Big and apply the context rounding.
        """
        with self._local_ctx():
            b = Big(0)
            b._d = +d  # unary plus applies current context
        return b

    # ------------ comparisons ------------

    def cmp(self, other: Big | int | float | str) -> int:
        o = Big(other)
        if self._d < o._d:
            return -1
        if self._d > o._d:
            return 1
        return 0

    def eq(self, other) -> bool:
        return self.cmp(other) == 0
    
    def __eq__(self, other) -> bool:
        return self.cmp(other) == 0

    def lt(self, other) -> bool:
        return self.cmp(other) < 0
    
    def __lt__(self, other) -> bool:
        return self.cmp(other) < 0

    def lte(self, other) -> bool:
        return self.cmp(other) <= 0
    
    def __le__(self, other) -> bool:
        return self.cmp(other) <= 0

    def gt(self, other) -> bool:
        return self.cmp(other) > 0
    
    def __gt__(self, other) -> bool:
        return self.cmp(other) > 0

    def gte(self, other) -> bool:
        return self.cmp(other) >= 0
    
    def __ge__(self, other) -> bool:
        return self.cmp(other) >= 0
    
    def abs(self):
        return Big(self._d.copy_abs())
    
    def __abs__(self):
        return Big(self._d.copy_abs())

    # ------------ arithmetic ------------

    def plus(self, other):
        """Return a new Big = this + other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d + o._d)
        
    def __add__(self, other):
        """Return a new Big = this + other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d + o._d)

    add = plus  # alias, like big.js

    def minus(self, other):
        """Return a new Big = this - other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d - o._d)
        
    def __sub__(self, other):
        """Return a new Big = this - other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d - o._d)

    sub = minus  # alias

    def times(self, other):
        """Return a new Big = this * other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d * o._d)

    def __mul__(self, other):
        """Return a new Big = this * other."""
        o = Big(other) if not isinstance(other, Big) else other
        with self._local_ctx():
            return self._wrap(self._d * o._d)
        
    mul = times  # alias

    def div(self, other):
        """
        Return a new Big = this / other.

        Result is rounded to Big.DP decimal places using Big.RM,
        """
        o = Big(other) if not isinstance(other, Big) else other
        # Test the value
        with self._local_ctx():
            q = self._d / o._d
            if self.DP > 0:
                unit = Decimal(1).scaleb(-self.DP)  # 10^-DP
                q = q.quantize(unit)
            else:
                q = q.quantize(Decimal(1))  # integer
            return self._wrap(q)
        
    def __truediv__(self, other):
        """
        Return a new Big = this / other.

        Result is rounded to Big.DP decimal places using Big.RM,
        """
        o = Big(other) if not isinstance(other, Big) else other
        # Test the value
        with self._local_ctx():
            q = self._d / o._d
            if self.DP > 0:
                unit = Decimal(1).scaleb(-self.DP)  # 10^-DP
                q = q.quantize(unit)
            else:
                q = q.quantize(Decimal(1))  # integer
            return self._wrap(q)
        
    def sqrt(self):
        """
        Return square root of this Big, rounded to Big.DP places.
        """
        with self._local_ctx():
            q = self._d.sqrt()
            if self.DP > 0:
                unit = Decimal(1).scaleb(-self.DP)
                q = q.quantize(unit)
            else:
                q = q.quantize(Decimal(1))
            return self._wrap(q)

    def neg(self):
        """Return a new Big which is the negation of this Big."""
        return self._wrap(-self._d)
    
    def __ne__(self):
        """Return a new Big which is the negation of this Big."""
        return self._wrap(-self._d)

    # ------------ formatting ------------

    def to_fixed(self, dp: int | None = None) -> str:
        """
        Returns a string with exactly dp decimal places.
        If dp is None, uses Big.DP.
        """
        if dp is None:
            dp = self.DP

        with self._local_ctx():
            if dp >= 0:
                unit = Decimal(1).scaleb(-dp)  # 10^-dp
                q = self._d.quantize(unit)
            else:
                unit = Decimal(1).scaleb(-dp)  # 10^-(-k) = 10^k
                q = (self._d / unit).to_integral_value() * unit

        s = format(q, "f")

        if dp <= 0:
            # no fractional part requested
            return s.split(".", 1)[0]

        if "." not in s:
            s += "." + "0" * dp
            return s

        intp, fracp = s.split(".", 1)
        fracp = fracp.ljust(dp, "0")[:dp]
        return intp + "." + fracp

    def to_number(self) -> float:
        """convert to Python float (may lose precision)."""
        return float(self._d)

    def __str__(self) -> str:
        """Convert to Python string"""
        return format(self._d, "f")

    def __repr__(self) -> str:
        return f"Big('{str(self)}')"
