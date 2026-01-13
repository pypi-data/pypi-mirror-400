#
# This is an auto-generated file.  DO NOT EDIT!
#

SHASH = "c6427eb39292f21707811cf7093268eb2b0d3d9f2780ddaf390bf51bb916e546"

from ansys.systemcoupling.core.adaptor.impl.types import *

from ._clear_state import _clear_state
from .clear_state import clear_state
from .delete_snapshot import delete_snapshot
from .get_snapshots import get_snapshots
from .open import open
from .open_snapshot import open_snapshot
from .save import save
from .save_snapshot import save_snapshot


class case_root(Container):
    """
    'root' object
    """

    syc_name = "CaseCommands"

    command_names = [
        "_clear_state",
        "clear_state",
        "delete_snapshot",
        "get_snapshots",
        "open",
        "open_snapshot",
        "save",
        "save_snapshot",
    ]

    _clear_state: _clear_state = _clear_state
    """
    _clear_state command of case_root.
    """
    clear_state: clear_state = clear_state
    """
    clear_state command of case_root.
    """
    delete_snapshot: delete_snapshot = delete_snapshot
    """
    delete_snapshot command of case_root.
    """
    get_snapshots: get_snapshots = get_snapshots
    """
    get_snapshots command of case_root.
    """
    open: open = open
    """
    open command of case_root.
    """
    open_snapshot: open_snapshot = open_snapshot
    """
    open_snapshot command of case_root.
    """
    save: save = save
    """
    save command of case_root.
    """
    save_snapshot: save_snapshot = save_snapshot
    """
    save_snapshot command of case_root.
    """
