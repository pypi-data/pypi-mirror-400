#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_machines(Command):
    """
    Get a list of dictionaries with machine names and core counts for
    the machines available for parallel processing.

    Returns information in the following format::

        [
            {
            'machine-name' : <machine-name-1 (str)>,
            'core-count' : <core-count-1 (int)>
            },
            {
            'machine-name' : <machine-name-2 (str)>,
            'core-count' : <core-count-2 (int)>
            },
            ...
        ]

    Returns an empty list when machines and core counts are not
    provided to System Coupling. You may specify those
    by providing --cnf command-line option when starting System
    Coupling. You can also specify those via the Parallel
    Partitioning dialog box in the System Coupling GUI.
    """

    syc_name = "GetMachines"
