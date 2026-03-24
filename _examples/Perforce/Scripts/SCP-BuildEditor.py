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

workspace_name = f'{ci.Perforce.get_ci_client_prefix()}SCP-Build'
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

ci.gl_open_block('ugs_buildgraph', 'Running BuildGraph...')
ue.uat().exec_buildgraph(
    'Engine/Build/Graph/Examples/BuildEditorAndTools.xml',
    'Submit To Perforce for UGS',
    [
        '-set:ArchiveStream=//UE5/Dev-Binaries',
        '-set:EditorTarget=SCPEditor',
        '-buildmachine',
        '-p4'
    ]
)
ci.gl_close_block('ugs_buildgraph')
