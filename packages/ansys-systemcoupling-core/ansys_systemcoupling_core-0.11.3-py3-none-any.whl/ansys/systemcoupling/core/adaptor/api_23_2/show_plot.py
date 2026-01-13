#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *


class show_plot(InjectedCommand):
    """
    Shows plots of transfer values and convergence for data transfers
    of a coupling interface.

    Parameters
    ----------
    interface_name : str
        Specification of which interface to plot.
    transfer_names : List, optional
        Specification of which data transfers to plot. Defaults
        to ``None``, which means plot all data transfers.
    working_dir : str, optional
        Working directory (defaults = ".").
    show_convergence : bool, optional
        Whether to show convergence plots (defaults to ``True``).
    show_transfer_values : bool, optional
        Whether to show transfer value plots (defaults to ``True``).

    """

    syc_name = "show_plot"

    cmd_name = "show_plot"

    argument_names = [
        "interface_name",
        "transfer_names",
        "working_dir",
        "show_convergence",
        "show_transfer_values",
    ]

    class interface_name(String):
        """
        Specification of which interface to plot.
        """

        syc_name = "interface_name"

    class transfer_names(StringList):
        """
        Specification of which data transfers to plot. Defaults
        to ``None``, which means plot all data transfers.
        """

        syc_name = "transfer_names"

    class working_dir(String):
        """
        Working directory (defaults = ".").
        """

        syc_name = "working_dir"

    class show_convergence(Boolean):
        """
        Whether to show convergence plots (defaults to ``True``).
        """

        syc_name = "show_convergence"

    class show_transfer_values(Boolean):
        """
        Whether to show transfer value plots (defaults to ``True``).
        """

        syc_name = "show_transfer_values"
