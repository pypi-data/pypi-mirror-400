from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, TypeAlias

from ape.utils import ManagerAccessMixin
from ape.types import AddressType

if TYPE_CHECKING:
    # NOTE: Not available in `typing` in 3.10

    from ape.api import ReceiptAPI, AccountAPI, BaseAddress
    from ape.contracts import ContractInstance
    from ape_tokens import Token


TokenType: TypeAlias = "Token | ContractInstance | AddressType | str"
TokenAmount: TypeAlias = Decimal | str | int
UserType: TypeAlias = "AccountAPI | BaseAddress | AddressType | str"


class Version(str, Enum):
    """All supported versions of Aave in this SDK"""

    V3 = "v3"


class BaseMarket(ABC, ManagerAccessMixin):
    """Class for working with an instance of an Aave market"""

    # NOTE: Only includes methods supported by ALL protocol versions.
    # NOTE: Implementations should provide their own constructors and contract properties.

    @property
    @abstractmethod
    def assets(self) -> list["Token"]:
        """
        Get all assets supported by this market.

        Returns:
            List of Tokens supported by Market.
        """

    def __contains__(self, token: TokenType) -> bool:
        return self.conversion_manager.convert(token, AddressType) in self.supported_assets

    @abstractmethod
    def get_position(self, account: UserType) -> "BasePosition":
        """Get position information for a specific account"""

    # Generic market information

    @abstractmethod
    def supply_yield(self, asset: TokenType) -> Decimal:
        """Check what the current annualized percentage yield is for supplying asset in market"""

    @abstractmethod
    def borrow_rate(self, asset: TokenType) -> Decimal:
        """
        Check what the current annualized percentage rate is for borrowing asset from market,
        for the given rate type.
        """

    @abstractmethod
    def total_supplied(self, asset: TokenType) -> Decimal:
        """Get the total amount supplied of the given asset to market"""

    @abstractmethod
    def total_borrowed(self, asset: TokenType) -> Decimal:
        """Get the total amount of the the given asset borrowed from market"""

    @abstractmethod
    def available_liquidity(self, asset: TokenType) -> Decimal:
        """Get the total amount of the given asset able to be borrowed from market"""

    @abstractmethod
    def utilization_rate(self, asset: TokenType) -> Decimal:
        """Get the total utilization ratio of the given asset in market (0.8 = 80%)"""

    @abstractmethod
    def max_ltv(self, asset: TokenType) -> Decimal:
        """Get the configured maximum loan-to-value ratio for given asset in market (0.8 = 80%)"""

    @abstractmethod
    def liquidation_threshold(self, asset: TokenType) -> Decimal:
        """Get the configured liquidation threshold for the given asset's utilization ratio"""

    @abstractmethod
    def liquidation_penalty(self, asset: TokenType) -> Decimal:
        """Get the configured current liquidation penalty ratio for the given asset"""

    @abstractmethod
    def reserve_factor(self, asset: TokenType) -> Decimal:
        """Get the configured reserve factor for the given asset (0.6 = 60%)"""

    @abstractmethod
    def is_allowed_collateral(self, asset: TokenType) -> bool:
        """Check if asset is currently configured to be used as collateral"""

    @abstractmethod
    def is_borrowable(self, asset: TokenType) -> bool:
        """Check if asset is configured to allow borrowing"""

    @abstractmethod
    def get_asset_price(self, asset: TokenType) -> Decimal:
        """
        Get current oracle price for an asset.

        Args:
            asset: Token address

        Returns:
            Price in base currency (usually USD with 8 decimals)
        """


class BasePosition(ABC, ManagerAccessMixin):
    """Class for managing a specific account's position"""

    def __init__(self, market: BaseMarket, account: AddressType):
        self.market = market
        self.account = account

    @property
    @abstractmethod
    def health_factor(self) -> Decimal:
        """Get current health factor of position (>=1 is healthy, <1 is able to be liquidated)"""

    @property
    @abstractmethod
    def ltv(self) -> Decimal:
        """Get current loan-to-value ratio of position (0.8 = 80%)"""

    @abstractmethod
    def supplied(self, asset: TokenType) -> Decimal:
        """Get the amount supplied to market by this account of the given asset"""

    @abstractmethod
    def deposit(
        self,
        asset: TokenType,
        amount: TokenAmount | None = None,
        **txn_args,
    ) -> "ReceiptAPI":
        """Deposit assets into the market (amount=None means "deposit all")"""

    @abstractmethod
    def withdraw(
        self,
        asset: TokenType,
        amount: TokenAmount | None = None,
        receiver: "UserType | None" = None,
        **txn_args,
    ) -> "ReceiptAPI":
        """Withdraw deposited assets (amount=None means "withdraw all")"""

    @abstractmethod
    def borrowed(self, asset: TokenType) -> Decimal:
        """Get the amount borrowed from market by this account of the given asset"""

    @abstractmethod
    def available(self, asset: TokenType) -> Decimal:
        """Get the amount able to be borrowed from market of the given asset"""

    @abstractmethod
    def borrow(
        self,
        asset: TokenType,
        amount: TokenAmount,
        # NOTE: Can put additional kwargs here e.g. `interest_rate_mode`
        **txn_args,
    ) -> "ReceiptAPI":
        """Borrow assets from the market"""

    @abstractmethod
    def repay(
        self,
        asset: TokenType,
        amount: TokenAmount | None = None,
        # NOTE: Can put additional kwargs here e.g. `interest_rate_mode`
        **txn_args,
    ) -> "ReceiptAPI":
        """Repay amount of borrowed assets (amount=None means "repay all")"""

    @abstractmethod
    def liquidation_price(self, collateral_asset: TokenType, debt_asset: TokenType) -> Decimal:
        """Calculate liquidation price for a collateral/debt pair"""

    @abstractmethod
    def liquidate(self, **txn_args) -> "ReceiptAPI":
        """Perform a liquidation of the account"""
