import nbformat
from nbformat import NotebookNode
from typing import Union


def _load_notebook(notebook: Union[str, NotebookNode]) -> NotebookNode:
    if isinstance(notebook, str):
        with open(notebook, encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

    assert notebook["nbformat"] >= 4
    assert notebook["nbformat_minor"] >= 4

    return notebook


def merge(notebook1: Union[str, NotebookNode], notebook2: Union[str, NotebookNode]) -> NotebookNode:
    """
    Return a notebook created from merging notebook2 into notebook1.

    This new notebook will be created by selecting cells from notebook1 and notebook2 in the following way:
        1. if a cell in notebook1 has the same id as a cell in notebook2:
            the cell in notebook2 and any preceding cells that have not yet been added to the new notebook
            will be appended to the new notebook.
        2. if a cell occurs in notebook1 and there is no corresponding cell with the same id in notebook2:
            the cell in notebook1 will be appended to the new notebook
        3. repeat steps 1 and 2 until all cells in notebook1 have been considered.
        4. if there remain any cells in notebook2 that have not been added to the new notebook, these cells
           appended to the new notebook
    """

    notebook1 = _load_notebook(notebook1)
    notebook2 = _load_notebook(notebook2)

    nb2_ids = {cell.id: i for i, cell in enumerate(notebook2.cells, start=1)}

    new_notebook = nbformat.v4.new_notebook()
    new_notebook.metadata = notebook1.metadata
    seen_ids = set()

    for cell in notebook1.cells:
        to_add = notebook2.cells[: nb2_ids.get(cell.id, 0)] or [cell]
        for add_cell in to_add:
            if add_cell.id not in seen_ids:
                seen_ids.add(add_cell.id)
                new_notebook.cells.append(add_cell)
    for cell in notebook2.cells:
        if cell.id not in seen_ids:
            new_notebook.cells.append(cell)
    return new_notebook


def check(notebook1: Union[str, NotebookNode], notebook2: Union[str, NotebookNode]) -> None:
    """
    Check if two notebooks can be merged (using the merge function) by checking if:
        - they share any cells with the same ids
        - the cells that they share (have the same ids) are in the same order in each notebook.

    If either condition above is false, an error will be raised.
    """
    notebook1 = _load_notebook(notebook1)
    notebook2 = _load_notebook(notebook2)

    nb1_ids = [cell.id for cell in notebook1.cells]
    nb2_ids = [cell.id for cell in notebook2.cells]

    shared_ids = set(nb1_ids).intersection(nb2_ids)

    if not shared_ids:
        raise Exception('Notebooks do not share any cell ids')
    if sorted(shared_ids, key=nb1_ids.index) != sorted(shared_ids, key=nb2_ids.index):
        raise Exception('Notebooks have shared cells in different orders')
