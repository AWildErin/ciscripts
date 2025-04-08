import os
import platform as plat_module
import logging
from functools import lru_cache

from ..utility import *
from .arguments import *

# To work around circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .unreal import Unreal


# noinspection PyMethodMayBeStatic
class UAT:
    """
    Main helper class for running tasks with UAT.

    For basic commands, there are pre-defined functions. However, you can run any command using exec(...).
    """

    logger = register_logger('uat')

    def __init__(self, unreal: 'Unreal'):
        self.logger.debug('Initialising UAT')
        self._unreal = unreal

    @lru_cache
    def _get_uat_executable(self) -> str:
        uat_path = ""
        plat = plat_module.system()

        if plat == 'Linux' or plat == 'Darwin':
            uat_path = "RunUAT.sh"
        else:
            uat_path = 'RunUAT.bat'

        return f'{self._unreal.batch_path}/{uat_path}'

    def exec(self, args: list) -> (int, str, str):
        """
        Executes RunUAT with the specified arguments

        :param args:    List of arguments to pass to RunUAT.bat/sh
        :return:        UAT exit code
        :rtype:         int, str
        """

        uat_exec = self._get_uat_executable()

        cmd = [uat_exec]
        cmd.extend(args)

        # If we don't have any args, print the help instead
        if len(args) == 0:
            cmd.append('-List')
        else: # can't use unattended with list
            cmd.append('-unattended')

        self.logger.debug(f'Executing UAT with {cmd}')

        return run_process(cmd, log_to_file=False)

    def build_cook_run(self, project: str, args: BuildCookRunArguments) -> (int, str, str):
        """
        Calls BuildCookRun with the specified arguments

        :param project: Path to your project
        :param args:    Data type of arguments to pass to BuildCookRun
        :return:        Return code of the UAT instance
        """

        # This is a required parameter, but it's separate to the arguments class,
        # so it's easier to manage and work with.
        cmd = ['BuildCookRun', f'-project="{project}"']

        cmd.extend(arg_formatter(vars(args)))

        return self.exec(cmd)

    def build_game(self, project: str, platform: str, configuration: str, notools: bool = True,
                   clean: bool = False) -> (int, str, str):
        """
        Builds the game modules for the specified project
        @todo use an argument datatype
        """

        cmd = [
            'BuildGame',
            f'-project={project}',
            f'-platform={platform}',
            f'-configuration={configuration}',
        ]

        if notools is True:
            cmd.append('-notools')

        if clean is True:
            cmd.append('-clean')

        return self.exec(cmd)

    def build_editor(self, project: str, notools: bool = True, clean: bool = False) -> (int, str, str):
        """
        Builds the editor modules for the specified project.
        Only ever build for the current platform in a development config.
        @todo use an argument datatype
        """

        cmd = [
            'BuildEditor',
            f'-project={project}'
        ]

        if notools is True:
            cmd.append('-notools')

        if clean is True:
            cmd.append('-clean')

        return self.exec(cmd)
