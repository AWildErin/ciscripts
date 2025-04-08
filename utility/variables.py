"""
Getters for various environment variables with correct default values.
"""

import os
from functools import lru_cache


@lru_cache
def ciscripts_force_allow_debug() -> bool:
    """
    Ignores CI mode check for set_logging_level(logging.DEBUG)
    Valid for: Any
    """
    var = os.getenv('ciscripts_force_allow_debug', '0')
    return var == '1'


@lru_cache
def is_ci() -> bool:
    """
    Returns whether the script is running in a CI environment
    Valid for: GitLab, GitHub
    """
    ci_var = os.getenv('ci', '0')
    return ci_var == '1'


@lru_cache
def ci_project_id() -> int:
    """
    Returns the GitLab project ID for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_project_id', 0)
    return var


def ci_project_title() -> str:
    """
    Returns the project title for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_project_title', '')
    return var


@lru_cache
def ci_project_url() -> str:
    """
    Returns the project url for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_project_url', '')
    return var

@lru_cache
def ci_commit_branch() -> str:
    """
    Returns the branch name for the current CI job.
    Not valid for merge request or tag pipelines. Use ci_commit_ref_name instead
    Valid for: GitLab
    """
    var = os.getenv('ci_commit_branch', '')
    return var


@lru_cache
def ci_commit_ref_name() -> str:
    """
    Returns the ref name for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_commit_ref_name', '')
    return var


@lru_cache
def ci_commit_message() -> str:
    """
    Returns the branch name for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_commit_message', '')
    return var


@lru_cache
def ci_commit_sha() -> str:
    """
    Returns the commit sha for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_commit_sha', '')
    return var


@lru_cache
def ci_commit_short_sha() -> str:
    """
    Returns the commit short sha for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_commit_short_sha', '')
    return var


@lru_cache
def ci_pipeline_id() -> int:
    """
    Returns the pipeline id for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_pipeline_id', -1)
    return var


@lru_cache
def ci_pipeline_url() -> str:
    """
    Returns the pipeline url for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_pipeline_url', '')
    return var


def ci_job_id() -> int:
    """
    Returns the job id for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_job_id', -1)
    return var


def ci_job_name() -> str:
    """
    Returns the job name for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_job_name', '')
    return var


def ci_job_url() -> str:
    """
    Returns the job url for the current CI job.
    Valid for: GitLab
    """
    var = os.getenv('ci_job_url', '')
    return var
