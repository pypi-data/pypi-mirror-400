#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class automatic_alignment_options(Container):
    """
    Automatic alignment settings.
    """

    syc_name = "AutomaticAlignmentOptions"

    property_names_types = [
        ("alignment_type", "AlignmentType", "str"),
        ("singular_value_tolerance", "SingularValueTolerance", "RealType"),
        ("verbosity", "Verbosity", "int"),
    ]

    @property
    def alignment_type(self) -> str:
        """Alignment type (\"Covariance\" or \"Moment Covariance\" or \"Inertial Axes\")."""
        return self.get_property_state("alignment_type")

    @alignment_type.setter
    def alignment_type(self, value: str):
        self.set_property_state("alignment_type", value)

    @property
    def singular_value_tolerance(self) -> RealType:
        """Tolerance used to compare singular values"""
        return self.get_property_state("singular_value_tolerance")

    @singular_value_tolerance.setter
    def singular_value_tolerance(self, value: RealType):
        self.set_property_state("singular_value_tolerance", value)

    @property
    def verbosity(self) -> int:
        """Set to 1 to print additional information about the alignment"""
        return self.get_property_state("verbosity")

    @verbosity.setter
    def verbosity(self, value: int):
        self.set_property_state("verbosity", value)
