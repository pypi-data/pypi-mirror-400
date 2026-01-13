#
# This is an auto-generated file.  DO NOT EDIT!
#

from ansys.systemcoupling.core.adaptor.impl.types import *

from .live_visualization_child import live_visualization_child


class live_visualization(NamedContainer[live_visualization_child]):
    """
    Configures live visualization via EnSight DVS.
    """

    syc_name = "LiveVisualization"

    child_object_type: live_visualization_child = live_visualization_child
    """
    child_object_type of live_visualization.
    """
