# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Indexed Scoreboard

from typing import Any

from .component import Component
from .scoreboard import Scoreboard


class IndexedScoreboard(Scoreboard):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initializes the indexed scoreboard component.

        :param name: Name of the indexed scoreboard.
        :type name: str
        :param parent: Parent component.
        :type parent: Component
        """
        super().__init__(name, parent)
        self.scoreboards = {}

    def set_indices(self, indices: list[Any]) -> None:
        """
        Sets the indices for the scoreboards.

        :param indices: List of indices.
        :type indices: list[Any]
        """
        for idx in indices:
            self.scoreboards[idx] = Scoreboard(f"{self.name}_{idx}", self)
            self.scoreboards[idx].set_verbose(self.verbose)
            self.scoreboards[idx].set_min_compare_count(self.min_compare_count)

    def set_verbose(self, verbose: bool) -> None:
        """
        Sets the verbosity of the scoreboards.

        :param verbose: Verbosity flag.
        :type verbose: bool
        """
        super().set_verbose(verbose)
        for v in self.scoreboards.values():
            v.set_verbose(verbose)

    def set_min_compare_count(self, count: int) -> None:
        """
        Sets the minimum number of comparisons required for the scoreboards.

        :param count: Minimum number of comparisons.
        :type count: int
        """
        super().set_min_compare_count(count)
        for v in self.scoreboards.values():
            v.set_min_compare_count(count)

    def get_index(self, item: Any) -> int:
        """
        Gets the index for the given item.

        :param item: The item to get the index for.
        :type item: Any
        :returns: The index of the item.
        :rtype: int
        """
        raise NotImplementedError

    async def run_phase(self) -> None:
        """
        Runs the scoreboard phase.
        """
        while True:
            self.before_item = await self.before_port.blocking_pop()
            self.scoreboards[self.get_index(self.before_item)].before_port.append(self.before_item)

            self.after_item = await self.after_port.blocking_pop()
            self.scoreboards[self.get_index(self.after_item)].after_port.append(self.after_item)

            self.compare_count += 1

            self.after_item = None
            self.before_item = None


__all__ = ["IndexedScoreboard"]
