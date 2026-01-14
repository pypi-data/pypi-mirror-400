# Python Toolbox

Python toolbox that provides a timer and a configuration parser.

## Installation

To install this module run:
```
pip install teklia-toolbox
```

## Timer

Wrapper that calculates the execution time of instructions. This information is stored in the `delta` attribute which is of type [datetime.timedelta](https://docs.python.org/3/library/datetime.html#available-types).

```python
from teklia_toolbox.time import Timer

with Timer() as t:
    # Some code
    pass
print(f'These instructions took {t.delta}')
```

## Configuration parser

### ConfigParser

The `ConfigParser` class allows to instantiate a parser. It takes as argument:
- a boolean `allow_extra_keys` to specify if the parser should ignore extra unspecified keys instead of causing errors (default to `True`)

#### Add option

The `add_option` function allows to add parameter to the parser. It takes as argument:
- a parameter `name`
- a parameter `type` (which must be [callable](https://docs.python.org/3/library/functions.html#callable)) (default to `str`)
- a `many` boolean to specify if the parameter can have a list of values (default to `False`)
- a `default` value (default to `object()`)

#### Add subparser

The `add_subparser` function adds a parser as a new option to the initial parser, to allow finer control over nested configuration options. It takes the same arguments as the `ConfigParser` class and the `add_option` function.

#### Parse data

The `parse_data` function parses configuration data from a dict. It will raise `ConfigurationError` if any error is detected. Otherwise it returns a dictionary. It takes as argument:
- `data` of type [Mapping](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)

#### Parse

The `parse` function parses configuration data from a yaml file. It will raise `ConfigurationError` if any error is detected. Otherwise it returns a dictionary. It takes as argument:
- a `path` to the yaml file
- a boolean `exist_ok` to specify if the parser should ignore a non-existing file (default to `False`)

```python
from teklia_toolbox.config import ConfigParser

parser = ConfigParser()
parser.add_option('names', type=str, many=True, default=[])
parser.add_option('pseudo', type=str) # Required
parser.add_option('age', type=int, default=21)

parents_parser = parser.add_subparser('parents', default={})

mother_parser = parents_parser.add_subparser('mother', default={})
mother_parser.add_option('name', type=str, default=None)
mother_parser.add_option('age', type=int, default=None)

father_parser = parents_parser.add_subparser('father', default={})
father_parser.add_option('name', type=str, default=None)
father_parser.add_option('age', type=int, default=None)

# This will return
# {
#     'names': ['Pierre', 'Dupont'],
#     'pseudo': 'BoumBoum',
#     'age': 21,
#     'parents': {
#         'mother': {
#             'name': 'Marie',
#             'age': None
#         },
#         'father': {
#             'name': None,
#             'age': None
#         }
#     }
# }
parser.parse_data({
    'names': ['Pierre', 'Dupont'],
    'pseudo': 'BoumBoum',
    'parents': {
        'mother': {
            'name' : 'Marie'
        }
    }
})
```

### ConfigurationError

The `ConfigurationError` class inherits from the [ValueError](https://docs.python.org/3/library/exceptions.html#ValueError) class. This type of error is raised if the parser finds errors during parsing.

```python
from teklia_toolbox.config import ConfigurationError

raise ConfigurationError("Oops..")
```

### dir_path and file_path

The `dir_path` and `file_path` functions allow you to easily add path or file parameters to the parser.

```python
from teklia_toolbox.config import ConfigParser
from teklia_toolbox.config import dir_path, file_path

parser = ConfigParser()
parser.add_option('root_path', type=dir_path, default=None)
parser.add_option('csv_file', type=file_path, default=None)

# This will return
# {
#   'root_path': PosixPath('/sweet/home'),
#   'csv_file': PosixPath('/coucou.csv')
# }
parser.parse_data({
    'root_path': '/sweet/home/',
    'csv_file': './coucou.csv'
})
```