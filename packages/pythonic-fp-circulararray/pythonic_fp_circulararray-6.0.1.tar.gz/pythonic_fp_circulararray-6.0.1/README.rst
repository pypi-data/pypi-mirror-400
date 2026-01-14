Pythonic FP - Circular Array
============================

PyPI project
`pythonic-fp-circulararray
<https://pypi.org/project/pythonic-fp-circulararray>`_.

Python module implementing stateful circular array data structures.

- variable storage capacity circular array

  - O(1) pops either end 
  - O(1) amortized pushes either end 
  - O(1) indexing, fully supports slicing
  - auto-resizing more storage capacity when necessary, manually compatible
  - iterable, safely mutates while iterators iterating over previous state
  - comparisons compare identity before equality, like builtins
  - in boolean context, falsy when empty, otherwise truthy
  - function ``ca`` produces auto-resizing circular array from arguments

- fixed storage capacity circular array

  - O(1) pops and pushes either end 
  - O(1) indexing, does not support slicing
  - fixed total storage capacity
  - iterable, safely mutates while iterators iterating over previous state
  - comparisons compare identity before equality, like builtins
  - in boolean context, falsy when either empty or full, otherwise truthy
  - function ``caf`` produces fixed capacity circular array from arguments

Part of the
`pythonic-fp
<https://grscheller.github.io/pythonic-fp>`_
PyPI projects.

Documentation
-------------

Documentation for this project is hosted on
`GitHub Pages
<https://grscheller.github.io/pythonic-fp/circulararray>`_.

Copyright and License
---------------------

Copyright (c) 2023-2025 Geoffrey R. Scheller. Licensed under the Apache
License, Version 2.0. See the LICENSE file for details.
