#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class execution_control(Container):
    """
    Configure execution control for a live visualization.
    """

    syc_name = "ExecutionControl"

    property_names_types = [("option", "Option", "str")]

    @property
    def option(self) -> str:
        """Set behavior of this object."""
        return self.get_property_state("option")

    @option.setter
    def option(self, value: str):
        self.set_property_state("option", value)
