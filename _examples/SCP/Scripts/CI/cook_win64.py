import ciscripts as ci
from shared.branch_config import *

import os

cwd = os.getcwd()
project = f'{cwd}/SCP.uproject'

# Get the relevant information
if 'STEAM_BRANCH' in os.environ:
    steam_branch = os.environ['STEAM_BRANCH']
else:
    steam_branch = 'internal'

ue = ci.Unreal.custom_build('AWE_Custom')
uat = ue.uat()

if steam_branch in shipping_only_branches:
    configs_to_build = ['Shipping']
else:
    configs_to_build = branch_configurations

for config in configs_to_build:
    ci.gl_open_block(f'CookGame_{config}', f'Cook and stage game files | {config}')
    uat.build_cook_run(
        project,
        ci.BuildCookRunArguments(
            configuration=config,
            platform='Win64',
            clean=True,
            build=True,
            cook=True,
            pak=True,
            stage=True,
            stagingdirectory=f'"{cwd}/Build/{config}"'
        )
    )
    ci.gl_close_block(f'CookGame_{config}')
