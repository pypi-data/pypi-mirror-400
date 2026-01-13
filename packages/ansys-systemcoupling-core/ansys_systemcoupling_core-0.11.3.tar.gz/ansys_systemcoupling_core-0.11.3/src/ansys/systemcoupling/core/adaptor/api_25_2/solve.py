#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class solve(InjectedCommand):
    """
    Solves the coupled analysis. This command will execute until
    end coupled analysis is reached, or it is interrupted or aborted
    (for example, via scStop file).

    Disabled when a solution is already in progress.

    For restarts, the ``open`` command must be run before the ``solve`` command.

    Note that if the ``execution_control.option`` for a participant is set to
    "ExternallyManaged", then System Coupling will not start the participant
    using either this command or any of the other commands that automatically
    start participants. The user is expected to manually start the participant.
    This function will not return until all participants have been connected.

    Note that this command will raise an exception if another instance of
    System Coupling is solving in the current working directory.
    """

    syc_name = "solve"

    cmd_name = "solve"
