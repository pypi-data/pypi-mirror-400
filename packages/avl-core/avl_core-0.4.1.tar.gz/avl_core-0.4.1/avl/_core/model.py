# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Model

from .component import Component
from .list import List
from .port import Port


class Model(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initialize the AVL model component.

        :param name: Name of the model.
        :type name: str
        :param parent: Parent component of the model.
        :type parent: Component
        """
        super().__init__(name, parent)
        self.item_port = List()
        self.item_export = Port("item_export", self)


__all__ = ["Model"]
