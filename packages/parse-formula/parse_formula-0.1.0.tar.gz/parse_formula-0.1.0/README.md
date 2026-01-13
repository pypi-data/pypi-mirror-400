# py-parse-formula: Chemical formula parser for Python

## Installation

```bash
pip install parse-formula
```

## Usage

### Basic Usage

By default, it returns `int` counts. (Only accept stoichiometric compounds)

```py
>>> from parse_formula import parse_formula

>>> parse_formula("CH3CH2CH2CH3")
{'C': 4, 'H': 10}

>>> parse_formula("K4[Fe(CN)6]")
{'K': 4, 'Fe': 1, 'C': 6, 'N': 6}
```

### Handling Non-stoichiometric Compounds (float/Decimal/Fraction)

You can specify the type of the returned counts using the `parse_number` argument.

```py
>>> from decimal import Decimal
>>> from fractions import Fraction
>>> from parse_formula import parse_formula

>>> parse_formula("Fe0.9O")
parse_formula._parser.FormulaValueError: invalid literal for int() with base 10: '0.9'

Hint: Try calling `parse_formula(..., parse_number=float)`

>>> parse_formula("Fe0.9O", parse_number=float)
{'Fe': 0.9, 'O': 1.0}

>>> parse_formula("Fe0.9O", parse_number=Decimal)
{'Fe': Decimal('0.9'), 'O': Decimal('1')}

>>> parse_formula("Fe0.9O", parse_number=Fraction)
{'Fe': Fraction(9, 10), 'O': Fraction(1, 1)}
```
