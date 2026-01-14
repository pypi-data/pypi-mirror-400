import os
import re
import sys
import traceback
import types
from contextlib import contextmanager
from IPython import get_ipython
from nbformat import read
from typing import List
from IPython.core.interactiveshell import InteractiveShell
from importlib.abc import MetaPathFinder, Loader
from importlib.machinery import ModuleSpec
from importlib.util import module_from_spec


def get_cells(module):
    return module.__cells__


def run_cells(module, raise_on_error: bool = True):
    for cell in module.__cells__:
        cell.run(raise_on_error=raise_on_error)

def run_cells_by_section(module, start_section, end_section = None, raise_on_error = True):
    # Required to have a start_section (heading after the #s)
    # end_section is not required but can be given as a stopping point

    # Initiating variables
    start, end = 0, None
    prefix = None
    start_found = False

    for i, cell in enumerate(module.__cells__):
        # Only scan markdown cells for headings
        if getattr(cell, 'cell_type', None) != "markdown":
            continue

        # Scan all lines in the markdown cell
        lines = cell.source.splitlines() if cell.source else []

        for line in lines:
            if not start_found:
                # Detect start_section at the beginning of a line
                start_pattern = re.match(rf"(#+) {start_section}", line)
                if start_pattern:
                    start_found = True
                    start = i
                    prefix = start_pattern.group(1) + " "  # '#' characters + space
            else:
                # Once start is found, look for end_section
                if end_section:
                    if re.match(rf"(#+) {end_section}", line):
                        end = i
                        break
                else:
                    # Auto-stop at the next header with same prefix (ignore deeper sub-sections)
                    if re.match(rf"{prefix}", line):
                        end = i
                        break

    lst = module.__cells__[start:end]  # Creating a sublist of cells to be run

    # Run only the cells in the list
    for cell in lst:
        cell.run(raise_on_error=raise_on_error)


def import_from_path(path):
    base, _ = os.path.splitext(os.path.basename(path))
    base = base.replace(' ', '_')
    finder = NotebookFinder()
    spec = finder.find_spec(base, path=[os.path.dirname(path)])
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_notebook(fullname, path=None):
    """find a notebook, given its fully qualified name and an optional path

    This turns "foo.bar" into "foo/bar.ipynb"
    and tries turning "Foo_Bar" into "Foo Bar" if Foo_Bar
    does not exist.
    """
    name = fullname.rsplit('.', 1)[-1]
    if not path:
        path = ['']
    for d in path:
        nb_path = os.path.join(d, name + ".ipynb")
        if os.path.isfile(nb_path):
            return nb_path
        # let import Notebook_Name find "Notebook Name.ipynb"
        nb_path = nb_path.replace("_", " ")
        if os.path.isfile(nb_path):
            return nb_path


@contextmanager
def _user_ns(shell, mod):
    """
    Ensure that magics that would affect the user_ns
    actually affect the notebook module's ns
    """
    save_user_ns = shell.user_ns
    shell.user_ns = mod.__dict__
    try:
        yield
    finally:
        shell.user_ns = save_user_ns


class _DummyShell(InteractiveShell):
    def enable_gui(self, *_a, **_kw):
        """Overrides not-implemented method in superclass"""


class Cell:
    def __init__(self, cell):
        self._cell = cell

    def __str__(self):
        return str(self._cell)

    def __repr__(self):
        return f"<{self._cell.cell_type.capitalize()}Cell id={id(self)} {str(self)}>"

    def __getattr__(self, item):
        return self._cell.__getattr__(item)

    def run(self, raise_on_error: bool = True):
        """no-op"""


class CodeCell(Cell):
    def __init__(self, cell, source, mod, shell):
        super().__init__(cell)
        self._source = source
        self._mod = mod
        self._shell = shell

    def __getattr__(self, item):
        if item == 'source':
            return self._source
        return super().__getattr__(item)

    def run(self, raise_on_error: bool = True):
        """Run this code cell.

        If an error is encountered when running the cell:

            - if raise_on_error is True, the error is raised
            - if raise_on_error is False, the error's traceback is printed to stderr
              but is not raised from this method
        """
        with _user_ns(self._shell, self._mod):
            filename = f'{self._mod.__file__}'
            if hasattr(self._cell, 'id'):
                filename += f' (Cell id: {self._cell.id})'
            try:
                code = compile(self._source, filename, 'exec')
                exec(code, self._mod.__dict__)
            except Exception as e:
                if raise_on_error:
                    raise
                else:
                    # First argument is unused (included for backwards compatibility
                    # with Python 3.9 and earlier)
                    traceback.print_exception(None, value=e, tb=e.__traceback__)
                    print('', file=sys.stderr)



class NotebookModule(types.ModuleType):
    __cells__: List[Cell]


class NotebookLoader(Loader):
    """Module Loader for Jupyter Notebooks"""
    _DEFAULT_GUI = ''  # TODO: allow user to change this (maybe in a contextmanager)

    def __init__(self, path=None):
        # get_ipython works if we're in a shell environment
        # otherwise use the dummy shell
        self.shell = get_ipython() or _DummyShell.instance()
        self.path = path

    def module_repr(self, module):
        return repr(module)

    def _create_fresh_module(self, fullname):
        mod = NotebookModule(fullname)
        mod.__file__ = find_notebook(fullname, self.path)
        mod.__loader__ = self
        mod.__dict__['get_ipython'] = get_ipython
        mod.__cells__ = []
        sys.modules[fullname] = mod
        return mod

    def _transform_source(self, source):
        source_list = source.splitlines()
        for i, line in enumerate(source.splitlines()):
            if re.match(r'%(matplotlib|pylab)', line):
                source_list[i] = re.sub(r'\sinline\s*', ' ', line).strip()
        return self.shell.input_transformer_manager.transform_cell('\n'.join(source_list))

    def load_module(self, fullname):
        """
        import a notebook as a module

        DEPRECATED: for python<3.3 only
        """
        mod = self._create_fresh_module(fullname)
        self.exec_module(mod)
        return mod

    def create_module(self, spec):
        return self._create_fresh_module(spec.name)

    def exec_module(self, module):
        path = find_notebook(module.__name__, self.path)
        with open(path, encoding='utf-8') as f:
            nb = read(f, as_version=4)
        module.__cells__ = []
        with _user_ns(self.shell, module):
            for cell in nb.cells:
                if cell.cell_type == 'code':
                    code = self._transform_source(cell.source)
                    module.__cells__.append(CodeCell(cell, code, module, self.shell))
                else:
                    module.__cells__.append(Cell(cell))


class NotebookFinder(MetaPathFinder):
    """
    Module finder that locates Jupyter Notebooks
    """
    def __init__(self):
        self.loaders = {}

    def find_module(self, fullname, path=None):
        """
        import a notebook as a module

        DEPRECATED: for python<3.3 only (but still used as a helper by find_spec)
        """
        if not find_notebook(fullname, path):
            return
        key = None if path is None else tuple(path)

        if key not in self.loaders:
            self.loaders[key] = NotebookLoader(path)
        return self.loaders[key]

    def find_spec(self, fullname, path, target=None):
        mod = self.find_module(fullname, path)
        if mod is None:
            return mod
        return ModuleSpec(fullname, mod)

    def invalidate_caches(self):
        self.loaders.clear()


sys.meta_path.append(NotebookFinder())
