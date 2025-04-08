import re
import json
import os
import hashlib

from .logger import *


_logger = register_logger('codequality')


# noinspection PyMethodMayBeStatic
def _extract_errors(compiler_output: str) -> list:
    # Define a regular expression pattern to match error messages
    error_pattern = re.compile(
        r'(?P<path>.*?\(\d+\)): (?P<severity>warning|error) (?P<code>[A-Z]\d+): (?P<description>.*)')

    errors = []
    for match in error_pattern.finditer(compiler_output):
        error = match.groupdict()
        # Parse line number
        error['line'] = int(re.search(r'\((\d+)\)', error['path']).group(1))
        # Remove line number from path
        error['path'] = re.sub(r'\(\d+\)', '', error['path']).strip()
        # Make the path relative to the current folder
        error['path'] = os.path.relpath(error['path'])
        error['path'] = error['path'].replace('\\', '/')  # Convert Windows path to Unix path
        # Set severity to "minor"
        error['severity'] = 'minor'
        # Generate fingerprint using the code and description
        fingerprint_str = error['code'] + error['description'] + error['path'] + str(error['line'])
        error['fingerprint'] = hashlib.md5(fingerprint_str.encode()).hexdigest()
        errors.append(error)

    return errors


def _generate_code_climate_report(errors):
    """
    Converts the errors list into code climate format
    """
    code_climate_report = []
    for error in errors:
        code_climate_issue = {
            "description": error['description'],
            "check_name": error['code'],
            "fingerprint": str(error['fingerprint']),
            "severity": error['severity'],
            "location": {
                "path": error['path'],
                "lines": {
                    "begin": error['line']
                }
            }
        }
        code_climate_report.append(code_climate_issue)

    return code_climate_report


def generate_report(compiler_output: str) -> list:
    """
    Takes the compiler output and returns a list of errors with the code climate spec
    :param compiler_output: String containing compiler output.
    :return:                List of errors
    """
    errors = _extract_errors(compiler_output)
    code_climate_report = _generate_code_climate_report(errors)

    return code_climate_report


def write_report(compiler_output: str, filepath: str, overwrite_existing: bool = False):
    """
    Writes the code quality report to a file
    :param compiler_output:     String containing compiler output.
    :param filepath:            File path to write the report to
    :param overwrite_existing:  Whether or not to overwrite the file if it exists.
    """

    _logger.info(f'Writing code quality report to {filepath}')

    report = generate_report(compiler_output)

    # If we want to overwrite existing, load the previous content into an array
    existing_content = []
    if not overwrite_existing and os.path.exists(filepath):
        with open(filepath, 'r') as file:
            existing_content = json.load(file)

    existing_content.append(report)

    with open(filepath, 'w') as file:
        json.dump(existing_content, file, indent=2)
