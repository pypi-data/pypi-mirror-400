from collections.abc import Iterable
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from ape.types import AddressType
from ape.utils import cached_property
from ape.utils.misc import ZERO_ADDRESS
from ape_tokens import Token, TokenInstance

from . import types as aave_types

if TYPE_CHECKING:
    from ape.api import ReceiptAPI
    from ape.contracts import ContractInstance


class InterestRateMode(int, Enum):
    """V3-specific borrowing type (fixed/stable or floating/variable APR)"""

    STABLE = 1
    """Use a stable interest rate for borrowing. NOTE: Deprecated on v3.2.0+"""

    VARIABLE = 2
    """Use a variable interest rate for borrowing. Is the default."""


def get_all_markets(chain_id: int) -> Iterable["Market"]:
    match chain_id:
        case 1:  # Ethereum Mainnet
            # NOTE: We have multiple of these, so give them names
            return [
                Market(
                    pool="0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
                    name="Core",
                ),
                Market(
                    pool="0x4e033931ad43597d96D6bcc25c280717730B58B1",
                    name="Prime",
                ),
                Market(
                    pool="0xAe05Cd22df81871bc7cC2a04BeCfb516bFe332C8",
                    name="Horizon RWA",
                ),
                Market(
                    pool="0x0AA97c284e98396202b6A04024F5E2c65026F3c0",
                    name="Ether.FI",
                ),
            ]

        case 11155111:  # Ethereum Sepolia
            return [
                Market(pool="0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"),
            ]

        case 42161:  # Arbitrum Mainnet
            return [
                Market(pool="0x794a61358D6845594F94dc1DB02A252b5b4814aD"),
            ]

        case 8453:  # Base Mainnet
            return [
                Market(pool="0xA238Dd80C259a72e81d7e4664a9801593F98d1c5"),
            ]

        case 146:  # Sonic Mainnet
            return [
                Market(pool="0x5362dBb1e601abF3a4c14c22ffEdA64042E5eAA3"),
            ]

        case 10:  # Optimism Mainnet
            return [
                Market(pool="0x794a61358D6845594F94dc1DB02A252b5b4814aD"),
            ]

        case _:
            raise ValueError(f"No markets on {chain_id}")


