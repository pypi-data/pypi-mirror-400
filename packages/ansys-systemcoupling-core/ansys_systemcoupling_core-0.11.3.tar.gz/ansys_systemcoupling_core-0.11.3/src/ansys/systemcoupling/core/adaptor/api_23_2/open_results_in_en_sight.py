#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class open_results_in_en_sight(Command):
    """
    Allows for System Coupling results to be postprocessed in EnSight.

    When this command is issued, System Coupling looks for the ``results.enc``
    file in the ``SyC/results`` subdirectory of the current working directory.

    When System Coupling finds the file, it loads the file into EnSight and
    generates a confirmation message indicating that results are being opened.

    If System Coupling is unable to find the ``results.enc`` file and/or the
    EnSight executable, then it raises an error.

    The ``open_results_in_ensight`` command may be issued multiple times from the same
    instance of System Coupling. Each time the command is issued, a new
    instance of the EnSight application is opened. Any existing instances of
    EnSight remain open, both when additional instances are created and when
    System Coupling exits.

    Parameters
    ----------
    file_name : str, optional
        The basename of the EnSight case file if using a non-standard file
        name. Overrides the default file name ``results.enc``.
    file_path : str, optional
        The path to the EnSight case if using a non-standard location.
        Overrides the default path of ``SyC/results``.

    """

    syc_name = "OpenResultsInEnSight"

    argument_names = ["file_name", "file_path"]

    class file_name(String):
        """
        The basename of the EnSight case file if using a non-standard file
        name. Overrides the default file name ``results.enc``.
        """

        syc_name = "FileName"

    class file_path(String):
        """
        The path to the EnSight case if using a non-standard location.
        Overrides the default path of ``SyC/results``.
        """

        syc_name = "FilePath"
