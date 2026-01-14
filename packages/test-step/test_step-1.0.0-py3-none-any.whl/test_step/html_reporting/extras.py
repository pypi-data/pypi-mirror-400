#  Copyright (c) 2026 CUJO LLC
import gzip
import re
import shutil
from pathlib import Path

import pytest_html.extras
from _pytest.config import Config
from _pytest.nodes import Node

from test_step.util import ArgumentError


class Extras:
    """
    API for attaching extras to pytest-html reports
    """

    def attach_file(self, file: Path, name: str | None = None, compress: bool = False):
        """
        Attach a file to the report.

        Identical semantics to extras.append(pytest_html.extras.extra(...))

        :param file: file to attach, copied
        :param name: attachment name in report, filename by default
        :param compress: compress file with gzip and add .gz extension
        """
        pass

    def attach_text(self, contents: str, name: str = 'Text', compress: bool = False):
        """
        Attach text to the report.

        Identical semantics to extras.append(pytest_html.extras.text(contents, name))

        :param contents: text contents to save
        :param name: attachment name in report
        :param compress: compress file with gzip and add .gz extension
        """
        pass


class NoopExtras(Extras):
    """
    NOOP placeholder used when reports are disabled. Does nothing.
    """
    pass


class PassthroughExtras(Extras):
    """
    Used when --self-contained-html is set. Forwards to regular pytest-html APIs. This includes the memory leaks,
    but --self-contained-html can't be used with large files anyway.

    compress parameter is ignored.
    """

    def __init__(self, pytest_html_extras: list):
        self._pytest_html_extras = pytest_html_extras

    def attach_file(self, file: Path, name: str | None = None, compress: bool = False):  # noqa: ARG002
        contents = file.read_text()
        name = name or file.name
        self._pytest_html_extras.append(pytest_html.extras.text(contents, name))

    def attach_text(self, contents: str, name: str = 'Text', compress: bool = False):  # noqa: ARG002
        self._pytest_html_extras.append(pytest_html.extras.text(contents, name))


class FileExtras(Extras):
    """
    Saves attached extras to <report dir>/extras/ and adds links to report.
    """
    dir_name = 'extras'

    def __init__(self, node: Node, extras: list, report_dir: Path):
        self._report_dir = report_dir
        self._extras_dir = self._report_dir / FileExtras.dir_name
        self._extras_dir.mkdir(parents=True, exist_ok=True)
        self._pytest_html_extras = extras
        self._attachment_counter = 0
        # based on pytest_html.basereport.BaseReport._asset_filename
        # execution_count is set by pytest-rerunfailures, untested integration!
        # https://github.com/pytest-dev/pytest-rerunfailures/tree/master?tab=readme-ov-file#development
        self._file_prefix = re.sub(r"[^\w.]", "_", node.nodeid) + '_' + str(getattr(node, "execution_count", 0))

    def attach_file(self, file: Path, name: str | None = None, compress: bool = False):
        extension = ''.join(file.suffixes)
        if not extension:
            raise ArgumentError(f'Filename "{file.name}" has no extension')
        name = name or file.name
        if compress:
            extension += '.gz'
            name += '.gz'
        relative_path = self._new_relative_file_path(extension)
        absolute_path = self._absolute_path(relative_path)
        if compress:
            with file.open('rb') as f_in, gzip.open(absolute_path, 'wb') as f_out:
                # noinspection PyTypeChecker
                shutil.copyfileobj(f_in, f_out)
        else:
            shutil.copy(file, absolute_path)
        self._pytest_html_extras.append(pytest_html.extras.url(str(relative_path), name))
        return relative_path

    def attach_text(self, contents: str, name: str = 'Text', compress: bool = False):
        extension = '.txt'
        if compress:
            extension += '.gz'
            name += '.gz'
        relative_path = self._new_relative_file_path(extension)
        absolute_path = self._absolute_path(relative_path)
        if compress:
            with gzip.open(absolute_path, 'wt', encoding='utf-8') as f:
                f.write(contents)
        else:
            absolute_path.write_text(contents, encoding='utf-8')
        self._pytest_html_extras.append(pytest_html.extras.url(str(relative_path), name))

    def _new_relative_file_path(self, extension: str) -> Path:
        """
        Unique file path to store an attachment, relative to report dir.
        """
        self._attachment_counter += 1
        filename = f'{self._file_prefix}_{self._attachment_counter}{extension}'
        return Path(FileExtras.dir_name) / filename

    def _absolute_path(self, relative: Path) -> Path:
        """
        Resolve path relative from report dir to absolute.
        """
        return self._report_dir / relative


def get_extras(extras: list, config: Config, node: Node) -> PassthroughExtras | FileExtras | NoopExtras:
    report_html = config.getoption('htmlpath', default=None)
    self_contained = config.getoption('self_contained_html', default=False)

    if report_html:
        if self_contained:
            value = PassthroughExtras(extras)
        else:
            report_dir = Path(report_html).parent
            value = FileExtras(node, extras, report_dir)
    else:
        value = NoopExtras()

    return value
