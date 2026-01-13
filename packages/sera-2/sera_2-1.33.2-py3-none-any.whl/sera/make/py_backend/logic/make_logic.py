from __future__ import annotations

from typing import Sequence

from sera.make.py_backend.logic.make_create_logic import make_python_create_logic
from sera.make.py_backend.logic.make_logic_graph import make_python_logic_graph
from sera.make.py_backend.logic.make_search_logic import make_python_search_logic
from sera.make.py_backend.logic.make_update_logic import make_python_update_logic
from sera.models import App, DataCollection


def make_python_logic(app: App, collections: Sequence[DataCollection]):
    """Make the basic structure for the logic."""
    app.logic.ensure_exists()

    for collection in collections:
        make_python_create_logic(collection, app.logic)
        make_python_update_logic(collection, app.logic)
        make_python_search_logic(collection, app.logic)

    # Generate digraph.py after all collection logic modules are created
    make_python_logic_graph(app, collections)
