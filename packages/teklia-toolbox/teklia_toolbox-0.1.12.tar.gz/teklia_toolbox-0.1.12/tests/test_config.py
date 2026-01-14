import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from teklia_toolbox.config import ConfigParser, ConfigurationError, dir_path, file_path


class TestConfigParser(TestCase):
    @patch("teklia_toolbox.config._all_checks")
    def test_file_path(self, all_checks_mock):
        all_checks_mock.return_value = True

        with self.assertRaisesRegex(AssertionError, " does not exist"):
            file_path("/aaaaaaa")

        with tempfile.NamedTemporaryFile() as f:
            parent_path = Path(f.name).parent
            with self.assertRaisesRegex(AssertionError, " is not a file"):
                file_path(parent_path)

            self.assertEqual(file_path(f.name), Path(f.name))

            # Existence checks should be ignored without all_checks
            all_checks_mock.return_value = False
            self.assertEqual(file_path(parent_path), parent_path)
            self.assertEqual(file_path("/aaaaaaa"), Path("/aaaaaaa"))

    @patch("teklia_toolbox.config._all_checks")
    def test_dir_path(self, all_checks_mock):
        all_checks_mock.return_value = True
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(dir_path(d), Path(d))

        with self.assertRaisesRegex(AssertionError, " does not exist"):
            dir_path("/aaaaaaa")

        with tempfile.NamedTemporaryFile() as f:
            with self.assertRaisesRegex(AssertionError, " is not a directory"):
                dir_path(f.name)

            # Existence checks should be ignored without all_checks
            all_checks_mock.return_value = False
            self.assertEqual(dir_path(f.name), Path(f.name))
            self.assertEqual(dir_path("/aaaaaaa"), Path("/aaaaaaa"))

    def test_configuration_error(self):
        error = ConfigurationError({"a": "b"})
        self.assertDictEqual(error.errors, {"a": "b"})
        self.assertEqual(str(error), '{"a": "b"}')
        self.assertEqual(repr(error), 'ConfigurationError({"a": "b"})')

    def test_add_option(self):
        parser = ConfigParser()
        parser.add_option("test", type=int)
        with self.assertRaisesRegex(
            AssertionError, "test is an already defined option"
        ):
            parser.add_option("test")
        with self.assertRaisesRegex(AssertionError, "Option type must be callable"):
            parser.add_option("toast", type=...)

    def test_parse_not_found(self):
        parser = ConfigParser()
        parser.add_option("something", default="thing")
        with self.assertRaises(FileNotFoundError):
            parser.parse(Path("/aaaaaaa"))
        self.assertDictEqual(
            parser.parse(Path("/aaaaaaa"), exist_ok=True),
            {"something": "thing"},
        )

    def test_parse_no_extra(self):
        parser = ConfigParser(allow_extra_keys=False)
        parser.add_option("something", type=bool, default=True)
        with self.assertRaises(ConfigurationError) as context:
            parser.parse_data({"something": False, "unknownthing": "oops"})

        self.assertDictEqual(
            context.exception.errors,
            {
                "unknownthing": "This option does not exist",
            },
        )

    def test_parse_null_no_default(self):
        parser = ConfigParser()
        parser.add_option("something", type=str)
        with self.assertRaises(ConfigurationError) as context:
            parser.parse_data({"something": None})

        self.assertDictEqual(
            context.exception.errors,
            {
                "something": "This option is required",
            },
        )

    def test_parse_null_with_default(self):
        parser = ConfigParser()
        parser.add_option("something", type=str, default=None)
        self.assertDictEqual(
            parser.parse_data({"something": None}),
            {"something": None},
        )
