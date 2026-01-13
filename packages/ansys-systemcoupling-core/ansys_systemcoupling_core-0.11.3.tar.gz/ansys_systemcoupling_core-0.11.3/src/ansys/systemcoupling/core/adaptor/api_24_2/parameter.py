#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .parameter_child import parameter_child


class parameter(NamedContainer[parameter_child]):
    """
    Configure a parameter for the coupling participant.
    """

    syc_name = "Parameter"

    child_object_type: parameter_child = parameter_child
    """
    child_object_type of parameter.
    """
