#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class update_interfaces(Command):
    """
    Command to apply transformation and instance defined in the interfaces.
    And display mapping mesh with the transformation and instance applied in the
    System Coupling viewer.

    The purpose of this command is to visually confirm the correctness of coupling
    interfaces definition, alignment and instancing settings, and to allow modifying
    those settings to fix any issues ("nudge" the alignment, etc.)
    """

    syc_name = "UpdateInterfaces"
