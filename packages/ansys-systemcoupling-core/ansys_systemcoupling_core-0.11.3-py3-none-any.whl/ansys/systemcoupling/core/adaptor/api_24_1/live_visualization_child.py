#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class live_visualization_child(Container):
    """
    Configures live visualization via EnSight DVS.
    """

    syc_name = "child_object_type"

    property_names_types = [
        ("option", "Option", "str"),
        ("write_results", "WriteResults", "bool"),
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
    def output_frequency(self) -> int:
        """Specify output frequency."""
        return self.get_property_state("output_frequency")

    @output_frequency.setter
    def output_frequency(self, value: int):
        self.set_property_state("output_frequency", value)
