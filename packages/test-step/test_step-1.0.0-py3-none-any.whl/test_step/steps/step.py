#  Copyright (c) 2026 CUJO LLC
import logging
import threading

from collections.abc import Callable
from functools import wraps
from pathlib import Path

from test_step.html_reporting.extras import PassthroughExtras, Extras

logger = logging.getLogger(__name__)


class step:  # noqa: N801
    """
    Mark start and end of logical test steps by decorating a function or using a context.

    Start step/end header uses optional step name and function name. Step name highly recommended for context.

    When used as a decorator:
     * step start logs header and function arguments
     * step end logs header and return value or exception raised

    When used as a context manager:
     * step start logs header
     * step end logs header and exception raised if any

    Ensure argument and return objects implement __repr__ for best results.

    Ensure _copy is overridden in subclasses to avoid shared state

    :param name: optional logical step name
    :param report_attachments: optional attachment paths to attach to this step in the report
    """

    def __init__(self, name: str | None = None, report_attachments: list[Path] | None = None):
        self.function_name: str | None = None
        self.name = name
        self.report_attachments = report_attachments

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create new step instance to avoid shared state
            step_instance = self._copy()
            assert type(self) is type(step_instance), "_copy must be overridden in subclasses"
            step_instance.function_name = func.__name__
            with step_instance:
                logger.info(f'Arguments {args}, {kwargs}')
                result = func(*args, **kwargs)
                logger.info(f'Returned: {result}')
                return result

        return wrapper

    def _copy(self):
        """
        Override this method to create a copy of your class.

        Example::

            class device_step(step):
                def __init__(self, name: str | None = None, screenshot_before: bool = False):
                    self._screenshot_before = screenshot_before
                    super().__init__(name)

                def _copy(self):
                    return device_step(self.name, self._screenshot_before)

        The method MUST be equivalent to creating a new instance with the same arguments.

        :return: new instance of your class
        """
        return step(self.name, self.report_attachments)

    def __enter__(self):
        if tracker := StepTrackerContext.get():
            tracker.enter(self.name, self.report_attachments)
        logger.info(f'Enter {self._header}')

    def __exit__(self, exc_type: str, exc_val: str, exc_tb: str):
        result = 'Pass'
        if exc_val:
            result = f'Raised {exc_val!r}'
            logger.info(result)
        if tracker := StepTrackerContext.get():
            tracker.exit(result)
        logger.info(f'Exit  {self._header}')
        return False

    @property
    def _header(self) -> str:
        components = tuple(c for c in (self.name, self.function_name) if c)
        title = ''
        if len(components) == 2:
            title = f' - {components[0]} ({components[1]})'
        if len(components) == 1:
            title = f' - {components[0]} '
        return f"---Step{title}---"


class StepNode:
    def __init__(self, name: str, report_attachments: list[Path] | None = None):
        self.name = name
        self.children = []
        self.parent = None
        self.result = None
        self.report_attachments = report_attachments

    def add_child(self, child: 'StepNode'):
        child.parent = self
        self.children.append(child)

    def to_dict(self):
        json = {"step": self.name, "result": self.result}
        if self.report_attachments:
            json["report_attachments"] = [str(attachment) for attachment in self.report_attachments]
        if self.children:
            json["steps"] = [child.to_dict() for child in self.children]
        return json


class StepTracker:
    def __init__(self, file_extras: Extras | None = None):
        self.root = StepNode('root')
        self.current = self.root
        self._file_extras = file_extras

    def enter(self, name: str, report_attachments: list[Path] | None = None):
        report_attachments = self._handle_extras(self._file_extras, report_attachments)
        node = StepNode(name, report_attachments)
        self.current.add_child(node)
        self.current = node

    def exit(self, result: str | None = None):
        self.current.result = result
        if self.current.parent:
            self.current = self.current.parent

    @staticmethod
    def _handle_extras(file_extras: Extras, report_attachments: list[Path]):
        if report_attachments and isinstance(file_extras, PassthroughExtras):
            logger.warning(
                f'Attachments not present in report steps because --self-contained-html was used. '
                f'Attachments: {report_attachments}')
            return []
        if file_extras and report_attachments:
            return [file_extras.attach_file(attachment) for attachment in report_attachments]
        return []


class StepTrackerContext:
    _local = threading.local()

    @staticmethod
    def get():
        return getattr(StepTrackerContext._local, 'tracker', None)

    @staticmethod
    def set(tracker: StepTracker):
        StepTrackerContext._local.tracker = tracker

    @staticmethod
    def clear():
        StepTrackerContext._local.tracker = None
