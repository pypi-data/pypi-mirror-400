#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class add_thermal_data_transfers(Command):
    """
    Adds group of data transfers for thermal physics.

    Returns the list of the data transfers created.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface on which the data transfer
        is to be created.
    option : str, optional
        Thermal data transfer option: 'Heat Rate' (default) or
        'Heat Transfer Coefficient' (possible for surface-surface transfers).

    """

    syc_name = "AddThermalDataTransfers"

    argument_names = ["interface", "option"]

    class interface(String):
        """
        String indicating the name of the interface on which the data transfer
        is to be created.
        """

        syc_name = "Interface"

    class option(String):
        """
        Thermal data transfer option: 'Heat Rate' (default) or
        'Heat Transfer Coefficient' (possible for surface-surface transfers).
        """

        syc_name = "Option"
