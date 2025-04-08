import sys
import json
import xml.etree.ElementTree as elemTree


def ue_to_junit(ue_path: str, out_path: str):
    """
    Converts UE's test spec to JUnit
    :param ue_path:     File path to reports.json output by Unreal
    :param out_path:    File path to place converted test report
    """

    with open(ue_path, 'r', encoding='utf-8-sig') as file:
        unreal_data = json.load(file)

    junit_root = elemTree.Element('testsuites')
    junit_root.set('time', str(unreal_data['totalDuration']))

    for test in unreal_data['tests']:
        full_test_path = test['fullTestPath']
        test_suite_name = '.'.join(full_test_path.split('.')[:-1])  # Extract test suite name

        testcase = elemTree.SubElement(junit_root, 'testcase')
        testcase.set('time', str(test['duration']))
        testcase.set('suite_name', test_suite_name)
        testcase.set('classname', test_suite_name)
        testcase.set('name', test['testDisplayName'])

        for entry in test['entries']:
            event = entry['event']
            message = event['message']
            if event['type'] == 'Error':
                failure = elemTree.SubElement(testcase, 'failure')
                failure.text = message
                failure.set('message', message)

    junit_tree = elemTree.ElementTree(junit_root)
    junit_tree.write(out_path)
