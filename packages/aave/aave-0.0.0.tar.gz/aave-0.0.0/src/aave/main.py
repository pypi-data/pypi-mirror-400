from collections.abc import Iterator
from typing import TYPE_CHECKING

from ape.utils import ManagerAccessMixin


if TYPE_CHECKING:
    from .types import TokenType, BaseMarket


class Aave(ManagerAccessMixin):
    """
    Main class for interacting with Aave protocol across all versions and markets.

    Usage:
        from aave import Aave
        aave = Aave()  # Defaults to all supported versions
        print(*aave.get_markets("WETH"))
    """

    def __init__(
        self,
        use_v2: bool = False,
        use_v3: bool = True,
    ):
        self.all_markets: list["BaseMarket"] = []
        if not (use_v2 or use_v3):
            raise ValueError("No protocol versions selected")

        if use_v2:
            raise NotImplementedError(" is not supported yet!")

        if use_v3:
            from . import v3

            self.all_markets.extend(v3.get_all_markets(self.provider.chain_id))

    def search_markets(self, *tokens: "TokenType") -> Iterator["BaseMarket"]:
        for market in self.all_markets:
            if all(token in market for token in tokens):
                yield market
