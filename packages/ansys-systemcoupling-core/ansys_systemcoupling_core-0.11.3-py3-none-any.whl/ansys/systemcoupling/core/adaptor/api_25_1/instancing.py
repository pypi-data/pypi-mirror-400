#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .instancing_child import instancing_child


class instancing(NamedContainer[instancing_child]):
    """
    Define instancing for an interface side.

    Available when cylindrical geometry instancing has been added to
    the data model.

    ``RotationAxis`` controls how the axis of rotation is defined.
    """

    syc_name = "Instancing"

    child_object_type: instancing_child = instancing_child
    """
    child_object_type of instancing.
    """
