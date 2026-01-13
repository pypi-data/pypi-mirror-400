#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .fluent_input import fluent_input


class execution_control(Container):
    """
    Configure execution control for a coupling participant.
    """

    syc_name = "ExecutionControl"

    child_names = ["fluent_input"]

    fluent_input: fluent_input = fluent_input
    """
    fluent_input child of execution_control.
    """
    property_names_types = [
        ("option", "Option", "str"),
        ("working_directory", "WorkingDirectory", "str"),
        ("use_wrapper_script", "UseWrapperScript", "bool"),
        ("python_script", "PythonScript", "str"),
        ("executable", "Executable", "str"),
        ("auto_distribution_settings", "AutoDistributionSettings", "bool"),
        ("use_ls_dyna_custom_executable", "UseLsDynaCustomExecutable", "bool"),
        ("ls_dyna_custom_executable", "LsDynaCustomExecutable", "str"),
        ("ls_dyna_parallel_option", "LsDynaParallelOption", "str"),
        (
            "include_hpc_distribution_types",
            "IncludeHPCDistributionTypes",
            "StringListType",
        ),
        ("number_of_cores_per_task", "NumberOfCoresPerTask", "int"),
        ("batch_options", "BatchOptions", "str"),
        ("additional_arguments", "AdditionalArguments", "str"),
        ("parallel_fraction", "ParallelFraction", "RealType"),
        ("initial_input", "InitialInput", "str"),
        ("additional_restart_input_file", "AdditionalRestartInputFile", "str"),
        ("gui_mode", "GuiMode", "bool"),
        ("base_output_file_name", "BaseOutputFileName", "str"),
        ("overwrite_existing_files", "OverwriteExistingFiles", "bool"),
        ("mass_normalized", "MassNormalized", "bool"),
        ("write_output", "WriteOutput", "bool"),
        ("environment_variables", "EnvironmentVariables", "StringListType"),
        ("precision", "Precision", "str"),
    ]

    @property
    def option(self) -> str:
        """Method used to find the solver executable file to be used to start
        the participant.

        - \"ProgramControlled\" - (Default) Find the executable based on the
          participant type. Available whenever the participant type is not
          set to \"DEFAULT\" or \"EXTERNALDATA\".
        - \"UserDefined\" - User supplied settings are used to find the executable.
        - \"ExternallyManaged\" - Typically used for workflows managed by
          `WorkBench`."""
        return self.get_property_state("option")

    @option.setter
    def option(self, value: str):
        self.set_property_state("option", value)

    @property
    def working_directory(self) -> str:
        """Participant working directory."""
        return self.get_property_state("working_directory")

    @working_directory.setter
    def working_directory(self, value: str):
        self.set_property_state("working_directory", value)

    @property
    def use_wrapper_script(self) -> bool:
        """Specify whether to use System Coupling-provided wrapper script to set up the environment."""
        return self.get_property_state("use_wrapper_script")

    @use_wrapper_script.setter
    def use_wrapper_script(self, value: bool):
        self.set_property_state("use_wrapper_script", value)

    @property
    def python_script(self) -> str:
        """Path to the Python script."""
        return self.get_property_state("python_script")

    @python_script.setter
    def python_script(self, value: str):
        self.set_property_state("python_script", value)

    @property
    def executable(self) -> str:
        """Path to participant executable."""
        return self.get_property_state("executable")

    @executable.setter
    def executable(self, value: str):
        self.set_property_state("executable", value)

    @property
    def auto_distribution_settings(self) -> bool:
        """Specify whether to use automatic distribution settings."""
        return self.get_property_state("auto_distribution_settings")

    @auto_distribution_settings.setter
    def auto_distribution_settings(self, value: bool):
        self.set_property_state("auto_distribution_settings", value)

    @property
    def use_ls_dyna_custom_executable(self) -> bool:
        """Specify whether to use custom executable for LS-DYNA."""
        return self.get_property_state("use_ls_dyna_custom_executable")

    @use_ls_dyna_custom_executable.setter
    def use_ls_dyna_custom_executable(self, value: bool):
        self.set_property_state("use_ls_dyna_custom_executable", value)

    @property
    def ls_dyna_custom_executable(self) -> str:
        """Path to LS-DYNA executable."""
        return self.get_property_state("ls_dyna_custom_executable")

    @ls_dyna_custom_executable.setter
    def ls_dyna_custom_executable(self, value: str):
        self.set_property_state("ls_dyna_custom_executable", value)

    @property
    def ls_dyna_parallel_option(self) -> str:
        """LS-DYNA Parallel Option."""
        return self.get_property_state("ls_dyna_parallel_option")

    @ls_dyna_parallel_option.setter
    def ls_dyna_parallel_option(self, value: str):
        self.set_property_state("ls_dyna_parallel_option", value)

    @property
    def include_hpc_distribution_types(self) -> StringListType:
        """Include HPC distribution types for the distributed AEDT runs."""
        return self.get_property_state("include_hpc_distribution_types")

    @include_hpc_distribution_types.setter
    def include_hpc_distribution_types(self, value: StringListType):
        self.set_property_state("include_hpc_distribution_types", value)

    @property
    def number_of_cores_per_task(self) -> int:
        """Specify number of parallel cores per task for parallel AEDT analysis."""
        return self.get_property_state("number_of_cores_per_task")

    @number_of_cores_per_task.setter
    def number_of_cores_per_task(self, value: int):
        self.set_property_state("number_of_cores_per_task", value)

    @property
    def batch_options(self) -> str:
        """Specify batch options for AEDT participant."""
        return self.get_property_state("batch_options")

    @batch_options.setter
    def batch_options(self, value: str):
        self.set_property_state("batch_options", value)

    @property
    def additional_arguments(self) -> str:
        """Additional command line arguments."""
        return self.get_property_state("additional_arguments")

    @additional_arguments.setter
    def additional_arguments(self, value: str):
        self.set_property_state("additional_arguments", value)

    @property
    def parallel_fraction(self) -> RealType:
        """Fraction of available cores to use for this participant"""
        return self.get_property_state("parallel_fraction")

    @parallel_fraction.setter
    def parallel_fraction(self, value: RealType):
        self.set_property_state("parallel_fraction", value)

    @property
    def initial_input(self) -> str:
        """Initial input."""
        return self.get_property_state("initial_input")

    @initial_input.setter
    def initial_input(self, value: str):
        self.set_property_state("initial_input", value)

    @property
    def additional_restart_input_file(self) -> str:
        """File containing MAPDL command snippets to modify the restarted run."""
        return self.get_property_state("additional_restart_input_file")

    @additional_restart_input_file.setter
    def additional_restart_input_file(self, value: str):
        self.set_property_state("additional_restart_input_file", value)

    @property
    def gui_mode(self) -> bool:
        """Run participant in graphical mode."""
        return self.get_property_state("gui_mode")

    @gui_mode.setter
    def gui_mode(self, value: bool):
        self.set_property_state("gui_mode", value)

    @property
    def base_output_file_name(self) -> str:
        """Base output file name for the CFD Server or SCDT Server."""
        return self.get_property_state("base_output_file_name")

    @base_output_file_name.setter
    def base_output_file_name(self, value: str):
        self.set_property_state("base_output_file_name", value)

    @property
    def overwrite_existing_files(self) -> bool:
        """Flag indicating whether CFD Server should overwrite existing files."""
        return self.get_property_state("overwrite_existing_files")

    @overwrite_existing_files.setter
    def overwrite_existing_files(self, value: bool):
        self.set_property_state("overwrite_existing_files", value)

    @property
    def mass_normalized(self) -> bool:
        """Controls whether mode shapes are mass normalized"""
        return self.get_property_state("mass_normalized")

    @mass_normalized.setter
    def mass_normalized(self, value: bool):
        self.set_property_state("mass_normalized", value)

    @property
    def write_output(self) -> bool:
        """Controls whether export scdt files for the SCDT Server"""
        return self.get_property_state("write_output")

    @write_output.setter
    def write_output(self, value: bool):
        self.set_property_state("write_output", value)

    @property
    def environment_variables(self) -> StringListType:
        """Additional unique environment variables for this participant."""
        return self.get_property_state("environment_variables")

    @environment_variables.setter
    def environment_variables(self, value: StringListType):
        self.set_property_state("environment_variables", value)

    @property
    def precision(self) -> str:
        """Set precision for this participant"""
        return self.get_property_state("precision")

    @precision.setter
    def precision(self, value: str):
        self.set_property_state("precision", value)
