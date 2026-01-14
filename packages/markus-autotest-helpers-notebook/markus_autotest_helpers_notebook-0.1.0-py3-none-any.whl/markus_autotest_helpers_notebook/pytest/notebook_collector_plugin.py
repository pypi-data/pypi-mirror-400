"""Pytest plugin for collecting tests from Jupyter notebooks."""

import pytest
from ..importer import import_from_path, get_cells
import re
import traceback

__all__ = [
    'pytest_collect_file',
    'IpynbFile',
    'IpynbItem'
]


try:
    PYTEST_VERSION = tuple(int(x) for x in pytest.__version__.split('.'))
except Exception:
    PYTEST_VERSION = (0, 0, 0)


if PYTEST_VERSION >= (7, 0, 0):
    def pytest_collect_file(file_path, path, parent):
        """pytest hook.

        Create a Collector for the given path, or None if not relevant.

        The new node needs to have the specified parent as a parent.
        """
        if path.ext == ".ipynb":
            return IpynbFile.from_parent(parent, path=file_path)
else:
    def pytest_collect_file(path, parent):
        """pytest hook.

        Create a Collector for the given path, or None if not relevant.

        The new node needs to have the specified parent as a parent.
        """
        if path.ext == ".ipynb":
            return IpynbFile.from_parent(parent, fspath=path)


class IpynbFile(pytest.File):
    TEST_PATTERN = re.compile(r"(?i)^\s*#+\s*(test.*?)\s*$")

    def collect(self):
        mod = import_from_path(self.fspath)
        setup_cells = []
        for cell in get_cells(mod):
            lines = cell.source.splitlines() or [""]  # dummy list so the next line works
            match = re.match(self.TEST_PATTERN, lines[0])
            if match and match.group(1):
                yield IpynbItem.from_parent(self, name=match.group(1), test_cell=cell, setup_cells=setup_cells, mod=mod)
                setup_cells = []
            else:
                setup_cells.append(cell)


class IpynbItem(pytest.Item):
    def __init__(self, name, parent, test_cell, setup_cells, mod):
        super().__init__(name, parent)
        self.test_cell = test_cell
        self.setup_cells = setup_cells
        self.mod = mod
        self._last_cell = None

    def runtest(self) -> None:
        for cell in self.setup_cells:
            self._last_cell = cell
            # Skip cell if markus "skip": True metdata is set
            if 'markus' in cell.metadata and cell.metadata.markus.get('skip', True):
                continue

            cell.run()
        self._last_cell = self.test_cell
        self.test_cell.run()

    @property
    def obj(self):
        return self.test_cell

    def repr_failure(self, excinfo, style=None):
        try:
            for tb in reversed(excinfo.traceback):
                if excinfo.typename == "SyntaxError" or str(tb.frame.code.path).startswith(self.mod.__file__):
                    err_line = tb.lineno
                    cell_lines = [
                        f"-> {l}" if i == err_line else f"   {l}"
                        for i, l in enumerate("".join(self._last_cell.source).splitlines())
                    ]

                    if self._last_cell is self.test_cell:
                        if excinfo.typename == "AssertionError":
                            header = "Failure in test cell:"
                        else:
                            header = "Error in test cell:"
                    else:
                        header = "Test cell was not executed because an earlier cell raised an error:"
                    lines = "\n".join(cell_lines)
                    return f"{header}\n\n{lines}\n\n{excinfo.exconly()}"
        except Exception:
            return f"Error when reporting test failure for {self.name}:\n{traceback.format_exc()}"

    def reportinfo(self):
        return self.fspath, None, f"Test cell: {self.name}"
