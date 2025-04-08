# AWE_FILE_BEGIN - Erin
# Creates an installed build of Unreal Engine with the specified options

import os
import ciscripts as ci
import utils.buildgraph as bg

logger = ci.register_logger('script')

# Optional Arguments
WithDDC = bg.get_envvar_str('WithDDC', False)
ArchiveSymbols = bg.get_envvar_str('ArchiveSymbols', False)

ChangeLogFile = os.getenv('RELEASE_CHANGELOG', None)

# Required Arguments
# These use os.enivron[] meaning they will error if it doesn't exist
version = os.environ['RELEASE_VERSION']
version_raw = version.strip('v')


if ChangeLogFile is not None and not os.path.exists(ChangeLogFile):
    logger.error('Change log file did not exist!')
    exit(1)

glab = ci.GLab(os.environ['CI_SERVER_HOST'], os.environ['GLAB_TOKEN'])

ci.gl_open_block('makeinstalledbuild', 'Make Installed Build')

cmd = [
  f'{os.getcwd()}/Engine/Build/BatchFiles/RunUAT.bat',
  f'BuildGraph',
  f'-script=Engine/Build/InstalledEngineBuild.xml',
  f'-target=Archive Installed Build Win64',
  f'-nosign',
  f'-set:UseSccache=true',
  f'-set:GameConfigurations=Development;Test;Shipping',
  f'-set:WithFullDebugInfo=false',
  f'-set:WithWin64=true',
  f'-set:WithAndroid=false',
  f'-set:WithLinux=false',
  f'-set:WithLinuxArm64=false',
  f'-set:WithIOS=false',
  f'-set:WithTVOS=false',
  f'-set:WithMac=false',
  f'-set:WithDDC={WithDDC}',
  f'-set:ArchiveSymbols={ArchiveSymbols}'
]

ret, stdout, stderr = ci.run_process(cmd)
if ret != 0:
  logger.critical('Build failed.')
  exit(ret)

ci.gl_close_block('makeinstalledbuild')

ci.gl_open_block('packages', 'Uploading Packages')

logger.info('Uploading editor package...')
folder_path = './LocalBuilds/Engine/Archives'
editor_file_name = 'Editor.7z'

editor_archives = []
for filename in os.listdir(folder_path):
    if filename.startswith(editor_file_name):
        editor_archives.append(os.path.join(folder_path, filename))

for path in editor_archives:
    glab.upload_generic_package('Editor', version_raw, path)


if WithDDC == 'true':
  logger.info('Uploading ddc package...')
  glab.upload_generic_package('DerivedDataCache', version_raw, './LocalBuilds/Engine/Archives/DerivedDataCache.7z')

if ArchiveSymbols == 'true':
  logger.info('Uploading symbols package...')
  glab.upload_generic_package('Symbols', version_raw, './LocalBuilds/Engine/Archives/Symbols.7z')

ci.gl_close_block('packages')

ci.gl_open_block('release', 'Creating Release')

logger.info('Getting editor packages...')
editor_package = glab.get_latest_package('Editor')
editor_assets = glab.get_assets_for_package(editor_package)

logger.info('Getting ddc packages...')
ddc_package = glab.get_latest_package('DerivedDataCache')
ddc_assets = glab.get_assets_for_package(ddc_package)

logger.info('Getting symbol packages...')
symbols_package = glab.get_latest_package('symbols')
symbols_assets = glab.get_assets_for_package(symbols_package)

release_assets = []
for asset in editor_assets:
  release_assets.append({
      "name": asset[0],
      "url": asset[1]
    })

for asset in ddc_assets:
  release_assets.append({
      "name": asset[0],
      "url": asset[1]
    })

for asset in symbols_assets:
  release_assets.append({
      "name": asset[0],
      "url": asset[1]
    })

logger.info('Creating release...')
glab.release_create(version, release_assets, release_notes_path=ChangeLogFile, title=f'Unreal Engine Release v{version_raw}')

ci.gl_close_block('release')

logger.info('Done!')
