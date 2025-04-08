from .process import *
from .logger import *

"""
A simple class for invoking 7z commands. We're relying on the commandline here to cut
down on reliance on 3rd party packages. Requires 7zip, obviously.
https://web.mit.edu/outland/arch/i386_rhel4/build/p7zip-current/DOCS/MANUAL/
"""

_logger = register_logger('zipper')

def zip_files(zip_path: str, files: list, args: list = None):
    """
    :param zip_path: Path to the zip file we want to create
    :param files:    List of files, accepts wildcard. use 7z cli docs for reference. Can relative paths to cwd or abs paths
    :param args:     Additional args to pass to 7z. If supplied, default compression level will be used unless specified otherwise
    """

    cmd = [
        '7z',  # 7z exe
        'a',  # Add to archive
        '-tzip',  # zip file
    ]

    # if no args were passed, assume we're not passing a compression level
    if args is None:
        cmd.append('-mx=5')
    else:
        cmd.extend(args)

    cmd.append(f'{zip_path}')

    cmd.extend(files)

    _logger.debug(f'Executing 7z with {cmd}')

    # Create the archive
    ret_code, stdout, stderr = run_process(cmd, sup_out_stdout=True)
    if ret_code != 0:
        _logger.fatal(f'Failed to zip archive! Exit code: {ret_code}')
