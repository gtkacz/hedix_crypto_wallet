from typing import NamedTuple

from src.common.enums import CurrencyEnum, WalletActionEnum


class Transaction(NamedTuple):
	"""
	Represents a transaction in a cryptocurrency wallet.

	Attributes:
		wallet_action (WalletActionEnum): The action performed in the transaction.
		currency (CurrencyEnum): The currency involved in the transaction.
		amount (float): The amount involved in the transaction.
	"""

	wallet_action: WalletActionEnum
	currency: CurrencyEnum
	amount: float
