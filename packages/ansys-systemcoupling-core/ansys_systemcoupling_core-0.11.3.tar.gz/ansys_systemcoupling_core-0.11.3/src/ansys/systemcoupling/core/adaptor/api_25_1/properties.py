#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class properties(Container):
    """
    UNDOCUMENTED
    """

    syc_name = "Properties"

    property_names_types = [
        ("accepts_new_inputs", "AcceptsNewInputs", "bool"),
        ("time_integration", "TimeIntegration", "str"),
    ]

    @property
    def accepts_new_inputs(self) -> bool:
        """Controls whether participant accept new input variables or parameters."""
        return self.get_property_state("accepts_new_inputs")

    @accepts_new_inputs.setter
    def accepts_new_inputs(self, value: bool):
        self.set_property_state("accepts_new_inputs", value)

    @property
    def time_integration(self) -> str:
        """Coupling participant time integration method (\"Implicit\" or \"Explicit\")"""
        return self.get_property_state("time_integration")

    @time_integration.setter
    def time_integration(self, value: str):
        self.set_property_state("time_integration", value)
