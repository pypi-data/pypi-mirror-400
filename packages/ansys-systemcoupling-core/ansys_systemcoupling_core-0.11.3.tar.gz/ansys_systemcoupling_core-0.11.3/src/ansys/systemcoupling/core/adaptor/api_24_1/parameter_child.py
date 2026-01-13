#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class parameter_child(Container):
    """
    Configure a parameter for the coupling participant.
    """

    syc_name = "child_object_type"

    property_names_types = [
        ("participant_display_name", "ParticipantDisplayName", "str"),
        ("display_name", "DisplayName", "str"),
        ("data_type", "DataType", "str"),
        ("tensor_type", "TensorType", "str"),
    ]

    @property
    def participant_display_name(self) -> str:
        """Parameter's display name as defined by the participant solver."""
        return self.get_property_state("participant_display_name")

    @participant_display_name.setter
    def participant_display_name(self, value: str):
        self.set_property_state("participant_display_name", value)

    @property
    def display_name(self) -> str:
        """Parameter's display name as defined in System Coupling."""
        return self.get_property_state("display_name")

    @display_name.setter
    def display_name(self, value: str):
        self.set_property_state("display_name", value)

    @property
    def data_type(self) -> str:
        """UNDOCUMENTED"""
        return self.get_property_state("data_type")

    @data_type.setter
    def data_type(self, value: str):
        self.set_property_state("data_type", value)

    @property
    def tensor_type(self) -> str:
        """Indicates the parameter tensor type (\"Scalar\" only)."""
        return self.get_property_state("tensor_type")

    @tensor_type.setter
    def tensor_type(self, value: str):
        self.set_property_state("tensor_type", value)
