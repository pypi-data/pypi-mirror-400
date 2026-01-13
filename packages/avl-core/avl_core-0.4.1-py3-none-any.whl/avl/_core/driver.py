# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Driver


from .component import Component
from .list import List


class Driver(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initialize Driver.

        :param name: Name of the driver.
        :type name: str
        :param parent: Parent component.
        :type parent: Component
        """
        super().__init__(name, parent)
        self.seq_item_port = List()

__all__ = ["Driver"]