class Market(aave_types.BaseMarket):
    def __init__(self, pool: AddressType, name: str | None = None):
        self.pool_address = pool
        self.name = name

    def __repr__(self) -> str:
        if self.name:
            return f"<v3.Market pool={self.pool_address} instance='{self.name}'>"

        return f"<v3.Market pool={self.pool_address}>"

    @cached_property
    def pool(self) -> "ContractInstance":
        # TODO: Add SDK contract type loading?
        return self.chain_manager.contracts.instance_at(self.pool_address)

    @cached_property
    def ADDRESSES_PROVIDER(self) -> "ContractInstance":
        # TODO: Add SDK contract type loading?
        return self.chain_manager.contracts.instance_at(self.pool.ADDRESSES_PROVIDER())

    @cached_property
    def oracle(self) -> "ContractInstance":
        # TODO: Add SDK contract type loading?
        return self.chain_manager.contracts.instance_at(self.ADDRESSES_PROVIDER.getPriceOracle())

    @cached_property
    def BASE_CURRENCY_UNIT(self) -> int:
        return 10 ** 8
        # NOTE: No idea if this changes, but is immutable 10 ** 8
        #       see: `return self.oracle.BASE_CURRENCY_UNIT()`

    @property
    def assets(self) -> list[Token]:
        """Supported Assets by the Market (for deposit or withdrawal)"""
        return [Token.at(addr) for addr in self.pool.getReservesList()]
    
    def get_reserve_data(self, asset: aave_types.TokenType):
        """Raw, unprocessed reserve data for pool"""
        return self.pool.getReserveData(asset)
    
    def a_token_for(self, asset: aave_types.TokenType) -> "Token | None":
        if (address := self.get_reserve_data(asset).aTokenAddress) is ZERO_ADDRESS:
            return None

        return Token.at(address)

    def debt_token_for(
        self,
        asset: aave_types.TokenType,
        rate_type: InterestRateMode | int = InterestRateMode.VARIABLE,
    ) -> "Token | None":

        match InterestRateMode(rate_type):
            case InterestRateMode.VARIABLE:
                if (address := self.get_reserve_data(asset).variableDebtTokenAddress) is ZERO_ADDRESS:
                    return None

            case InterestRateMode.STABLE:
                if (address := self.get_reserve_data(asset).stableDebtTokenAddress) is ZERO_ADDRESS:
                    return None

        return Token.at(address)

    def supply_yield(self, asset: aave_types.TokenType) -> Decimal:
        reserve_data = self.get_reserve_data(asset)

    def borrow_rate(
        self,
        asset: aave_types.TokenType,
        rate_type: InterestRateMode | int = InterestRateMode.VARIABLE,
    ) -> Decimal:
        """Get current borrow rate for asset, for interest rate_type (Result is ratio)"""

        reserve_data = self.get_reserve_data(asset)

        match InterestRateMode(rate_type):
            case InterestRateMode.STABLE:
                apr = reserve_data.currentStableBorrowRate
            case InterestRateMode.VARIABLE:
                apr = reserve_data.currentVariableBorrowRate

        return Decimal(apr) / 10**27

    def total_supplied(self, asset: aave_types.TokenType) -> Decimal:
        reserve_data = self.get_reserve_data(asset)

    def total_borrowed(self, asset: aave_types.TokenType) -> Decimal:
        reserve_data = self.get_reserve_data(asset)

    def available_liquidity(self, asset: aave_types.TokenType) -> Decimal:
        reserve_data = self.get_reserve_data(asset)
        
    def get_reserve_config(self, asset: aave_types.TokenType):
        return self.data_provider.getReserveConfigurationData(asset)

    def utilization_rate(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def max_ltv(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def liquidation_threshold(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def liquidation_penalty(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def reserve_factor(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def is_allowed_collateral(self, asset: aave_types.TokenType) -> bool:
        reserve_config = self.get_reserve_config(asset)

    def is_borrowable(self, asset: aave_types.TokenType) -> bool:
        """Is given asset borrowable"""

        reserve_data = self.get_reserve_data(asset)
        return (
            reserve_data.currentStableBorrowRate > 0
            or reserve_data.currentVariableBorrowRate > 0
        )

    def get_asset_price(self, asset: aave_types.TokenType) -> Decimal:
        reserve_config = self.get_reserve_config(asset)

    def get_position(self, account: aave_types.UserType) -> "Position":
        return Position(market=self, account=self.conversion_manager.convert(account, AddressType))


class Position(aave_types.BasePosition):
    @property
    def user_data(self):
        """Raw user account data from pool"""
        return self.market.pool.getUserAccountData(self.account)

    @property
    def total_collateral(self) -> Decimal:
        """Sum of position's total collateral value, using Oracle Price"""
        return Decimal(self.user_data.totalCollateralBase) / self.market.BASE_CURRENCY_UNIT

    @property
    def total_debt(self) -> Decimal:
        """Sum of position's total debt value, using Oracle Price"""
        return Decimal(self.user_data.totalDebtBase) / self.market.BASE_CURRENCY_UNIT

    @property
    def net_worth(self) -> Decimal:
        """Net value of account, using Oracle Price (negative implies liquidation required)"""
        return self.total_collateral - self.total_debt

    @property
    def max_ltv(self) -> Decimal:
        """Maximum LTV (loan-to-value) allowed for this position (ratio)"""
        return Decimal(self.user_data.ltv) / 10_000

    @property
    def total_borrowable(self) -> Decimal:
        """The total amount borrowable (`ltv == max_ltv`), using Oracle Price"""
        return Decimal(self.user_data.availableBorrowsBase) / self.market.BASE_CURRENCY_UNIT

    @property
    def health_factor(self) -> Decimal:
        """Current health factor of this position (liquidated below 1.0)"""
        # return self.liquidation_ltv / self.ltv
        return Decimal(self.user_data.healthFactor) / self.market.BASE_CURRENCY_UNIT
    
    @property
    def liquidation_ltv(self) -> Decimal:
        """LTV (loan-to-value) at which liquidation occurs for this position (ratio)"""
        return Decimal(self.user_data.currentLiquidationThreshold) / 10_000

    @property
    def ltv(self) -> Decimal:
        """Current actual LTV (loan-to-value) for this position (ratio)"""
        return self.total_debt / self.total_collateral

    def supplied(self, asset: aave_types.TokenType) -> Decimal:
        """Current amount of asset supplied for this position"""
        if not (a_token := self.market.a_token_for(asset)):
            return Decimal(0)
       
        # NOTE: aToken balance accrues as native underlying balance
        return Decimal(a_token.balanceOf(self.account)) / Decimal(10 ** a_token.decimals())

    @property
    def collateral(self) -> dict[Token, Decimal]:
        return {
            token: supplied
            for token in self.market.assets
            if (supplied := self.supplied(token)) > 0
        }

    def deposit(
        self,
        asset: aave_types.TokenType,
        amount: aave_types.TokenAmount | None = None,
        **txn_args,
    ) -> "ReceiptAPI":
        """Perform a deposit of a given amount of the specific asset, optionally on behalf of another account"""
        if not isinstance(asset, TokenInstance):
            asset = Token.at(self.conversion_manager.convert(asset, AddressType))

        sender = txn_args.get("sender") or self.account_manager.default_sender
        if amount is None:
            amount = asset.balanceOf(sender)

        elif isinstance(amount, Decimal):
            amount = int(amount * 10 ** asset.decimals())

        elif not isinstance(amount, int):
            amount = self.conversion_manager.convert(amount, int)

        # Check and handle approvals
        if asset.allowance(sender, self.market.pool) < amount:
            asset.approve(self.market.pool, amount, sender=sender)

        # Perform deposit
        return self.market.pool.supply(
            asset,
            amount,
            self.account,  # onBehalfOf is the Position's account
            0,  # referralCode # TODO: Should we figure this out?
            **txn_args,
        )

    def withdraw(
        self,
        asset: aave_types.TokenType,
        amount: aave_types.TokenAmount | None = None,
        receiver: "aave_types.UserType | None" = None,
        **txn_args,
    ) -> "ReceiptAPI":
        # Check and handle approvals
        if not isinstance(asset, TokenInstance):
            asset = Token.at(self.conversion_manager.convert(asset, AddressType))

        sender = txn_args.get("sender") or self.account_manager.default_sender
        if amount is None:
            amount = asset.balanceOf(sender)

        elif isinstance(amount, Decimal):
            amount = int(amount * 10 ** asset.decimals())

        return self.market.pool.withdraw(
            asset,
            amount,
            receiver or self.account,
            **txn_args,
        )

    def borrowed(
        self,
        asset: aave_types.TokenType,
        rate_type: InterestRateMode | int = InterestRateMode.VARIABLE,
    ) -> Decimal:
        if not (debt_token := self.market.debt_token_for(asset, rate_type=rate_type)):
            return Decimal(0)
       
        # NOTE: Debt token accrues as native underlying balance
        return Decimal(debt_token.balanceOf(self.account)) / Decimal(10 ** debt_token.decimals())

    @property
    def debt(self) -> dict[Token, Decimal]:
        return {
            token: borrowed
            for token in self.market.assets
            if (borrowed := self.borrowed(token)) > 0
        }

    def available(self, asset: aave_types.TokenType) -> Decimal:
        return min(
            self.market.get_reserve_data(asset),
        )

    def borrow(
        self,
        asset: aave_types.TokenType,
        amount: aave_types.TokenAmount,
        rate_type: InterestRateMode | int = InterestRateMode.VARIABLE,
        on_behalf_of: "aave_types.UserType | None" = None,
        **txn_args,
    ) -> "ReceiptAPI":
        if not isinstance(asset, TokenInstance):
            asset = Token.at(self.conversion_manager.convert(asset, AddressType))

        # TODO: Check credit delegation authority for `on_behalf_of`?

        if isinstance(amount, Decimal):
            amount = int(amount * 10 ** asset.decimals())

        elif not isinstance(amount, int):
            amount = self.conversion_manager.convert(amount, int)

        # Perform deposit
        return self.market.pool.borrow(
            asset,
            amount,
            rate_type,
            0,  # referralCode # TODO: Should we figure this out?
            on_behalf_of or self.account,  # onBehalfOf could be a credit delegate
            **txn_args,
        )

    def repay(
        self,
        asset: aave_types.TokenType,
        amount: aave_types.TokenAmount | None = None,
        rate_type: InterestRateMode | int = InterestRateMode.VARIABLE,
        **txn_args,
    ) -> "ReceiptAPI":
        # Check and handle approvals
        if not isinstance(asset, TokenInstance):
            asset = Token.at(self.conversion_manager.convert(asset, AddressType))

        sender = txn_args.get("sender") or self.account_manager.default_sender
        if amount is None:
            amount = asset.balanceOf(sender)

        elif isinstance(amount, Decimal):
            amount = int(amount * 10 ** asset.decimals())

        elif not isinstance(amount, int):
            amount = self.conversion_manager.convert(amount, int)
        
        # Check and handle approvals
        sender = txn_args.get("sender") or self.account_manager.default_sender
        if asset.allowance(sender, self.market.pool) < amount:
            asset.approve(self.market.pool, amount, sender=sender)

        return self.market.pool.repay(
            asset,
            amount,
            rate_type,
            self.account,  # onBehalfOf is the Position's account
            **txn_args,
        )
    
    def liquidation_price(self, collateral_asset: aave_types.TokenType, debt_asset: aave_types.TokenType) -> Decimal:
        raise NotImplementedError

    def liquidate(
        self,
        collateral_asset: aave_types.TokenType,
        debt_asset: aave_types.TokenType,
        debt_amount: aave_types.TokenAmount | None = None,
        receive_underlying: bool = True,
        **txn_args,
    ) -> "ReceiptAPI":
        # NOTE: LTV is debt / collateral, and 
        sender = txn_args.get("sender") or self.account_manager.default_sender
        if debt_amount is None:
            debt_amount = min(
                debt_asset.balanceOf(sender),
                int(self.borrowed(debt_asset) * 10 ** debt_asset.decimals()),
            )

        elif isinstance(debt_amount, Decimal):
            debt_amount = int(debt_amount * 10 ** debt_asset.decimals())

        elif not isinstance(debt_amount, int):
            debt_amount = self.conversion_manager.convert(debt_amount, int)
        
        # Check and handle approvals
        sender = txn_args.get("sender") or self.account_manager.default_sender
        if debt_asset.allowance(sender, self.market.pool) < debt_amount:
            debt_asset.approve(self.market.pool, debt_amount, sender=sender)

        self.market.pool.liquidationCall(
            collateral_asset,
            debt_asset,
            self.account,
            debt_amount,
            not receive_underlying,
            **txn_args,
        )
