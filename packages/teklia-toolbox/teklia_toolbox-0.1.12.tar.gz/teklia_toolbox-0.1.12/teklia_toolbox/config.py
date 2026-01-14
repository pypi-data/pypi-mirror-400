import json
import os
import sys
from collections import namedtuple
from collections.abc import Mapping
from pathlib import Path

import yaml

Option = namedtuple("Option", ["type", "default"])


# Used as a default value in `ConfigParser.add_option(default=UNSET)`
# because default=None implies that the option is optional
UNSET = object()


def _all_checks():
    """
    Prevents checking for path existence when running unit tests
    or other dev-related operations.
    This is the same as settings.ALL_CHECKS, but since the configuration
    is accessed before settings are initialized, it has to be copied here.
    This is made as a method to make mocking in unit tests much simpler
    than with a module-level constant.
    """
    os.environ.get("ALL_CHECKS") == "true" or "runserver" in sys.argv


def file_path(data):
    path = Path(data).resolve()
    if _all_checks():
        assert path.exists(), f"{path} does not exist"
        assert path.is_file(), f"{path} is not a file"
    return path


def dir_path(data):
    path = Path(data).resolve()
    if _all_checks():
        assert path.exists(), f"{path} does not exist"
        assert path.is_dir(), f"{path} is not a directory"
    return path


class ConfigurationError(ValueError):
    def __init__(self, errors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = errors

    def __str__(self):
        return json.dumps(self.errors)

    def __repr__(self):
        return f"{self.__class__.__name__}({self!s})"


class ConfigParser:
    def __init__(self, allow_extra_keys=True):
        """
        :param allow_extra_keys bool: Ignore extra unspecified keys instead
        of causing errors.
        """
        self.options = {}
        self.allow_extra_keys = allow_extra_keys

    def add_option(self, name, *, type=str, many=False, default=UNSET):
        assert name not in self.options, f"{name} is an already defined option"
        assert callable(type), "Option type must be callable"
        if many:
            self.options[name] = Option(lambda data: list(map(type, data)), default)
        else:
            self.options[name] = Option(type, default)

    def add_subparser(self, *args, allow_extra_keys=True, **kwargs):
        """
        Add a parser as a new option to this parser,
        to allow finer control over nested configuration options.
        """
        parser = ConfigParser(allow_extra_keys=allow_extra_keys)
        self.add_option(*args, **kwargs, type=parser.parse_data)
        return parser

    def parse_data(self, data):
        """
        Parse configuration data from a dict.
        Will raise ConfigurationError if any error is detected.
        """
        if not isinstance(data, Mapping):
            raise ConfigurationError("Parser data must be a mapping")

        parsed, errors = {}, {}

        if not self.allow_extra_keys:
            for name in data:
                if name not in self.options:
                    errors[name] = "This option does not exist"
        for name, option in self.options.items():
            if data.get(name) is not None:
                value = data[name]
            elif option.default is UNSET:
                errors[name] = "This option is required"
                continue
            elif option.default is None:
                parsed[name] = None
                continue
            else:
                value = option.default

            try:
                parsed[name] = option.type(value)
            except ConfigurationError as e:
                # Allow nested error dicts for nicer error messages
                # with add_subparser
                errors[name] = e.errors
            except Exception as e:
                errors[name] = str(e)

        if errors:
            raise ConfigurationError(errors)
        return parsed

    def parse(self, path, exist_ok=False):
        if not path.is_file() and exist_ok:
            # Act like the file is empty
            return self.parse_data({})
        return self.parse_data(yaml.safe_load(path.read_bytes()))
