#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .execution_control_1 import execution_control


class live_visualization_child(Container):
    """
    Configures live visualization via EnSight DVS.
    """

    syc_name = "child_object_type"

    child_names = ["execution_control"]

    execution_control: execution_control = execution_control
    """
    execution_control child of live_visualization_child.
    """
    property_names_types = [
        ("option", "Option", "str"),
        ("write_results", "WriteResults", "bool"),
        ("start_grpc_server", "StartGrpcServer", "bool"),
        ("hide_ensight_gui", "HideEnsightGUI", "bool"),
        ("output_frequency", "OutputFrequency", "int"),
    ]

    @property
    def option(self) -> str:
        """Specifies live visualization working process

        Allowed values:

        - \"ProgramControlled\" - Generation of postprocessing results is disabled for now.

        -  \"Off\" - Generation of postprocessing results is disabled.

        Allowed values for step-based analyses:

        - \"LastStep\" - Generate results only for the last coupling step completed.

        - \"EveryStep\" - Generate results at the end of every coupling step.

        - \"StepInterval\" - Generate results at the end of coupling steps at
          the interval specified by the output frequency setting.

        Allowed values for iteration-based analyses:

        - \"LastIteration\" - Generate results only for the last coupling
          iteration completed.

        - \"EveryIteration\" - Generate results at the end of every coupling
          iteration.

        - \"IterationInterval\" - Generate results at the end of coupling
          iterations at the interval specified by the output frequency setting."""
        return self.get_property_state("option")

    @option.setter
    def option(self, value: str):
        self.set_property_state("option", value)

    @property
    def write_results(self) -> bool:
        """Write results to files when conducting live visualization."""
        return self.get_property_state("write_results")

    @write_results.setter
    def write_results(self, value: bool):
        self.set_property_state("write_results", value)

    @property
    def start_grpc_server(self) -> bool:
        """Request that the EnSight client is started with a gRPC server running."""
        return self.get_property_state("start_grpc_server")

    @start_grpc_server.setter
    def start_grpc_server(self, value: bool):
        self.set_property_state("start_grpc_server", value)

    @property
    def hide_ensight_gui(self) -> bool:
        """Request that the EnSight client is started hidden (in batch mode)."""
        return self.get_property_state("hide_ensight_gui")

    @hide_ensight_gui.setter
    def hide_ensight_gui(self, value: bool):
        self.set_property_state("hide_ensight_gui", value)

    @property
    def output_frequency(self) -> int:
        """Specify output frequency."""
        return self.get_property_state("output_frequency")

    @output_frequency.setter
    def output_frequency(self, value: int):
        self.set_property_state("output_frequency", value)
