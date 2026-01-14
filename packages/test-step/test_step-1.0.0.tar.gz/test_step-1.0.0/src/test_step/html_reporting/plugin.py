#  Copyright (c) 2026 CUJO LLC

import pytest
from _pytest.fixtures import FixtureRequest
from test_step.html_reporting.extras import Extras, get_extras


@pytest.fixture
def file_extras(pytestconfig, extras, request: FixtureRequest) -> Extras:
    return get_extras(extras, pytestconfig, request.node)
