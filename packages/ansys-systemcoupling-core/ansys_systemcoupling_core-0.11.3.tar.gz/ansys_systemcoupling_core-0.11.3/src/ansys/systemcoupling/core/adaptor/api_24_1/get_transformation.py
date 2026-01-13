#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_transformation(Command):
    """
    Given an interface and side, returns the resultant transformation, in
    the form of a Python dictionary and formatted as a DataModel
    reference_frame object. If multiple transformations are aplied to the
    interface side, the composite transformation is returned.

    This command can only be invoked after the analysis
    is initialized.

    Parameters
    ----------
    interface_name : str
        Name of the interface
    side : str
        Interface side. Can be "One" or "Two".

    """

    syc_name = "GetTransformation"

    argument_names = ["interface_name", "side"]

    class interface_name(String):
        """
        Name of the interface
        """

        syc_name = "InterfaceName"

    class side(String):
        """
        Interface side. Can be "One" or "Two".
        """

        syc_name = "Side"
