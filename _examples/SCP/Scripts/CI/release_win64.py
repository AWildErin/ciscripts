import ciscripts as ci
import os
import platform
import subprocess
from shared.branch_config import *

def exec_git(cmd:str) -> str:
    proc = subprocess.run(f'git {cmd}', capture_output=True, text=True)
    # Some commands append \n. This is easiest to do
    return proc.stdout.splitlines()[0]

cwd = os.getcwd()

# Get the relevant information
if 'STEAM_BRANCH' in os.environ:
    steam_branch = os.environ['STEAM_BRANCH']
else:
    steam_branch = 'internal'

steam_user = os.environ['STEAM_DEPLOY_USERNAME']
steam_pass = os.environ['STEAM_DEPLOY_PASSWORD']
steam_seed = os.environ['STEAM_DEPLOY_TOKEN']

is_ci = 'CI' in os.environ and os.environ['CI'] == 'true'
if (is_ci):
    git_branch = os.environ['CI_COMMIT_REF_NAME']
    git_commit = os.environ['CI_COMMIT_SHORT_SHA']
else:
    git_branch = exec_git('rev-parse --abbrev-ref HEAD')
    git_commit = exec_git('rev-parse --short HEAD')

steam = ci.SteamCMD(steam_user, steam_pass, steam_seed)
steamapi = ci.SteamAPI(os.environ['STEAM_PARTNER_API_KEY'])

if steam_branch in shipping_only_branches:
    configs_to_build = ['Shipping']
else:
    configs_to_build = branch_configurations

requires_approval = steam_branch == 'default' or steam_branch == 'beta'

for config in configs_to_build:
    config_branch = f'{steam_branch}_{config}'.lower()

    ci.gl_open_block(f'DeployGame_{config}', f'Deploying {steam_app_id} to {config_branch} | {config}')
    desc = steam_build_description_format.format(git_branch = git_branch, git_commit = git_commit, build_config = config, steam_branch = config_branch)
    ret, build_id = steam.run_app_build(f'{cwd}/Build/Scripts/app_{steam_app_id}_{config}.vdf', desc)
    if ret != 0:
        raise Exception('Failed to push app build to steam!')

    if build_id == -1:
        raise Exception('Failed to get build id from build!')

    if requires_approval:
        steamapi.set_build_live(steam_app_id, config_branch, build_id, approver_steam_id=steam_approver_id)
    else:
        steamapi.set_build_live(steam_app_id, config_branch, build_id)

    ci.gl_close_block(f'DeployGame_{config}')
