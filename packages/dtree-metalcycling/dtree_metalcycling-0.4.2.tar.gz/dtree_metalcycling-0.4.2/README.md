# **dtree**: Linux **tree** but for Python dictionaries

Dictionaries are fun and useful!. But just like a folder structure, they can be multitiered storing all kinds of things in nested hierarchies. `tree` is a Linux utility that prints the multilevel structure of directories as a beautiful tree. `dtree` does the same but for dictionaries.

## Example

Consider the following dictionary

```python
dictionary = { "A": { "B": { "C": 0, "D": "some-string" }, "E": None }, "F": { "G": 0.0, "H": set([]) } }
```

Using `dtree` you can print the tree structure in different ways:

![Demo](https://github.com/metalcycling/dtree/blob/25ed816adacc2cbce20ecd02910891eeb1cb3106/docs/dtree.png?raw=true "Demo")

## Installation

This utility can be installed directly from PyPI as:

```bash
pip install dtree-metalcycling
```

For local installations intended for development, from the top of this repository run:

```bash
pip install -e .
```

## Known limitations

This version currently prints the `str` representation of the dictionary keys for the nodes of the tree. When keys are custom class objects, printing them could be very verbose so that would cause issues with the printed tree. I'll fix this in future PRs.

