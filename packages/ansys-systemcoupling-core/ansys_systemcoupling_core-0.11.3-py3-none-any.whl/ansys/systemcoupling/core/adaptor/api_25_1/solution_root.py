#
# This is an auto-generated file.  DO NOT EDIT!
#

SHASH = "0987c9ed416b22e5d86458a81cba5c65a60eb6e6a32fb2f856bf7464f995ed36"

from ansys.systemcoupling.core.adaptor.impl.types import *

from ._solve import _solve
from .abort import abort
from .connect_ensight_dvs import connect_ensight_dvs
from .create_restart_point import create_restart_point
from .get_machines import get_machines
from .get_transformation import get_transformation
from .initialize import initialize
from .interrupt import interrupt
from .open_results_in_ensight import open_results_in_ensight
from .partition_participants import partition_participants
from .show_plot import show_plot
from .shutdown import shutdown
from .solve import solve
from .start_participants import start_participants
from .step import step
from .write_csv_chart_files import write_csv_chart_files
from .write_ensight import write_ensight


class solution_root(Container):
    """
    'root' object
    """

    syc_name = "SolutionCommands"

    command_names = [
        "_solve",
        "abort",
        "connect_ensight_dvs",
        "create_restart_point",
        "get_machines",
        "get_transformation",
        "initialize",
        "interrupt",
        "open_results_in_ensight",
        "partition_participants",
        "show_plot",
        "shutdown",
        "solve",
        "start_participants",
        "step",
        "write_csv_chart_files",
        "write_ensight",
    ]

    _solve: _solve = _solve
    """
    _solve command of solution_root.
    """
    abort: abort = abort
    """
    abort command of solution_root.
    """
    connect_ensight_dvs: connect_ensight_dvs = connect_ensight_dvs
    """
    connect_ensight_dvs command of solution_root.
    """
    create_restart_point: create_restart_point = create_restart_point
    """
    create_restart_point command of solution_root.
    """
    get_machines: get_machines = get_machines
    """
    get_machines command of solution_root.
    """
    get_transformation: get_transformation = get_transformation
    """
    get_transformation command of solution_root.
    """
    initialize: initialize = initialize
    """
    initialize command of solution_root.
    """
    interrupt: interrupt = interrupt
    """
    interrupt command of solution_root.
    """
    open_results_in_ensight: open_results_in_ensight = open_results_in_ensight
    """
    open_results_in_ensight command of solution_root.
    """
    partition_participants: partition_participants = partition_participants
    """
    partition_participants command of solution_root.
    """
    show_plot: show_plot = show_plot
    """
    show_plot command of solution_root.
    """
    shutdown: shutdown = shutdown
    """
    shutdown command of solution_root.
    """
    solve: solve = solve
    """
    solve command of solution_root.
    """
    start_participants: start_participants = start_participants
    """
    start_participants command of solution_root.
    """
    step: step = step
    """
    step command of solution_root.
    """
    write_csv_chart_files: write_csv_chart_files = write_csv_chart_files
    """
    write_csv_chart_files command of solution_root.
    """
    write_ensight: write_ensight = write_ensight
    """
    write_ensight command of solution_root.
    """
