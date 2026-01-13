#
# This is an auto-generated file.  DO NOT EDIT!
#

SHASH = "5752cfcb125c06b52c7d98fc8d1287154da25832c24c95eb0a98d3876d385b47"

from ansys.systemcoupling.core.adaptor.impl.types import *

from ._solve import _solve
from .abort import abort
from .connect_ensight_dvs import connect_ensight_dvs
from .create_restart_point import create_restart_point
from .get_machines import get_machines
from .get_transformation import get_transformation
from .initialize import initialize
from .interrupt import interrupt
from .map import map
from .open_results_in_ensight import open_results_in_ensight
from .partition_participants import partition_participants
from .show_plot import show_plot
from .shutdown import shutdown
from .solve import solve
from .step import step
from .update_interfaces import update_interfaces
from .write_csv_chart_files import write_csv_chart_files
from .write_ensight import write_ensight
from .write_target_data import write_target_data


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
        "map",
        "open_results_in_ensight",
        "partition_participants",
        "show_plot",
        "shutdown",
        "solve",
        "step",
        "update_interfaces",
        "write_csv_chart_files",
        "write_ensight",
        "write_target_data",
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
    map: map = map
    """
    map command of solution_root.
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
    step: step = step
    """
    step command of solution_root.
    """
    update_interfaces: update_interfaces = update_interfaces
    """
    update_interfaces command of solution_root.
    """
    write_csv_chart_files: write_csv_chart_files = write_csv_chart_files
    """
    write_csv_chart_files command of solution_root.
    """
    write_ensight: write_ensight = write_ensight
    """
    write_ensight command of solution_root.
    """
    write_target_data: write_target_data = write_target_data
    """
    write_target_data command of solution_root.
    """
