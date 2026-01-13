#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class instancing_child(Container):
    """
    Define instancing for an interface side.

    Available when cylindrical geometry instancing has been added to
    the data model.

    ``RotationAxis`` controls how the axis of rotation is defined.
    """

    syc_name = "child_object_type"

    property_names_types = [
        ("rotation_axis", "RotationAxis", "str"),
        ("instances_in_full_circle", "InstancesInFullCircle", "int"),
        ("instances_for_mapping", "InstancesForMapping", "int"),
        ("reference_frame", "ReferenceFrame", "str"),
        ("axis", "Axis", "str"),
        ("axis_from", "AxisFrom", "RealVectorType"),
        ("axis_to", "AxisTo", "RealVectorType"),
        ("rotational_offset", "RotationalOffset", "RealType"),
    ]

    @property
    def rotation_axis(self) -> str:
        """UNDOCUMENTED"""
        return self.get_property_state("rotation_axis")

    @rotation_axis.setter
    def rotation_axis(self, value: str):
        self.set_property_state("rotation_axis", value)

    @property
    def instances_in_full_circle(self) -> int:
        """Total number of instances (including the first instance) in
        a full 360 degree rotation of the participant mesh. This value
        includes the reference instance (with the participant mesh).
        All instances defined for the instancing object have identical
        angles."""
        return self.get_property_state("instances_in_full_circle")

    @instances_in_full_circle.setter
    def instances_in_full_circle(self, value: int):
        self.set_property_state("instances_in_full_circle", value)

    @property
    def instances_for_mapping(self) -> int:
        """Number of instances to be included in the mapping when instancing
        is applied.

        Required when the number of instances to be used for mapping does
        not match the number of instances in a full circle. Default
        assumes a 360 degree rotation of the participant mesh. This value
        includes the reference instance (with the participant mesh)."""
        return self.get_property_state("instances_for_mapping")

    @instances_for_mapping.setter
    def instances_for_mapping(self, value: int):
        self.set_property_state("instances_for_mapping", value)

    @property
    def reference_frame(self) -> str:
        """Reference frame that defines the orientation of the instancing.

        Rotation will be around the z-axis of the reference frame,
        following the right-hand rule."""
        return self.get_property_state("reference_frame")

    @reference_frame.setter
    def reference_frame(self, value: str):
        self.set_property_state("reference_frame", value)

    @property
    def axis(self) -> str:
        """Principal axis of rotation for instancing"""
        return self.get_property_state("axis")

    @axis.setter
    def axis(self, value: str):
        self.set_property_state("axis", value)

    @property
    def axis_from(self) -> RealVectorType:
        """Define the starting point of a user-defined axis."""
        return self.get_property_state("axis_from")

    @axis_from.setter
    def axis_from(self, value: RealVectorType):
        self.set_property_state("axis_from", value)

    @property
    def axis_to(self) -> RealVectorType:
        """Define the end point of a user-defined axis."""
        return self.get_property_state("axis_to")

    @axis_to.setter
    def axis_to(self, value: RealVectorType):
        self.set_property_state("axis_to", value)

    @property
    def rotational_offset(self) -> RealType:
        """Offset (in radians) about the rotation axis for the first instance"""
        return self.get_property_state("rotational_offset")

    @rotational_offset.setter
    def rotational_offset(self, value: RealType):
        self.set_property_state("rotational_offset", value)
