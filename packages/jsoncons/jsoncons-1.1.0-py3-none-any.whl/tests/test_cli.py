# tests/test_cli.py v1.1.0 includes Fibonacci hashing function

import unittest
import sys
import io
import os
import json
import tempfile
import shutil
from unittest.mock import patch

# Add the parent directory (project root) to the Python path
# This allows importing 'serial_json' even when running tests directly
# Adjust the path if your structure is different
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main function from the CLI module
# Ensure this import works based on your project structure and how tests are run
try:
    from jsoncons import cli
except ImportError:
    # Fallback if running the test file directly might require path adjustments
    # or ensuring the package is installed ('pip install -e .')
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from jsoncons import cli


class TestFibonacciHashing(unittest.TestCase):
    """Tests for the fibonacci_hash_to_index function."""

    def test_valid_index_range_power_of_2_8(self):
        """Test that fibonacci_hash_to_index returns valid indices for table size 8."""
        for hash_value in [0, 1, 100, 1000, 0xFFFFFFFFFFFFFFFF]:
            index = cli.fibonacci_hash_to_index(hash_value, 8)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, 8)

    def test_valid_index_range_power_of_2_16(self):
        """Test that fibonacci_hash_to_index returns valid indices for table size 16."""
        for hash_value in [0, 1, 100, 1000, 0xFFFFFFFFFFFFFFFF]:
            index = cli.fibonacci_hash_to_index(hash_value, 16)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, 16)

    def test_valid_index_range_power_of_2_1024(self):
        """Test that fibonacci_hash_to_index returns valid indices for table size 1024."""
        for hash_value in [0, 1, 100, 1000, 0xFFFFFFFFFFFFFFFF]:
            index = cli.fibonacci_hash_to_index(hash_value, 1024)
            self.assertGreaterEqual(index, 0)
            self.assertLess(index, 1024)

    def test_consistency_same_input_same_output(self):
        """Test that the same hash value always produces the same index."""
        hash_value = 12345
        table_size = 256
        index1 = cli.fibonacci_hash_to_index(hash_value, table_size)
        index2 = cli.fibonacci_hash_to_index(hash_value, table_size)
        index3 = cli.fibonacci_hash_to_index(hash_value, table_size)
        self.assertEqual(index1, index2)
        self.assertEqual(index2, index3)

    def test_error_non_power_of_2_table_size(self):
        """Test that non-power-of-2 table sizes raise ValueError."""
        invalid_sizes = [3, 5, 6, 7, 9, 10, 15, 17, 100, 1000]
        for size in invalid_sizes:
            with self.assertRaises(ValueError) as context:
                cli.fibonacci_hash_to_index(12345, size)
            self.assertIn("power of 2", str(context.exception))

    def test_error_zero_table_size(self):
        """Test that table size 0 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            cli.fibonacci_hash_to_index(12345, 0)
        self.assertIn("power of 2", str(context.exception))

    def test_error_negative_table_size(self):
        """Test that negative table sizes raise ValueError."""
        with self.assertRaises(ValueError) as context:
            cli.fibonacci_hash_to_index(12345, -8)
        self.assertIn("power of 2", str(context.exception))

    def test_edge_case_hash_value_zero(self):
        """Test that hash value 0 produces a valid index."""
        index = cli.fibonacci_hash_to_index(0, 256)
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, 256)

    def test_edge_case_max_64bit_hash(self):
        """Test that maximum 64-bit hash value produces a valid index."""
        max_hash = 0xFFFFFFFFFFFFFFFF
        index = cli.fibonacci_hash_to_index(max_hash, 256)
        self.assertGreaterEqual(index, 0)
        self.assertLess(index, 256)

    def test_table_size_1(self):
        """Test that table size 1 (power of 2) always returns 0."""
        for hash_value in [0, 1, 100, 1000, 0xFFFFFFFFFFFFFFFF]:
            index = cli.fibonacci_hash_to_index(hash_value, 1)
            self.assertEqual(index, 0)


class TestJsonConsCLI(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures, if any."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.input_file_path = os.path.join(self.test_dir, 'input.json')
        self.output_file_path = os.path.join(self.test_dir, 'output.json')
        self.invalid_file_path = os.path.join(self.test_dir, 'invalid.json')

        # Sample valid JSON data
        self.valid_data = {"z": 1, "a": 2, "items": ["x", "y"]}
        self.valid_json_str = json.dumps(self.valid_data)
        self.valid_json_pretty = json.dumps(self.valid_data, indent=2) + '\n'

        # Sample invalid JSON data
        self.invalid_json_str = '{"key": "value", broken'

        # Write sample files
        with open(self.input_file_path, 'w') as f:
            f.write(self.valid_json_str)
        with open(self.invalid_file_path, 'w') as f:
            f.write(self.invalid_json_str)

    def tearDown(self):
        """Tear down test fixtures, if any."""
        # Remove the temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def run_cli(self, args_list, stdin_data=None):
        """Helper function to run the CLI main function with specific args and stdin."""
        # Patch sys.argv
        full_args = ['jsoncons'] + args_list
        # Use StringIO to capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        # Patch stdin if stdin_data is provided
        stdin_patch = None
        if stdin_data is not None:
            stdin_patch = patch('sys.stdin', io.StringIO(stdin_data))
            stdin_patch.start()

        exit_code = 0
        try:
            with patch('sys.argv', full_args), \
                 patch('sys.stdout', stdout_capture), \
                 patch('sys.stderr', stderr_capture):
                cli.main()
        except SystemExit as e:
            exit_code = e.code
        finally:
            if stdin_patch:
                stdin_patch.stop()

        return stdout_capture.getvalue(), stderr_capture.getvalue(), exit_code

    # -- Success Cases --

    def test_stdin_stdout_valid(self):
        """Test reading valid JSON from stdin and writing to stdout."""
        stdout, stderr, exit_code = self.run_cli(['encode'], stdin_data=self.valid_json_str)
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        # Default indent is 2
        self.assertEqual(stdout, self.valid_json_pretty)

    def test_infile_outfile_valid(self):
        """Test reading valid JSON from file and writing to file."""
        stdout, stderr, exit_code = self.run_cli(['encode', self.input_file_path, self.output_file_path])
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, '') # Should write to file, not stdout
        self.assertTrue(os.path.exists(self.output_file_path))
        with open(self.output_file_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, self.valid_json_pretty)

    def test_indent_option_4(self):
        """Test the --indent 4 option."""
        stdout, stderr, exit_code = self.run_cli(['encode', '--indent', '4'], stdin_data=self.valid_json_str)
        expected_output = json.dumps(self.valid_data, indent=4) + '\n'
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, expected_output)

    def test_indent_option_0_compact(self):
        """Test the --indent 0 option for compact output."""
        stdout, stderr, exit_code = self.run_cli(['encode', '--indent', '0'], stdin_data=self.valid_json_str)
        # Compact output (no indent) with a trailing newline
        expected_output = json.dumps(self.valid_data, indent=None, separators=(',', ':')) + '\n'
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, expected_output)

    def test_sort_keys_option(self):
        """Test the --sort-keys option."""
        stdout, stderr, exit_code = self.run_cli(['encode', '--sort-keys'], stdin_data=self.valid_json_str)
        expected_output = json.dumps(self.valid_data, indent=2, sort_keys=True) + '\n'
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, expected_output)

    def test_combined_options_compact_sorted(self):
        """Test combined --indent 0 and --sort-keys."""
        stdout, stderr, exit_code = self.run_cli(['encode', '--indent', '0', '--sort-keys'], stdin_data=self.valid_json_str)
        expected_output = json.dumps(self.valid_data, indent=None, sort_keys=True, separators=(',', ':')) + '\n'
        self.assertEqual(exit_code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(stdout, expected_output)

    # -- Error Cases --

    def test_invalid_json_stdin(self):
        """Test reading invalid JSON from stdin."""
        stdout, stderr, exit_code = self.run_cli(['encode'], stdin_data=self.invalid_json_str)
        self.assertNotEqual(exit_code, 0, "Exit code should be non-zero for invalid JSON")
        self.assertEqual(stdout, '')
        self.assertIn("Error: Invalid JSON input", stderr)

    def test_invalid_json_infile(self):
        """Test reading invalid JSON from a file."""
        stdout, stderr, exit_code = self.run_cli(['encode', self.invalid_file_path])
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, '')
        self.assertIn("Error: Invalid JSON input", stderr)

    def test_same_input_output_file(self):
        """Test error when input and output file paths are the same."""
        # Need to provide the same *path*, not just the same content file
        stdout, stderr, exit_code = self.run_cli(['encode', self.input_file_path, self.input_file_path])
        # The important thing is that it exits with an error code
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stdout, '')
        # The error is logged via the logging module to stderr

    # Note: Testing argparse's FileType errors (like file not found) can be done,
    # but might be considered testing the library itself. We focus here on the
    # custom logic within cli.main().


if __name__ == '__main__':
    unittest.main()