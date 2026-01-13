# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Agent

from .component import Component


class Agent(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initialize the avl_agent instance.

        :param name: Name of the agent instance
        :type name: str
        :param parent: Parent component
        :type parent: Component
        """
        super().__init__(name, parent)

__all__ = ["Agent"]
