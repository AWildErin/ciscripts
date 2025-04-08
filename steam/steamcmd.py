import platform
import subprocess
import os

from pathlib import Path
from ..utility import *


# noinspection PyMethodMayBeStatic
class SteamCMD:
    """
    Wrapper around SteamCMD

    This class assumes SteamCMD and SteamCMD-2FA are in a folder added to PATH.

    For security, we recommend storing the information in CI variables then accessing them with
    os.getenv. The following variable setup is what we use:
    - STEAM_DEPLOY_USERNAME - Steam username of the deploy account
    - STEAM_DEPLOY_PASSWORD - Steam password
    - STEAM_DEPLOY_TOKEN - Steam 2FA seed, you can obtain it by following:
        https://github.com/SteamTimeIdler/stidler/wiki/Getting-your-%27shared_secret%27-code-for-use-with-Auto-Restarter-on-Mobile-Authentication

    !! KEEP YOUR TOKEN SAFE. Anybody with the token can generate 2FA codes and bypass it to access your account. !!

    @todo Maybe we can handle autogenerating the vdfs depending on factors. This will allow us to a system to allow
        pushing git branches to specific Steam branches.
    """

    _logger = register_logger('steamcmd')

    _update_message = 'Update complete, launching Steamcmd...'
    _build_finished_regex = r'Successfully finished AppID \d+ build \(BuildID (\d+)\)'

    def __init__(self, username: str, password: str, seed: str):
        self.username = username
        self.password = password
        self.seed = seed

    def generate_code(self, username: str, password: str, seed: str) -> str:
        """
        Generates a steam authentication code using the specified seed
        :param username:    Steam username
        :param password:    Steam password
        :param seed:        Seed obtained using a tool like Steam Desktop Authenticator.
        :return:            Generated code
        """

        cmd = f'steamcmd-2fa -u {username} -p "{password}" -s "{seed}" -c'
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode == 0:
            return proc.stdout
        else:
            self._logger.error(
                f'Failed to obtain 2FA code from SteamCMD-2FA! Error code: {proc.returncode} {proc.stdout}')

    def exec(self, args: list) -> (int, str, str):
        """
        Executes SteamCMD with then specified arguments
        """

        code = self.generate_code(self.username, self.password, self.seed)
        if code is None:
            self._logger.fatal("Failed to obtain Steam authentication code!")
            return

        cmd = [
            f'steamcmd',
            f'+login {self.username} "{self.password}" {code}',

            '+api_logging 1 1',
            '+set_spew_level 4 4',
            '+@ShutdownOnFailedCommand 1',
        ]

        cmd.extend(args)
        cmd.append('+quit')

        self._logger.debug(f'Executing SteamCMD with {cmd}')

        ret, stdout, stderr = run_process(cmd, allow_fail=True)

        # Check if we updated, if so re-run the command
        match = re.match(self._update_message, stdout)
        if match is not None:
            self._logger.debug('Steam updated, restarting exec!')
            return self.exec(args)

        return ret, stdout, stderr

    def run_app_build(self, build_script: str, desc: str = None, preview: bool = False) -> (int, int):
        """
        Runs a build of the specified build script. See Steamworks docs for more information.

        :param build_script:    Path to the app build .vdf file
        :param desc:            Build description
        :param preview:         Whether or not this is a preview build. Preview builds will not get uploaded to Steam
        :return:                SteamCMD return code, and the submitted build id if uploaded.
        """

        # We can't easily pass just a list of args due to how steamcmd or subprocess handles them
        cmd = str('+run_app_build')

        # @todo Is this actually working? For som reason It doesn't actually run a preview for me.
        if preview is True:
            cmd += ' -preview'

        if desc is not None:
            cmd += f' -desc "{desc}"'

        cmd += f' "{str(Path(build_script).absolute())}"'

        self._logger.info(f'Running app build for {build_script}')

        ret, stdout, stderr = self.exec([cmd])
        build_id = -1

        match = re.search(self._build_finished_regex, stdout)
        if match is not None:
            build_id = match.group(1)

        return ret, build_id
