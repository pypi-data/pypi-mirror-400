#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class _add_participant(Command):
    """
    For internal use only.

    Parameters
    ----------
    participant_type : str, optional
        ...
    input_file : str, optional
        ...
    executable : str, optional
        ...
    additional_arguments : str, optional
        ...
    working_directory : str, optional
        ...

    """

    syc_name = "AddParticipant"

    argument_names = [
        "participant_type",
        "input_file",
        "executable",
        "additional_arguments",
        "working_directory",
    ]

    class participant_type(String):
        """
        ...
        """

        syc_name = "ParticipantType"

    class input_file(String):
        """
        ...
        """

        syc_name = "InputFile"

    class executable(String):
        """
        ...
        """

        syc_name = "Executable"

    class additional_arguments(String):
        """
        ...
        """

        syc_name = "AdditionalArguments"

    class working_directory(String):
        """
        ...
        """

        syc_name = "WorkingDirectory"
