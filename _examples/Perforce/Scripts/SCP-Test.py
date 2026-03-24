import os 

import ciscripts as ci

logger = ci.register_logger('script')

p4port = os.getenv('P4_PORT', '')
p4user = os.getenv('P4_USER', '')
p4pass = os.getenv('P4_PASS', '')
p4finger = os.getenv('P4_FINGER', '')

p4 = ci.Perforce(p4port, p4user, p4pass, fingerprint=p4finger)

ci.gl_open_block('p4_login', 'Logging in...')
p4.login()
ci.gl_close_block('p4_login')

# This workspace is shared with release as well, this is is fine as we
# also run this script as part of the release process
workspace_name = f'{ci.Perforce.get_ci_client_prefix()}SCP-Release'
workspace_root = f'C:\\workspaces\\{workspace_name}'
client_view = [
    '//UE5/Main/... //$NAME/...',
    '-//UE5/Main/LyraGame/... //$NAME/LyraGame/...',
]

ci.gl_open_block('p4_update', 'Updating client...')
p4.update_client(workspace_name, workspace_root, client_view)
ci.gl_close_block('p4_update')

ci.gl_open_block('p4_sync', 'Syncing client...')
p4.sync_workspace(workspace_name)
ci.gl_close_block('p4_sync')

ue = ci.Unreal.source_build(workspace_root)
project_dir = f'{workspace_root}/SCPGame'

ci.gl_open_block('scp_compileeditor', 'Compiling editor...')
ue.uat().build_editor(f'{project_dir}/SCPGame.uproject')
ci.gl_close_block('scp_compileeditor')

ci.gl_open_block('scp_runtests', 'Running tests...')
ue.editor().run_tests(f'{project_dir}/SCPGame.uproject', 'StartsWith:SCP', f'{project_dir}/Tests')
ci.gl_close_block('scp_runtests')

ci.ue_to_junit(f'{project_dir}/Tests/index.json', f'{project_dir}/Tests/index.xml')