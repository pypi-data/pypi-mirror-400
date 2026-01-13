#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class update_participant(Command):
    """
    Given the name of a participant, updates the state of the participant.

    Available for DEFAULT-SRV, CFD-SRV, MECH-SRV, and SCDT-SRV and
    AEDT participants.

    As part of the update, System Coupling updates all regions, variables,
    and parameters defined in the participant, including all variable
    attributes. Regions, variables, and parameters may be added to the
    participant but may not be removed.

    You may specify an input file using an optional argument. If an input
    file is not provided, then the original input file will be reimported.

    Note: AEDT participants must be updated using an scp file.

    If the update process fails, System Coupling displays an error. In this
    case, you can either update the setup in the participant application to
    remove any issues with the update process or delete the participant
    from the analysis and then re-add it using the updated input file.

    Parameters
    ----------
    participant_name : str
        Participant name. Must be the name of an existing participant.
    input_file : str, optional
        Name of the input file for the participant to be added.
        Currently supported formats are SCP files, mechanical server
        (\*.rst) files, cfd server (\*.csv) files, and system coupling
        data server (\*.scdt/axdt/csv) files.

    """

    syc_name = "UpdateParticipant"

    argument_names = ["participant_name", "input_file"]

    class participant_name(String):
        """
        Participant name. Must be the name of an existing participant.
        """

        syc_name = "ParticipantName"

    class input_file(String):
        """
        Name of the input file for the participant to be added.
        Currently supported formats are SCP files, mechanical server
        (\*.rst) files, cfd server (\*.csv) files, and system coupling
        data server (\*.scdt/axdt/csv) files.
        """

        syc_name = "InputFile"
