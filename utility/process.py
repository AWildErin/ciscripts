import os
import subprocess
from datetime import datetime
from pathlib import Path

_custom_log_dir: str = ""
_ciscripts_root_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/../")
def get_process_log_dir():
    """
    Gets the log dir for process logs.
    Defaults to (ciscripts)/.ciscripts/process_logs/

    The reason it's within ciscripts is that it makes it easier to ignore, as we can just ignore it within the
    ciscripts repo and not have to worry about dealing with projects using ciscripts
    """

    if _custom_log_dir:
        return _custom_log_dir

    return f'{_ciscripts_root_dir}/.ciscripts/process_logs'


def set_process_log_dir(new_path: str):
    """
    Allows scripts to customise the output directory.
    """
    global _custom_log_dir
    _custom_log_dir = new_path


def run_process(cmd: list, sup_con_stdout: bool = False, sup_out_stdout: bool = False,
                sup_con_stderr: bool = False, sup_out_stderr: bool = False,
                log_to_file: bool = True, allow_fail: bool = False) -> (int, str, str):
    """
    Executes a subprocess with the given arguments and returns the exit code and stdout
    """

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    command_start_date = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

    stdout = ""
    for line in proc.stdout:
        if not sup_con_stdout:
            print(line, end='', flush=True)
        if not sup_out_stdout:
            stdout += line

    stderr = ""
    for line in proc.stderr:
        if not sup_con_stderr:
            print(line, end='', flush=True)
        if not sup_out_stderr:
            stderr += line

    if log_to_file:
        log_dir = get_process_log_dir()
        Path(log_dir).mkdir(parents=True, exist_ok=True)

        exe_name = os.path.basename(cmd[0])

        f = open(f'{log_dir}/{exe_name}_{command_start_date}_stdout.txt', 'w')
        f.write(stdout)
        f.close()

        f = open(f'{log_dir}/{exe_name}_{command_start_date}_stderr.txt', 'w')
        f.write(stderr)
        f.close()

    proc.stdout.close()
    proc.stderr.close()
    return_code = proc.wait()

    if allow_fail is False and return_code != 0:
        raise Exception(f'Program failed with error code: {return_code}!')

    return return_code, stdout, stderr
