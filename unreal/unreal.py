import logging
import os
import sys

# Locks to windows for now, eventually we should scope to allow this to work on non windows platforms
import winreg


from ..utility import *
from .uat import UAT
from .editor import Editor


class Unreal:
    logger = register_logger('unreal')

    # The registry path where UE looks for registered builds
    windows_reg_path = r'SOFTWARE\Epic Games\Unreal Engine\Builds'

    def __init__(self):
        """
        The base Unreal object.
        find install must be called yourself!
        """
        self.major = 0
        self.minor = 0
        self.version = ''
        self.is_source_build = False

    @classmethod
    def egs_build(cls, major: int, minor: int) -> 'Unreal':
        """
        Fetches the UE5 version stored in an environment variable such as UE_5.3_DIR.
        If no variable is found, it will then search C:/Program Files/Epic Games/UE_Major.Minor/

        :param major:           The major version of the UE build
        :param minor:           The minor version of the UE build
        """
        ue = Unreal()
        ue.major = major
        ue.minor = minor
        ue.version = f'{major}.{minor}'

        ue._find_install()

        # Setup objects
        ue._uat = UAT(ue)
        ue._editor = Editor(ue)

        return ue

    @classmethod
    def custom_build(cls, custom_guid: str) -> 'Unreal':
        """
        Looks for UE via the string env var UE_(custom_guid)_DIR or looks for the guid in
        HKCU:/SOFTWARE/Epic Games/Unreal Engine/Builds

        This will imply that the build is a source build, or an installed build derived from a source build.
        This will not work with EGS builds.
        """
        ue = Unreal()
        ue.version = custom_guid
        ue.is_source_build = True

        ue._find_install()

        # Setup objects
        ue._uat = UAT(ue)
        ue._editor = Editor(ue)

        return ue

    def _find_install(self):
        self.logger.info(f'Looking for UE {self.version}')

        # Look for the environment variable first
        ue_dir = os.environ.get(f'UE_{self.version}_DIR', 'UNKNOWN')

        # As a fallback, look for the default folder
        if ue_dir == 'UNKNOWN':
            # If we're a source build we'll need to handle this a bit differently
            if self.is_source_build:
                self.logger.debug(
                    f'Environment variable UE_{self.version}_DIR is not defined, looking inside build registry')

                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.windows_reg_path, 0, winreg.KEY_READ) as key:
                        value, regtype = winreg.QueryValueEx(key, self.version)

                        ue_dir = value
                except FileNotFoundError:
                    self.logger.fatal(f'Failed to find {self.version} inside '
                                      f'registry path (HKCU:{self.windows_reg_path})')
                    sys.exit(1)
                except Exception as e:
                    self.logger.fatal(f'Encountered exception when trying t find {self.version} '
                                      f'inside HKCU:{self.windows_reg_path}')
                    raise e
            else:
                self.logger.debug(
                    f'Environment variable UE_{self.version}_DIR is not defined, looking inside Program Files')

                prog_files_dir = f'C:/Program Files/Epic Games/UE_{self.version}'
                if os.path.exists(prog_files_dir):
                    ue_dir = prog_files_dir
                else:
                    self.logger.debug('Failed to find Unreal Engine installation in Program Files!')

        # If we can't find UE in either the env vars or program files, fatally error!
        if ue_dir == 'UNKNOWN':
            self.logger.fatal(
                f'Failed to find Unreal Engine installation. Please either define UE_{self.version}_DIR or install '
                f'Unreal Engine into your Program Files/Epic Games!')
            sys.exit(1)

        # Check to see if it's a valid Unreal Engine Path
        if not os.path.exists(f'{ue_dir}/Engine/Build/BatchFiles/RunUAT.bat'):
            self.logger.fatal(f'Could not find RunUAT.bat in {ue_dir}. Please verify the Unreal Engine installation!')
            sys.exit(1)

        self.logger.info(f'Found UE installation at {ue_dir}')
        self.unreal_path = ue_dir.replace(os.sep, '/')
        self.binaries_path = f'{ue_dir}/Engine/Binaries/Win64'
        self.batch_path = f'{ue_dir}/Engine/Build/BatchFiles'

    def uat(self) -> UAT:
        return self._uat

    def editor(self) -> Editor:
        return self._editor
