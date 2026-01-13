#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_mode_shape_variables(Command):
    """
    Given an interface name, returns a list of mode shape variables available
    from the MECH-SRV participant.

    Parameters
    ----------
    interface : str
        String indicating the name of the interface.

    """

    syc_name = "GetModeShapeVariables"

    argument_names = ["interface"]

    class interface(String):
        """
        String indicating the name of the interface.
        """

        syc_name = "Interface"
