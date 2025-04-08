import subprocess

from ..utility import *

# To work around circular imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .unreal import Unreal


# noinspection PyMethodMayBeStatic
class Editor:
    logger = register_logger('editor')

    def __init__(self, unreal: 'Unreal'):
        self._unreal = unreal

    def exec_cmd(self, project: str, args: list, nullrhi: bool = True) -> (int, str, str):
        """
        Executes UnrealEditor-Cmd with the specified arguments
        :param project: Path to .uproject
        :param args:    Arguments to pass to the exe
        :param nullrhi: Whether to run with a null renderer
        :return:        Exit code and stdout
        """

        cmd = [f'{self._unreal.binaries_path}/UnrealEditor-Cmd',
               f'{project}',
               '-unattended',
               '-buildmachine',
               '-stdout',
               '-nopause',
               '-nosplash',
               '-fullstdoutlogoutput']

        if nullrhi is True:
            cmd.append('-nullrhi')

        cmd.extend(args)

        self.logger.debug(f'Executing UnrealEditor-Cmd with {cmd}')
        return process.run_process(cmd, log_to_file=False)

    def exec(self, project: str, args: list) -> (int, str, str):
        """
        Executes UnrealEditor.exe with the specified arguments
        :param project: Path to .uproject
        :param args:    Arguments to pass to the exe
        :return:        Exit code and stdout
        """

        cmd = [f'{self._unreal.binaries_path}/UnrealEditor']

        cmd.extend(args)

        self.logger.debug(f'Executing UnrealEditor with {cmd}')
        return process.run_process(cmd)

    def run_commandlet(self, project: str, commandlet: str, args: list = None) -> (int, str):
        cmd = [f'-run={commandlet}']

        if args is not None:
            cmd.extend(args)

        return self.exec_cmd(project, cmd)

    def run_tests(self, project: str, test_filter: str, output_path: str) -> (int, str, str):
        """
        Runs tests with the specified project
        :param project:         Path to .uproject
        :param test_filter:     Test names separated by '+'
        :param output_path:     Output directory for test report
        :return:                Exit code and stdout
        """

        cmd = [
            f'-ExecCmds=Automation RunTests {test_filter};quit',
            '-TestExit="Automation Test Queue Empty"',
            f'-ReportExportPath="{output_path}"'
        ]

        return self.exec_cmd(project, cmd)
