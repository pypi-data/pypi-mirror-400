#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class write_target_data(Command):
    """
    Command to write target data for target participant after mapping operation.

    The purpose of this command is to write target mesh and target mapped data in
    the target participant working directory and thus mapping results from SystemCoupling can
    be check in the target participant.

    Parameters
    ----------
    overwrite : bool, optional
        Flag indicating whether to overwrite the existing target data file. Default value is False.

    """

    syc_name = "WriteTargetData"

    argument_names = ["overwrite"]

    class overwrite(Boolean):
        """
        Flag indicating whether to overwrite the existing target data file. Default value is False.
        """

        syc_name = "Overwrite"
