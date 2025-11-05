from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass, field
from queue import SimpleQueue
from warnings import warn

from src.common.enums import CurrencyEnum, WalletActionEnum
from src.common.types import Transaction


@dataclass
class Wallet:
	"""
	A cryptocurrency wallet.

	Attributes:
		transaction_list (list[tuple[WalletActionEnum, CurrencyEnum, float]]): A list of transactions performed on the wallet.

	Raises:
		ValueError: If any transaction is invalid.
	"""

	transaction_list: Sequence[Transaction]
	state: dict[CurrencyEnum, float] = field(default_factory=lambda: defaultdict(float))

	def __post_init__(self) -> None:
		"""
		Initializes the wallet by processing the transaction list.
		"""
		transaction_queue: SimpleQueue[Transaction] = SimpleQueue()

		for transaction in self.transaction_list:
			transaction_queue.put(transaction)

		while not transaction_queue.empty():
			wallet_action, currency, amount = transaction_queue.get()
			self._validate_transaction(wallet_action, currency, amount)

			if wallet_action == WalletActionEnum.DEPOSIT:
				self.state[currency] += amount

			elif wallet_action == WalletActionEnum.WITHDRAW:
				if self.state[currency] < amount:
					warn(
						f"Insufficient funds for withdrawal: {amount} {currency}, transaction skipped.",
						stacklevel=1,
					)
					continue

				self.state[currency] -= amount

	@staticmethod
	def _validate_currency(currency: CurrencyEnum) -> None:
		"""
		Validates if the provided currency is supported.

		Args:
			currency (CurrencyEnum): The currency to validate.

		Raises:
			ValueError: If the currency is not supported.
		"""
		if currency not in CurrencyEnum:
			raise ValueError(f"Unsupported currency: {currency}")

	@staticmethod
	def _validate_wallet_action(wallet_action: WalletActionEnum) -> None:
		"""
		Validates if the provided wallet action is supported.

		Args:
			wallet_action (WalletActionEnum): The currency to validate.

		Raises:
			ValueError: If the wallet action is not supported.
		"""
		if wallet_action not in WalletActionEnum:
			raise ValueError(f"Unsupported wallet action: {wallet_action}")

	@staticmethod
	def _validate_amount(amount: float) -> None:
		"""
		Validates if the provided amount is supported.

		Args:
			amount (float): The amount to validate.

		Raises:
			ValueError: If the amount is not supported.
		"""
		if amount <= 0:
			raise ValueError(f"Amount must be positive: {amount}")

	def _validate_transaction(
		self,
		wallet_action: WalletActionEnum,
		currency: CurrencyEnum,
		amount: float,
	) -> None:
		"""
		Validates a transaction's parameters.

		Args:
			wallet_action (WalletActionEnum): The action to validate.
			currency (CurrencyEnum): The currency to validate.
			amount (float): The amount to validate.
		"""
		self._validate_wallet_action(wallet_action)
		self._validate_currency(currency)
		self._validate_amount(amount)

	@property
	def balance(self) -> dict[CurrencyEnum, float]:
		"""
		Returns the current balance of the wallet.

		Returns:
			dict[CurrencyEnum, float]: A dictionary with the balance of each currency.
		"""
		return dict(self.state)
