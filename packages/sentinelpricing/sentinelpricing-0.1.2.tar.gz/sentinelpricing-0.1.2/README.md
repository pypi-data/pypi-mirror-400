# Sentinel Rating Framework

Sentinel is a simple framework for insurance related pricing. Sentinel allows you to write your insurance product frameworks in pure Python. No additional
packages or modules required.

```python3
# Standard Library Imports
import csv

# Sentinel Imports
from sentinelpricing import Framework

class Motor(Framework):
    """A Fake Motor Insurance Product...
	
        ...with very simple pricing.
    """

    def load_rating_file(self, path):
        with open(path) as f:
	    reader = csv.DictReader(f)
	    table = LookupTable(reader, name=path)
        return table

    def set_up(self):
    	"""Load rating tables into the framework"""
        self.age = load_rating_file("age_rates.csv")        
	self.lic = load_rating_file("lic_rates.csv")

    def calculation(self, quote):
        """Quote Calculation"""
        # Imagine a base rate of £/$150
        quote += 150
        
        # Multiply that by the age rating factor
        quote *= self.age[quote['age']]
        
        # Multiply that by the license years rating factor
        quote *= self.lic[quote['lic']]
        
        # Return the finished quote
        return quote

# Returns a Quote object from the Motor Framework.
Motor.quote(
	{"age": 34, "lic": 7}
)
```

With a few lines of code, you are ready to use Sentinel to start building pricing engines for
analysis, or rating engines ready for deployment. Python is the most popular language in the world
(as of 2024), now you can use it and all its features to bring your work to the next level.

## Installing Sentinel

Sentinel is available on PyPi, albeit with a slightly different name:

`$ python -m pip install sentinelpricing`

Sentinel officially supports Python 3.8+.

## Features

Whilst in alpha development, features are expected to be added as and when - so keep checking!

- Framework Inheritance
- Audit Trails for Quote Calculations
- Lookup Tables for Rates
- Helpful Data Handling

## Developers and API Reference

Note, the Sentinel Package should never require third-party libraries. You'll have enough of an
argument with your IT department to just get Python installed - If they get wind of having to
download *dependencies* you'll never hear the end of it.

