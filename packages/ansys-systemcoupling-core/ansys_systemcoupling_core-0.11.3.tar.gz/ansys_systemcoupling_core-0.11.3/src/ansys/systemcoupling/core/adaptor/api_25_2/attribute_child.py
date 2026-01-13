#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .dimensionality import dimensionality


class attribute_child(Container):
    """
    Configure an attribute.
    """

    syc_name = "child_object_type"

    child_names = ["dimensionality"]

    dimensionality: dimensionality = dimensionality
    """
    dimensionality child of attribute_child.
    """
    property_names_types = [
        ("attribute_type", "AttributeType", "str"),
        ("modifiable", "Modifiable", "bool"),
        ("real_value", "RealValue", "RealType"),
        ("integer_value", "IntegerValue", "int"),
        ("string_value", "StringValue", "str"),
    ]

    @property
    def attribute_type(self) -> str:
        """The type of the attribute (\"Real\", \"Integer\", or \"String\")."""
        return self.get_property_state("attribute_type")

    @attribute_type.setter
    def attribute_type(self, value: str):
        self.set_property_state("attribute_type", value)

    @property
    def modifiable(self) -> bool:
        """Controls whether the attribute is Modifiable"""
        return self.get_property_state("modifiable")

    @modifiable.setter
    def modifiable(self, value: bool):
        self.set_property_state("modifiable", value)

    @property
    def real_value(self) -> RealType:
        """Real attribute value."""
        return self.get_property_state("real_value")

    @real_value.setter
    def real_value(self, value: RealType):
        self.set_property_state("real_value", value)

    @property
    def integer_value(self) -> int:
        """Integer attribute value."""
        return self.get_property_state("integer_value")

    @integer_value.setter
    def integer_value(self, value: int):
        self.set_property_state("integer_value", value)

    @property
    def string_value(self) -> str:
        """String attribute value."""
        return self.get_property_state("string_value")

    @string_value.setter
    def string_value(self, value: str):
        self.set_property_state("string_value", value)
