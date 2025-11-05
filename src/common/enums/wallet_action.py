from enum import StrEnum


class WalletActionEnum(StrEnum):
	"""Enum representing supported wallet actions."""

	DEPOSIT = "DEPOSIT"
	WITHDRAW = "WITHDRAW"
