from typing import TypedDict

from src.common.enums import CurrencyEnum, WalletActionEnum


class Transaction(TypedDict):
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
