#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class connect_ensight_dvs(Command):
    """
    Allow System Coupling to create DVS clients and connect these clients to
    the dvs server that is already launched in another process/thread remotely.

    When this command is issued, System Coupling is connected to remote EnSight
    and the in-situ data streaming from system coupling to EnSight is ready.

    Parameters
    ----------
    port : int, optional
        DVS Server port that System Coupling would connect to. Default value is 50055.
    host_name : str, optional
        DVS Server host name that System Coupling would connect to. Default value is "127.0.0.1".

    """

    syc_name = "ConnectEnSightDVS"

    argument_names = ["port", "host_name"]

    class port(Integer):
        """
        DVS Server port that System Coupling would connect to. Default value is 50055.
        """

        syc_name = "Port"

    class host_name(String):
        """
        DVS Server host name that System Coupling would connect to. Default value is "127.0.0.1".
        """

        syc_name = "HostName"
