import ciscripts as ci
import os

cwd = os.getcwd()
project = f'{cwd}/SCP.uproject'
code_quality = f'{cwd}/report.json'
test_dir = f'{cwd}/tests'

ue = ci.Unreal.custom_build('AWE_Custom')

# Build editor
ci.gl_open_block('CompileEditor', 'Compile editor binaries')
ue.uat().build_editor(project)
ci.gl_close_block('CompileEditor')

# Run Tests
ci.gl_open_block('RunTests', 'Compile project tests')
ue.editor().run_tests(project, 'StartsWith:SCP', test_dir)
ci.gl_close_block('RunTests')

# Convert the tests
ci.ue_to_junit(f'{test_dir}/index.json', f'{test_dir}/index.xml')
