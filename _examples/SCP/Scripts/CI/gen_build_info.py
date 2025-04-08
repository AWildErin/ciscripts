import os
from datetime import datetime, timezone
import subprocess

def exec_git(cmd:str) -> str:
    proc = subprocess.run(f'git {cmd}', capture_output=True, text=True)
    # Some commands append \n. This is easiest to do
    return proc.stdout.splitlines()[0]

if __name__ == '__main__':
    cwd = os.getcwd()
    header_file_path = f'{cwd}/Source/SCPGame/VersionInfo.h'
    header_file_name = os.path.basename(header_file_path)
    print(f'Writing build info to {header_file_path}')

    # Prefer to use CI variables if we're a CI machine
    is_ci = 'CI' in os.environ and os.environ['CI'] == 'true'

    with open(f'{header_file_path}.in', 'r') as file:
        file_text = file.read()

    branch = '%BRANCH_NAME%'
    commit_short = '%COMMIT_SHORT%'
    commit_long = '%COMMIT_LONG%'
    time_utc = '%BUILD_TIMEUTC%'
    time_local = '%BUILD_TIMELOCAL%'
    if (is_ci):
        branch = os.environ['CI_COMMIT_REF_NAME']
        commit_short = os.environ['CI_COMMIT_SHORT_SHA']
        commit_long = os.environ['CI_COMMIT_SHA']
    else:
        branch = exec_git('rev-parse --abbrev-ref HEAD')
        commit_short = exec_git('rev-parse --short HEAD')
        commit_long = exec_git('rev-parse HEAD')


    time_utc = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S')
#    time_local = datetime.now().strftime('%d/%m/%Y %H:%S:%M')

    file_text = file_text.replace('%BRANCH_NAME%', branch)
    file_text = file_text.replace('%COMMIT_SHORT%', commit_short)
    file_text = file_text.replace('%COMMIT_LONG%', commit_long)
    file_text = file_text.replace('%BUILD_TIMEUTC%', time_utc)
#    file_text = file_text.replace('%BUILD_TIMELOCAL%', time_local)

    with open(header_file_path, 'w') as file:
        file.write(file_text)
