import ciscripts as ci
import os
import pathlib

py_dir = pathlib.Path(__file__).parent.resolve()
project = f'{py_dir}/../../SCP.uproject'

ue = ci.Unreal.custom_build('AWE_Custom')

# Build editor
ue.uat().build_editor(project, clean=True)
