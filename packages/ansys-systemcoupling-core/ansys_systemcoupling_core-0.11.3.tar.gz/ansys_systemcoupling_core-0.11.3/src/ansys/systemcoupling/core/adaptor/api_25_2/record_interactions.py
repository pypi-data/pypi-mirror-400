#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class record_interactions(Container):
    """
    "Controls whether the System Coupling Participant library will record the setup and solution data files for testing and debugging.
    """

    syc_name = "RecordInteractions"

    property_names_types = [
        ("record_setup", "RecordSetup", "bool"),
        ("record_solution", "RecordSolution", "bool"),
        ("record_precision", "RecordPrecision", "int"),
    ]

    @property
    def record_setup(self) -> bool:
        """Flag indicating whether participant record scp file."""
        return self.get_property_state("record_setup")

    @record_setup.setter
    def record_setup(self, value: bool):
        self.set_property_state("record_setup", value)

    @property
    def record_solution(self) -> bool:
        """Flag indicating whether participant record solution files."""
        return self.get_property_state("record_solution")

    @record_solution.setter
    def record_solution(self, value: bool):
        self.set_property_state("record_solution", value)

    @property
    def record_precision(self) -> int:
        """Set the digital precision of solution variable,1 <= N <= 16.."""
        return self.get_property_state("record_precision")

    @record_precision.setter
    def record_precision(self, value: int):
        self.set_property_state("record_precision", value)
