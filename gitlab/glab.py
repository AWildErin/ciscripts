import platform
import subprocess
import os
import re
import json
from typing import List, Tuple, Any
from pathlib import Path

from ..utility import *


class GLab:
    """
    Helper class to manage interacting with glab
    """

    _logger = register_logger('glab')
    _glab_api_error_regex = r'glab:\s+([^(]*).*(HTTP \d{3})'

    def __init__(self, host: str, token: str):
        self._logger.info('Authenticating glab...')

        self._gitlab_hostname = host
        self._gitlab_token = token

        self.exec(['auth', 'login', f'-h', host, f'-t', token, '--api-protocol', 'https'], log_to_file=False)

    @staticmethod
    def _replace_api_placeholders(endpoint: str) -> str:
        """
        Replaces glab api placeholders with correct api values
        @todo Handle others values. See #1
        """
        endpoint = endpoint.replace(':id', str(ci_project_id()))

        return endpoint

    def _throw_exec_exception(self, args: list[str], ret: int, stdout: str, stderr: str, custom_str: str = ''):
        """
        Simple helper function that will throw an exception and print stdout and stderr to the console
        """
        self._logger.critical(f'Failed to run glab with args: {args}!')
        self._logger.critical(f'Returned error code: {ret}. Output and error below.')
        self._logger.critical('----')
        self._logger.critical(stdout)
        self._logger.critical('----')
        self._logger.critical(stderr)
        if custom_str:
            self._logger.critical('----')
            self._logger.critical(custom_str)

        raise Exception('Error occurred while executing glab! Please read the logs above.')

    def exec(self, args: list[str], display_console_stdout=False, display_console_stderr=False,
             log_to_file=True) -> (int, str, str):
        cmd = [
            'glab'
        ]

        cmd.extend(args)

        is_calling_api = False
        if args[0] == 'api':
            is_calling_api = True

            # Try to get the index of -X, if it doesn't exist
            # we can assume it's a GET request
            # @todo This seems to have a perf impact so lets just make the user do it themselves, but revisit this later
            #try:
            #    method_index = args.index('-X')
            #    value = args[method_index + 1]
            #    if 'get' in value.lower():
            #        cmd.append('--paginate')
            #except ValueError:
            #    # Add paginate to get requests
            #    cmd.append('--paginate')

            if is_ci():
                # glab can't seem to update placeholder values when in CI mode
                replaced_args = self._replace_api_placeholders(cmd[2])
                self._logger.debug(f'Replacing api args from {cmd[2]} to {replaced_args}')
                cmd[2] = replaced_args

        self._logger.debug(f'Executing command: {cmd}')

        ret, stdout, stderr = run_process(cmd, sup_con_stdout=not display_console_stdout,
                                          sup_con_stderr=not display_console_stderr, log_to_file=log_to_file,
                                          allow_fail=True)

        self._logger.debug(f'Executed glab. Returned {ret}.')
        self._logger.debug(stdout)
        self._logger.debug(stderr)

        if ret != 0:
            self._throw_exec_exception(args, ret, stdout, stderr)

        # Handle certain cases for the API command
        if is_calling_api:
            # When calling endpoints, it will return 0 even if there's HTTP error message in stderr
            if len(stderr) > 0:
                match = re.match(self._glab_api_error_regex, stderr)

                # No successful HTTP codes should be inside stderr, so it's fine to
                # throw an error if group 2 has contents.
                # GLab reports that it needs updating here too, even on API calls
                if match is not None and match.group(2):
                    self._throw_exec_exception(args, ret, stdout, stderr)

        return ret, stdout, stderr

    def _get_project_data(self) -> dict:
        """
        Helper to get the current project data. Needed mainly for get_assets_for_package as the project id is
        not returned to us in any case, and we can't rely on CI env vars in non CI environments
        """

        ret, stdout, stderr = self.exec(['api', 'projects/:id'])
        try:
            obj = json.loads(stdout)
        except ValueError as err:
            raise Exception('Got text that was not json?')

        return obj

    #
    #   Common Helpers
    #

    def get_latest_package(self, package_name: str) -> dict:
        """
        Gets the latest package object for the specified package name
        """
        # Lock semver for only this function, its the only one that uses it
        # The reason why is because we use ciscripts to handle compiling for people who do not want to compile via VS
        # and this breaks it.
        import semver

        cmd = [
            'api',
            '/projects/:id/packages'
            '?order_by=version'
            '&sort=desc'
            f'&package_name={package_name}',
            '--paginate'
        ]

        ret, stdout, stderr = self.exec(cmd)

        # Assume we got the correct data as exec will throw an exception if it errors
        if len(stdout) > 0:
            data = json.loads(stdout)
            if not data:
                self._logger.debug(f'get_latest_package({package_name}) returned empty array! Returning empty dict.')
                return {}

            sorted_versions = sorted(data, key=lambda x: semver.Version.parse(x['version']))
            return sorted_versions[-1]
        else:
            return {}

    def get_assets_for_package(self, package: dict) -> list[tuple[str, str]]:
        """
        Returns a list of asset links for the specified package.
        """

        assets = []

        # if the dict is empty, return an empty list
        if not package:
            return assets

        package_name = package["name"]
        package_type = package['package_type']
        package_version = package['version']
        package_id = package['id']

        # GitLab never gives us the project id in any of the results from the package API requests,
        # so we'll need to run an additional API request here for people running this outside of CI environments

        project_id = ci_project_id()
        if not is_ci():
            project_id = self._get_project_data()['id']

        base_package_url = f'https://{self._gitlab_hostname}/api/v4/projects/{project_id}/packages/{package_type}/{package_name}/{package_version}'

        cmd = [
            'api',
            f'/projects/:id/packages/{package_id}/package_files',
            '--paginate'
        ]
        ret, stdout, stderr = self.exec(cmd)

        obj = json.loads(stdout)

        for asset in obj:
            assets.append((asset['file_name'], f'{base_package_url}/{asset["file_name"]}'))

        return assets

    def upload_generic_package(self, package_name: str, version: str, file_path: str, path_in_registry: str = None):
        """
        Uploads a file to the generic package registry with the specified package name and version
        :param package_name     : Package name
        :param version          : Version of the package
        :param file_path        : File to upload
        :param path_in_registry : Optional path within the package, if None file will be at the root of the package
        """

        package_path = os.path.basename(file_path)
        if path_in_registry is not None:
            package_path = path_in_registry

        cmd = [
            'api',
            f'/projects/:id/packages/generic/{package_name}/{version}/{package_path}',
            '-X', 'PUT',
            '--input', file_path
        ]
        self.exec(cmd)

    def release_create(self, release_version: str, assets: list[dict], title: str = None,
                       release_notes_path: str = None, additional_args: list[str] = None):
        """
        Creates a release with the specified version and files
        See https://gitlab.com/gitlab-org/cli/-/blob/main/docs/source/release/create.md

        :param release_version      : Release version, will be used for the tag and title.
        :param assets               : Assets to include within the release
        :param title                : Title of the release. If empty it will default to "Release {release_version}"
        :param release_notes_path   : Path to the release notes of the release
        :param additional_args      : A list of additional arguments to pass to the command. Key and Value must be split
        """

        cmd = [
            'release',
            'create',
            release_version
        ]

        if len(assets) > 0:
            cmd.append(f'--assets-links={json.dumps(assets)}')

        if title is not None:
            cmd.append(f'-n')
            cmd.append(title)
        else:
            cmd.append('-n')
            cmd.append(f'Release {release_version}')

        if release_notes_path is not None:
            cmd.append(f'-F')
            cmd.append(os.path.abspath(release_notes_path))

        if additional_args is not None:
            cmd.extend(additional_args)

        ret, stdout, stderr = self.exec(cmd, display_console_stderr=True)
