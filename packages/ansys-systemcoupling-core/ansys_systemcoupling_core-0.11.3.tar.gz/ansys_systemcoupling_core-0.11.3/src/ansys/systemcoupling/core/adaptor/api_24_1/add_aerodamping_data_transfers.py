#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class add_aerodamping_data_transfers(Command):
    """
    Adds data transfer for each specified mode shape.

    Returns the name of the Data Transfers created.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface on which the data transfer
        is to be created.
    mode_shapes : List, optional
        List of mode shapes to transfer. If not provided, a
        data transfer is created for each available modeshape.

    """

    syc_name = "AddAerodampingDataTransfers"

    argument_names = ["interface", "mode_shapes"]

    class interface(String):
        """
        String indicating the name of the interface on which the data transfer
        is to be created.
        """

        syc_name = "Interface"

    class mode_shapes(StringList):
        """
        List of mode shapes to transfer. If not provided, a
        data transfer is created for each available modeshape.
        """

        syc_name = "ModeShapes"
