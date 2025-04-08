#
# Configuration for steam build branches
# Directly ties into the cook and release scripts
#

# Which branches are shipping only, all other branches imply (branch_name)_(config) in steam.
# E.g.: internal = internal_shipping and internal_test
shipping_only_branches = [
    'default',
    'beta'
]

# What configurations will be build when a non shipping only branch is supplied
# When building, the staging directory will be passed as cwd/Build/{config}
branch_configurations = [
    'Shipping',
    'Test'
]

# What the description will be on the steam build
# Valid format placeholders:
# git_commit - string
# git_branch - string
# build_config - string
# steam_branch - string
steam_build_description_format = '{git_commit} on {git_branch}, with config {build_config}, for {steam_branch}'

# The approver must approve all deployments to branches inside shipping_only_branches
# This ID is for Erin (awilderin)
steam_approver_id = 76561198051936114

# App ID of the steam application
steam_app_id = 3031800
