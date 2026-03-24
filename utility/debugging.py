import subprocess


def init_remote_debugger(no_auth=False):
    """
    Initializes the remote debugger

    @param no_auth Disables authentication on the remote debugger
    """

    cmd = [
        'C:/Program Files/Microsoft Visual Studio 17.0/Common7/IDE/Remote Debugger/x64/msvsmon.exe',
        '/silent'
    ]

    if no_auth:
        cmd.append('/noauth')
        cmd.append('/anyuser')

    subprocess.Popen(cmd)
