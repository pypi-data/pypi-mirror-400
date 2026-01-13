#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_thermal_data_transfer_options(Command):
    """
    Given an interface name, returns a list of available possible options for
    ``add_thermal_data_transfers`` given the context, and whether those
    data transfers are actually available. When only one option is conceptually
    possible (e.g., not a surface-surface transfer), the returned dictionary is
    empty.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface.

    """

    syc_name = "GetThermalDataTransferOptions"

    argument_names = ["interface"]

    class interface(String):
        """
        String indicating the name of the interface.
        """

        syc_name = "Interface"
