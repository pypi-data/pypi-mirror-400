#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_add_data_transfer_group_commands(Command):
    """
    Given an interface name, returns a list with possible commands
    for adding data transfer groups.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface.

    """

    syc_name = "GetAddDataTransferGroupCommands"

    argument_names = ["interface"]

    class interface(String):
        """
        String indicating the name of the interface.
        """

        syc_name = "Interface"
