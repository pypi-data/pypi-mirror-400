# Hassena's Darija Translator

This is a fun demo package created for Hassena. It translates simple English words into Moroccan Darija.

## Installation

```bash
pip install hassena-darija-demo
```

## Usage

```python
from hassena_darija import to_darija, say_hello_hassena

print(say_hello_hassena())

# Translate words
print(f"Thanks in Darija is: {to_darija('thanks')}")
print(f"Hello in Darija is: {to_darija('hello')}")
print(f"Friend in Darija is: {to_darija('friend')}")
```
