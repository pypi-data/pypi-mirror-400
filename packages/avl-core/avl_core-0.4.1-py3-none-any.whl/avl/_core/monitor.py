# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Monitor


from .component import Component
from .port import Port


class Monitor(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initialize the Monitor instance.

        :param name: Name of the monitor.
        :type name: str
        :param parent: Parent component.
        :type parent: Component
        """
        super().__init__(name, parent)
        self.item_export = Port("item_export", self)

__all__ = ["Monitor"]
