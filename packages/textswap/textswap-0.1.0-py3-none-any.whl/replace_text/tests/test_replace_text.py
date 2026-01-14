import json
import os
import unittest

from click.testing import CliRunner

from replace_text.replace_text import replace_text


class TestReplaceText(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_folder = "test_folder"
        self.config_file = "config.json"

        # Create test folder and files
        os.makedirs(self.test_folder, exist_ok=True)
        with open(os.path.join(self.test_folder, "test1.txt"), "w") as f:
            f.write("Hello world")
        with open(os.path.join(self.test_folder, "test2.txt"), "w") as f:
            f.write("Python is awesome")

        # Create config file
        config = {
            "dictionaries": {"test_dict": {"Hello": "Bonjour", "world": "monde", "Python": "Java"}},
            "ignore_extensions": [".ignore"],
            "ignore_directories": ["ignore_dir"],
            "ignore_file_prefixes": ["ignore_"],
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)

    def tearDown(self):
        # Clean up test files and folders
        for root, dirs, files in os.walk(self.test_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_folder)
        os.remove(self.config_file)

    def test_replace_text_keys_to_values(self):
        result = self.runner.invoke(
            replace_text,
            [
                "--direction",
                "1",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        with open(os.path.join(self.test_folder, "test1.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Bonjour monde")

        with open(os.path.join(self.test_folder, "test2.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Java is awesome")

    def test_replace_text_values_to_keys(self):
        # First, replace keys with values
        self.runner.invoke(
            replace_text,
            [
                "--direction",
                "1",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )

        # Then, test replacing values with keys
        result = self.runner.invoke(
            replace_text,
            [
                "--direction",
                "2",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        with open(os.path.join(self.test_folder, "test1.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Hello world")

        with open(os.path.join(self.test_folder, "test2.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Python is awesome")

    def test_ignore_extensions(self):
        with open(os.path.join(self.test_folder, "test.ignore"), "w") as f:
            f.write("Hello world")

        result = self.runner.invoke(
            replace_text,
            [
                "--direction",
                "1",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        with open(os.path.join(self.test_folder, "test.ignore")) as f:
            content = f.read()
        self.assertEqual(content, "Hello world")  # Content should remain unchanged

    def test_ignore_directories(self):
        os.makedirs(os.path.join(self.test_folder, "ignore_dir"), exist_ok=True)
        with open(os.path.join(self.test_folder, "ignore_dir", "test.txt"), "w") as f:
            f.write("Hello world")

        result = self.runner.invoke(
            replace_text,
            [
                "--direction",
                "1",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        with open(os.path.join(self.test_folder, "ignore_dir", "test.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Hello world")  # Content should remain unchanged

    def test_ignore_file_prefixes(self):
        with open(os.path.join(self.test_folder, "ignore_test.txt"), "w") as f:
            f.write("Hello world")

        result = self.runner.invoke(
            replace_text,
            [
                "--direction",
                "1",
                "--folder",
                self.test_folder,
                "--dict-name",
                "test_dict",
            ],
        )
        self.assertEqual(result.exit_code, 0)

        with open(os.path.join(self.test_folder, "ignore_test.txt")) as f:
            content = f.read()
        self.assertEqual(content, "Hello world")  # Content should remain unchanged


if __name__ == "__main__":
    unittest.main()
