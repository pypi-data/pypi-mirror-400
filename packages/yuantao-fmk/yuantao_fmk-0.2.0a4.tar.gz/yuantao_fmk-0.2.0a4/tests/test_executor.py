
import os
import unittest
from yuantao_fmk.executor import execute_command
SHELL_SCRIPT = os.path.join(os.path.dirname(__file__), "test_scripts", "test_execute_command.sh")


class TestExecutor(unittest.TestCase):
    def test_execute_command_success(self):
        ret = execute_command(["bash", SHELL_SCRIPT, "1"])
        self.assertEqual(ret, 0)

    def test_execute_command_fail(self):
        ret = execute_command(["bash", SHELL_SCRIPT, "2"])
        self.assertEqual(ret, 1)

    def test_execute_command_error_detection(self):
        ret = execute_command(["bash", SHELL_SCRIPT, "3"])
        self.assertEqual(ret, 1)

if __name__ == "__main__":
    unittest.main()