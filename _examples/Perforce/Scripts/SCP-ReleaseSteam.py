import os 

import ciscripts as ci
from Shared.SCPBranchConfig import *

logger = ci.register_logger('script')

#
# Customisable stuff
#

# This workspace is shared with release as well, this is is fine as we
# also run this script as part of the release process
workspace_name = f'{ci.Perforce.get_ci_client_prefix()}SCP-Release'
workspace_root = f'C:\\workspaces\\{workspace_name}'
client_view = [
    '//UE5/Main/... //$NAME/...',
    '-//UE5/Main/LyraGame/... //$NAME/LyraGame/...',
]

project_dir = f'{workspace_root}/SCPGame'
project_file = 'SCPGame.uproject'

#
# PERFORCE
#

p4port = os.getenv('P4_PORT', '')
p4user = os.getenv('P4_USER', '')
p4pass = os.getenv('P4_PASS', '')
p4finger = os.getenv('P4_FINGER', '')

p4 = ci.Perforce(p4port, p4user, p4pass, fingerprint=p4finger)

ci.gl_open_block('p4_login', 'Logging in...')
p4.login()
ci.gl_close_block('p4_login')

ci.gl_open_block('p4_update', 'Updating client...')
p4.update_client(workspace_name, workspace_root, client_view)
ci.gl_close_block('p4_update')

ci.gl_open_block('p4_sync', 'Syncing client...')
p4.sync_workspace(workspace_name)
ci.gl_close_block('p4_sync')

#
# COOK GAME
#

ue = ci.Unreal.source_build(workspace_root)

ci.gl_open_block('scp_updatelocalversion', 'Updating version files...')
ue.uat().exec(['UpdateLocalVersion'])
ci.gl_close_block('scp_updatelocalversion')

ci.gl_open_block('scp_compileeditor', 'Compiling editor...')
ue.uat().build_editor(f'{project_dir}/{project_file}')
ci.gl_close_block('scp_compileeditor')

# Get the relevant information
if 'STEAM_BRANCH' in os.environ:
    steam_branch = os.environ['STEAM_BRANCH']
else:
    steam_branch = 'internal'

if steam_branch in shipping_only_branches:
    configs_to_build = ['Shipping']
else:
    configs_to_build = branch_configurations

for config in configs_to_build:
    ci.gl_open_block(f'scp_cook_{config}', f'Cook and stage game files | {config}')

    arguments = ci.BuildCookRunArguments(
        configuration=config,
        platform='Win64',
        clean=False,
        build=True,
        cook=True,
        pak=True,
        stage=True,
        stagingdirectory=f'"{project_dir}/Build/{config}"',
        nocodesign=True
    )

    if config in map_section_configurations:
        arguments.mapinisectionstocook = '+'.join(map_section_configurations[config])

    ue.uat().build_cook_run(
        f'{project_dir}/{project_file}',
        arguments
    )
    ci.gl_close_block(f'scp_cook_{config}')

#
# RELEASE GAME
#

steam_user = os.environ['STEAM_DEPLOY_USERNAME']
steam_pass = os.environ['STEAM_DEPLOY_PASSWORD']
steam_seed = os.environ['STEAM_DEPLOY_TOKEN']

steam = ci.SteamCMD(steam_user, steam_pass, steam_seed)
steamapi = ci.SteamAPI(os.environ['STEAM_PARTNER_API_KEY'])

requires_approval = steam_branch == 'default' or steam_branch == 'beta'

changes = p4.get().run_changes('-m', '1', '//...')
current_cl = changes[0]['change'] if changes else 0

for config in configs_to_build:
    config_branch = f'{steam_branch}_{config}'.lower()

    ci.gl_open_block(f'scp_deploy_{config}', f'Deploying {steam_app_id} to {config_branch} | {config}')
    desc = steam_build_description_format.format(p4_changelist = current_cl, build_config = config, steam_branch = config_branch)
    ret, build_id = steam.run_app_build(f'{project_dir}/Build/Scripts/app_{steam_app_id}_{config}.vdf', desc)
    if ret != 0:
        raise Exception('Failed to push app build to steam!')

    if build_id == -1:
        raise Exception('Failed to get build id from build!')

    if requires_approval:
        steamapi.set_build_live(steam_app_id, config_branch, build_id, approver_steam_id=steam_approver_id)
    else:
        steamapi.set_build_live(steam_app_id, config_branch, build_id)

    ci.gl_close_block(f'scp_deploy_{config}')