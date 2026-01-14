# bigmathutils — Arbitrary-Precision Decimal Numbers for Python

`bigmathutils` is a tiny wrapper around Python’s built-in [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html) type.

It gives you:

- Easy, consistent handling of **big numbers** (money, crypto, prices, etc.)
- **Configurable precision** (`DP`) and **rounding mode** (`RM`)

Perfect when `float` is too imprecise and you want something safer but still easy to use.

---

## Features

- ✅ Arbitrary-precision decimal arithmetic  
- ✅ Global defaults for decimal places (`DP`) and rounding mode (`RM`)  
- ✅ Minimal, focused API  
- ✅ Works with `str`, `int`, `float`, `Decimal`, and `Big` values  

---

## Installation

If you’ve published this as a package:

```bash
pip install bigmathutils
```

## Quick Start

```python
from bigmathutils import Big

# Basic construction
a = Big("0.1")
b = Big("0.2")

# Addition
c = a + b
print(c)           # -> 0.3

# Or using methods, if you added them:
# c = a.add(b)

# Multiplication
d = Big("1.23") * Big("4")
print(d)           # -> 4.92
```

Because Big uses Decimal under the hood, you don’t get the usual floating-point surprises:

```python
from bigmathutils import Big

print(0.1 + 0.2)        # 0.30000000000000004 (float)
print(Big("0.1") + Big("0.2"))  # 0.3 (Big)
```

## Configuration

`Big` exposes two important global settings:

```python
from bigmathutils import Big

# Maximum decimal places for division, sqrt, etc.
Big.DP = 20    # default: 20

# Rounding mode (like big.js)
# 0: ROUND_DOWN
# 1: ROUND_HALF_UP      (default)
# 2: ROUND_HALF_EVEN
# 3: ROUND_UP
Big.RM = 1
```

Internally, these map to decimal’s rounding modes via _ROUND_MAP.

You can also use decimal.localcontext() for temporary precision overrides inside your own code, but for most use cases, setting Big.DP and Big.RM is enough.

## Creating Big Numbers

```python
from bigmathutils import Big
from decimal import Decimal

Big("1.2345")         # from string
Big(12345)            # from int
Big(1.2345)           # from float (not recommended for exact finance values)
Big(Decimal("1.2345"))# from Decimal
Big(Big("1.2345"))    # from another Big
```

Under the hood, the constructor converts the value to a Decimal and stores it as self._d.

## Arithmetic

The exact API here depends on how you implemented `Big`.

Below is a typical pattern using operator overloading.

### Addition

```python
x = Big("1.1")
y = Big("2.2")
print(x + y)      # -> 3.3
```

### Subtraction

```python
x = Big("5")
y = Big("2.5")
print(x - y)      # -> 2.5
```

### Multiplication

```python
x = Big("1.5")
y = Big("3")
print(x * y)      # -> 4.5
```

### Division

Division respects Big.DP and Big.RM:

```python
from bigmathutils import Big

Big.DP = 10
Big.RM = 1  # ROUND_HALF_UP

x = Big("1")
y = Big("3")

print(x / y)  # -> 0.3333333333  (10 decimal places)
```

## License

MIT License

Copyright (c) 2025 Matt Henry