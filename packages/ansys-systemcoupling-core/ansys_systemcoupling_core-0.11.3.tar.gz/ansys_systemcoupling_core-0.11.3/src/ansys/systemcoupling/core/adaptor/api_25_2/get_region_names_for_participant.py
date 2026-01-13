#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class get_region_names_for_participant(Command):
    """
    This query is deprecated and will be deleted in future releases.
    To get region names for a participant, you can use ``get_child_names``
    query, for example:

    ``setup.coupling_participant[name].region.get_child_names()```

    Parameters
    ----------
    participant_name : str
        Name of the participant.

    """

    syc_name = "GetRegionNamesForParticipant"

    argument_names = ["participant_name"]

    class participant_name(String):
        """
        Name of the participant.
        """

        syc_name = "ParticipantName"
