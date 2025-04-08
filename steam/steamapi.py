import platform
import subprocess
import os
import re
import json
from typing import List, Tuple, Any
from pathlib import Path

from ..utility import *


class SteamAPI:
    """
    Helper class for some Steam web API endpoints
    """

    _logger = register_logger('steamapi')
    _partner_url = 'https://partner.steam-api.com'
    _community_url = 'https://api.steampowered.com'

    def __init__(self, api_key: str):
        self._api_key = api_key

    def _exec(self, url: str, data: dict, verb: str = 'get') -> (int, dict):
        # Just to handle cases where we use the library for workflows not requiring steamapi access
        import requests

        data_with_key = {'key': self._api_key} | data

        if verb == 'get':
            req = requests.get(url=url, data=data_with_key)
        else:
            # Treat as post request
            req = requests.post(url=url, data=data_with_key)

        code = req.status_code
        if code == 201:
            split_url = url.split('/')
            if 'SetAppBuildLive' in split_url:
                self._logger.warning(f'This action requires approval from {data["steamid"]}\'s Steam mobile app! '
                                     f'Please contact them.')
        elif code != 200:
            self._logger.error(f'({code}) Failed request to {url} with data:')
            self._logger.error(data)
            self._logger.error('Response body:')
            self._logger.error(req.text)
            return code, {}

        req_json = req.json()
        return code, req_json

    def set_build_live(self, app_id: int, branch: str, build_id: int,
                       description: str = 'Automated SetAppBuildLive', approver_steam_id: int = 0):
        """
        Sets the specified build id live for the specified branch

        :param app_id           : App ID for the build
        :param branch           : The branch to set the build live on. Public branches need approval.
        :param build_id         : The build we wish to set live
        :param description      : Optional description for the build.
        :param approver_steam_id: If defined, any pushes to public branches must be approved by this Steam user
        :return:
        """
        self._logger.info(f'Deploying {build_id} on {branch} for {app_id}.')
        # @todo This isn't ideal as it relies on default and beta being the only public ones.
        # we should leave it up the script to define.
        if approver_steam_id == 0:
            self._logger.warning('approver_steam_id not set! Deployments to public branches may '
                                 'require manual action in Steamworks')
        else:
            self._logger.warning(f'approver_steam_id was set to {approver_steam_id}! '
                                 f'All deployments must be approved by that user in Steam.')

        data = {
            'appid': app_id,
            'buildid': build_id,
            'betakey': branch,
            'description': description
        }

        if approver_steam_id != 0:
            data['steamid'] = approver_steam_id

        status_code, data = self._exec(f'{self._partner_url}/ISteamApps/SetAppBuildLive/v1', data, 'post')

        result = data['response']['result']
        if result != 1:
            self._logger.error(f'Failed to deploy {build_id} onto {branch}')
            sys.exit(1)

        self._logger.info('Request complete, result:')
        self._logger.info(f'Status code: {status_code}')
        self._logger.info(data)
