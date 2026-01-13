#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class generate_input_file(Command):
    """
    Generates the input journal file for a given Fluent participant.

    Available for Fluent participants when ``fluent_input.option`` is not
    set to ``journal_file``.

    Given the participant's name and a file name, generates a Fluent
    journal script which may be set as the value for the ``journal_file``
    setting.

    System Coupling uses the generated scrkpt for the coupled analysis.

    Scripts generated using this method may be edited before the
    coupled analysis is started.

    Parameters
    ----------
    participant_name : str
        Name of the participant for which the execution command will
        be returned.
    file_name : str
        Name of the journal script to be written. Note that this name is relative
        to the participant's working directory.

    """

    syc_name = "GenerateInputFile"

    argument_names = ["participant_name", "file_name"]

    class participant_name(String):
        """
        Name of the participant for which the execution command will
        be returned.
        """

        syc_name = "ParticipantName"

    class file_name(String):
        """
        Name of the journal script to be written. Note that this name is relative
        to the participant's working directory.
        """

        syc_name = "FileName"
