# Copyright 2024 Apheleia
#
# Description:
# Apheleia Verification Library Scoreboard

from .component import Component
from .list import List


class Scoreboard(Component):
    def __init__(self, name: str, parent: Component) -> None:
        """
        Initializes the scoreboard component.

        :param name: Name of the scoreboard.
        :type name: str
        :param parent: Parent component.
        :type parent: Component
        """

        super().__init__(name, parent)
        self.before_port = List()
        self.before_item = None
        self.after_port = List()
        self.after_item = None
        self.compare_count = 0
        self.min_compare_count = 0
        self.verbose = False

    def set_verbose(self, verbose: bool) -> None:
        """
        Sets the verbosity of the scoreboard.

        :param verbose: Verbosity flag.
        """
        self.verbose = verbose

    def set_min_compare_count(self, count: int) -> None:
        """
        Sets the minimum number of comparisons required.

        :param count: Minimum number of comparisons.
        """
        self.min_compare_count = count

    async def run_phase(self) -> None:
        """
        Runs the scoreboard phase.
        """
        while True:
            self.before_item = await self.before_port.blocking_pop()
            self.after_item = await self.after_port.blocking_pop()

            self.before_item.compare(self.after_item, verbose=self.verbose, bidirectional=True)

            self.compare_count += 1

            self.after_item = None
            self.before_item = None

    async def report_phase(self) -> None:
        """
        Reports the results of the scoreboard.
        """
        if len(self.before_port) + int(self.before_item is not None) > 0 or len(
            self.after_port
        ) + int(self.after_item is not None):
            self.error(
                f"Outstanding items: before_port={len(self.before_port) + int(self.before_item is not None)} after_port={len(self.after_port) + int(self.after_item is not None)}"
            )

        if self.compare_count < self.min_compare_count:
            self.error(
                f"Not enough items compared: {self.compare_count} < {self.min_compare_count}"
            )

        if self.verbose:
            self.info(f"Compared {self.compare_count} items")


__all__ = ["Scoreboard"]
