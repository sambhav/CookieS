import errno
import subprocess
import sys
from subprocess import PIPE, STDOUT

from cookiecutter import utils
from cookiecutter.exceptions import FailedHookException

EXIT_SUCCESS = 0


def run_script(script_path, cwd="."):
    """Execute a script from a working directory.

    :param script_path: Absolute path to the script to run.
    :param cwd: The directory to run the script from.
    """
    run_thru_shell = sys.platform.startswith("win")
    if script_path.endswith(".py"):
        script_command = [sys.executable, script_path]
    else:
        script_command = [script_path]

    utils.make_executable(script_path)
    try:
        proc = subprocess.Popen(
            script_command, shell=run_thru_shell, cwd=cwd, stderr=STDOUT, stdout=PIPE
        )
        exit_status = proc.wait()
        output = proc.stdout.read().decode()
        if exit_status != EXIT_SUCCESS:
            raise FailedHookException(
                "Hook script failed (exit status: {})\n {}".format(exit_status, output)
            )
        # Print the output from the hooks so that we can capture the information
        # for the UI
        print(output)
    except OSError as os_error:
        if os_error.errno == errno.ENOEXEC:
            raise FailedHookException(
                "Hook script failed, might be an " "empty file or missing a shebang"
            )
        raise FailedHookException("Hook script failed (error: {})".format(os_error))
