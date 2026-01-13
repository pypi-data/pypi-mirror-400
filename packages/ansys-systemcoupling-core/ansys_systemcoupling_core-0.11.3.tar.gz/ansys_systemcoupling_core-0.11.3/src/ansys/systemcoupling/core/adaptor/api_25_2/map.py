#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class map(Command):
    """
    Command to perform map operation.

    When user friendly mapping workflow is enabled, this command will perform
    the map operation between the interfaces as part of the user friendly mapping
    workflow.
    Otherwise, this operation would clears all existing state, except for datamodel,
    before beginning the operation.
    """

    syc_name = "Map"
