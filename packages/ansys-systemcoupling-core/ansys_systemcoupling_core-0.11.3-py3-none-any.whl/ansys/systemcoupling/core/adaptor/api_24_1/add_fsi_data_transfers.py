#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class add_fsi_data_transfers(Command):
    """
    Adds group of data transfers for FSI physics.

    Returns the list of the data transfers created.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface on which the data transfer
        is to be created.

    """

    syc_name = "AddFSIDataTransfers"

    argument_names = ["interface"]

    class interface(String):
        """
        String indicating the name of the interface on which the data transfer
        is to be created.
        """

        syc_name = "Interface"
