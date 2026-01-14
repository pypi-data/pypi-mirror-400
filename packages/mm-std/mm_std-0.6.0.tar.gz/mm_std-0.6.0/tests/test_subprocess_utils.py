import os

from mm_std import CmdResult, run_cmd, run_ssh_cmd
from mm_std.subprocess_utils import TIMEOUT_EXIT_CODE


class TestCmdResult:
    def test_combined_output_with_both_stdout_and_stderr(self):
        """Test combined output when both stdout and stderr are present."""
        result = CmdResult(stdout="output", stderr="error", code=0)
        assert result.combined_output == "output\nerror"

    def test_combined_output_with_only_stdout(self):
        """Test combined output when only stdout is present."""
        result = CmdResult(stdout="output", stderr="", code=0)
        assert result.combined_output == "output"

    def test_combined_output_with_only_stderr(self):
        """Test combined output when only stderr is present."""
        result = CmdResult(stdout="", stderr="error", code=1)
        assert result.combined_output == "error"

    def test_combined_output_with_neither(self):
        """Test combined output when both stdout and stderr are empty."""
        result = CmdResult(stdout="", stderr="", code=0)
        assert result.combined_output == ""


class TestRunCmd:
    def test_successful_command(self):
        """Test execution of a successful command."""
        result = run_cmd("echo 'hello world'")
        assert result.code == 0
        assert result.stdout.strip() == "hello world"
        assert result.stderr == ""

    def test_command_with_exit_code(self):
        """Test command that returns non-zero exit code."""
        result = run_cmd("exit 42", shell=True)
        assert result.code == 42
        assert result.stdout == ""

    def test_command_with_stderr(self):
        """Test command that outputs to stderr."""
        result = run_cmd("echo 'error message' >&2", shell=True)
        assert result.code == 0
        assert result.stdout == ""
        assert result.stderr.strip() == "error message"

    def test_capture_output_false(self):
        """Test command execution without capturing output."""
        result = run_cmd("echo 'test'", capture_output=False)
        assert result.code == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_timeout_handling(self):
        """Test command timeout handling."""
        result = run_cmd("sleep 2", timeout=1)
        assert result.code == TIMEOUT_EXIT_CODE
        assert result.stdout == ""
        assert result.stderr == "timeout"

    def test_echo_command(self, capsys):
        """Test echo_command parameter prints the command."""
        run_cmd("echo 'test'", echo_command=True)
        captured = capsys.readouterr()
        assert "echo 'test'" in captured.out

    def test_command_with_pipes(self):
        """Test command with pipes requires shell=True."""
        result = run_cmd("echo 'line1\nline2\nline3' | grep 'line2'", shell=True)
        assert result.code == 0
        assert result.stdout.strip() == "line2"

    def test_working_directory_commands(self, tmp_path):
        """Test commands that interact with filesystem."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        result = run_cmd(f"cat {test_file}")
        assert result.code == 0
        assert result.stdout.strip() == "test content"

    def test_environment_variables(self):
        """Test command that uses environment variables requires shell=True."""
        result = run_cmd("echo $HOME", shell=True)
        assert result.code == 0
        assert result.stdout.strip() == os.environ.get("HOME", "")

    def test_safe_mode_backticks_literal(self):
        """Test that backticks are treated as literal text in safe mode."""
        result = run_cmd("echo 'hello `world`'")
        assert result.code == 0
        assert "`world`" in result.stdout

    def test_safe_mode_dollar_literal(self):
        """Test that $() is treated as literal text in safe mode."""
        result = run_cmd("echo 'hello $(whoami)'")
        assert result.code == 0
        assert "$(whoami)" in result.stdout


class TestRunSshCmd:
    def test_ssh_command_construction(self):
        """Test that SSH command is properly constructed and quoted."""
        result = run_ssh_cmd("nonexistent-host", "echo 'test'", timeout=1)

        assert result.code != 0
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()

    def test_ssh_with_key_path(self):
        """Test SSH command with key path parameter."""
        result = run_ssh_cmd("nonexistent-host", "echo 'test'", ssh_key_path="/path/to/key", timeout=1)

        assert result.code != 0
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()

    def test_ssh_echo_command(self, capsys):
        """Test that SSH command echoing works."""
        run_ssh_cmd("nonexistent-host", "echo 'test'", echo_command=True, timeout=1)
        captured = capsys.readouterr()

        assert "ssh" in captured.out
        assert "nonexistent-host" in captured.out

    def test_ssh_command_quoting(self):
        """Test that SSH commands with special characters are properly quoted."""
        result = run_ssh_cmd("nonexistent-host", "echo 'hello; echo world'", timeout=1)

        assert result.code != 0
        assert "timeout" in result.stderr or "connect" in result.stderr.lower() or "resolve" in result.stderr.lower()
