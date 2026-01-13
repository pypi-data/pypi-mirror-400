# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Port

from typing import Any

from .component import Component
from .list import List


class Port(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initializes the port with a name and parent component.

        :param name: The name of the port.
        :type name: str
        :param parent: The parent component to which this port belongs.
        :type parent: Component
        """
        super().__init__(name, parent)
        self.channels = []

    def connect(self, dst_list: List) -> None:
        """
        Connects the port to a destination list.

        :param dst_list: The destination list to connect to.
        :type dst_list: List
        """
        self.channels.append(dst_list)

    def write(self, data: Any) -> None:
        """
        Writes data to the connected channels.

        :param data: The data to be written.
        """
        for c in self.channels:
            c.append(data)

    def delete(self) -> None:
        """
        Deletes the connected channels.
        """
        for c in self.channels:
            c.delete()


__all__ = ["Port"]
