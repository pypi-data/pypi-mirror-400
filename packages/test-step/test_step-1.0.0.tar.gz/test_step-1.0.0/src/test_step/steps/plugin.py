#  Copyright (c) 2026 CUJO LLC
import json
import logging

from _pytest.config import hookimpl, Parser
from _pytest.nodes import Item

from test_step.html_reporting.extras import get_extras
from test_step.steps.step import StepTrackerContext, StepTracker
from copy import deepcopy

logger = logging.getLogger(__name__)


def pytest_addoption(parser: Parser):
    parser.addoption("--show-steps", action="store_true", default=False,
                     help="Specify whether to show step details in reports")


@hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: Item):
    outcome = yield
    config = item.config
    if not config.getoption("--show-steps"):
        return

    report = outcome.get_result()
    # pytest_runtest_makereport gets invoked three times per test - setup, call, teardown
    match report.when:
        case 'setup':
            file_extras = None
            report_dir = config.getoption('htmlpath', default=None)
            if report_dir:
                file_extras = get_extras([], config, item)
            tracker = StepTracker(file_extras)
            StepTrackerContext.set(tracker)
        case 'call':
            if tracker := StepTrackerContext.get():
                steps = [child.to_dict() for child in tracker.root.children]
                report.steps = steps if len(steps) > 0 else None
        case 'teardown':
            StepTrackerContext.clear()


@hookimpl(hookwrapper=True)
def pytest_html_results_table_html(report, data):
    yield
    if getattr(report, 'steps', None):
        steps_with_links = deepcopy(report.steps)
        for step in steps_with_links:
            if 'report_attachments' in step:
                step['report_attachments'] = [
                    f'<a href={attachment} target="_blank">{attachment}</a>'
                    for attachment in step['report_attachments']
                ]
        steps_json = json.dumps(steps_with_links, indent=2)
        data.insert(0, f"<pre>{steps_json}</pre>")
