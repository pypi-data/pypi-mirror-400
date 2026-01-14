<!--
SPDX-FileCopyrightText: 2022 Thomas Kramer

SPDX-License-Identifier: CC-BY-SA-4.0
-->

# Liberty Parser

This library provides functions to parse, manipulate and format 'Liberty' files.
The liberty format is a common standard to describe certain aspects of standard-cell libraries such as timing, power, cell pin types, etc.

## Example


```python
from liberty.parser import parse_liberty

# Read and parse a library.
library = parse_liberty(open(liberty_file).read())



# Format the library.
print(str(library))

# Loop through all cells.
for cell_group in library.get_groups('cell'):
    cell_name = cell_group.args[0]
    print(cell_name)

    # Loop through all pins of the cell.
    for pin_group in cell_group.get_groups('pin'):
        pin_name = pin_group.args[0]
        print(pin_name)

        # Access a pin attribute.
        some_attribute = pin_group['some_attribute']

```

## Library structure.

The liberty library is made of `Group` objects.
The library itself is a `Group` object. A `Group` contains
other nested `Group`s, has a name, a list of arguments and
attributes.

```liberty
group_name(args) {
    simple_attribute: 1.23;
    other_group_name(args) {
        other_simple_attribute: 2.34;
        complex_attribute (1.23, 2.34);
    }
}
```

## Reading arrays and timing tables.

Timing tables are stored in the liberty format as attributes which holds a string with comma-separated values.

This string can be converted into a Numpy array with `get_array`:
```python
some_group.get_array('attribute_name')
```

## More examples

Example scripts can be found under `./examples`.

## Install for development

Run the following command to install the liberty parser using symlinks. This allows to edit the parser with immediate effect on the installed package.
```
pip install --upgrade --editable .
```

