from unittest import TestCase
from unittest.mock import patch

from src.common.enums import CurrencyEnum, WalletActionEnum
from src.wallet import Wallet


class TestWallet(TestCase):
	WARN_MSG = "Insufficient funds for withdrawal: {} {}, transaction skipped."

	# Initialization Tests
	def test_simple_wallet_initialization(self):
		"""Test basic wallet initialization with mixed transactions."""
		transactions = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.5),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.USD, 300),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 2),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 5),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 0.5),
		]

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(2, "BTC")):
			wallet = Wallet(transaction_list=transactions)

			self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)
			self.assertEqual(wallet.balance[CurrencyEnum.ETH], 5.0)
			self.assertEqual(wallet.balance[CurrencyEnum.USD], 700.0)

	def test_empty_wallet_initialization(self):
		"""Test wallet initialization with no transactions."""
		wallet = Wallet(transaction_list=[])
		self.assertEqual(wallet.balance, {})

	def test_single_deposit_initialization(self):
		"""Test wallet initialization with a single deposit."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0)]
		wallet = Wallet(transaction_list=transactions)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)

	def test_multiple_deposits_same_currency(self):
		"""Test multiple deposits to the same currency."""
		transactions = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 2.5),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 0.5),
		]
		wallet = Wallet(transaction_list=transactions)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 4.0)

	# Deposit Tests
	def test_deposit_returns_true(self):
		"""Test that deposit transactions return True."""
		wallet = Wallet(transaction_list=[])
		result = wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0)
		self.assertTrue(result)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)

	def test_deposit_multiple_currencies(self):
		"""Test deposits to different currencies."""
		wallet = Wallet(transaction_list=[])
		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.5)
		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 10.0)
		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000.0)

		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.5)
		self.assertEqual(wallet.balance[CurrencyEnum.ETH], 10.0)
		self.assertEqual(wallet.balance[CurrencyEnum.USD], 1000.0)

	def test_deposit_decimal_amounts(self):
		"""Test deposits with decimal amounts."""
		wallet = Wallet(transaction_list=[])
		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 0.123456)
		self.assertAlmostEqual(wallet.balance[CurrencyEnum.BTC], 0.123456, places=6)

	# Withdraw Tests
	def test_withdraw_with_sufficient_funds_returns_true(self):
		"""Test that successful withdrawal returns True."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 10.0)]
		wallet = Wallet(transaction_list=transactions)
		result = wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0)
		self.assertTrue(result)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 5.0)

	def test_withdraw_exact_balance(self):
		"""Test withdrawing the exact balance."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 5.0)]
		wallet = Wallet(transaction_list=transactions)
		result = wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0)
		self.assertTrue(result)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 0.0)

	def test_withdraw_insufficient_funds_returns_false(self):
		"""Test that failed withdrawal returns False."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0)]
		wallet = Wallet(transaction_list=transactions)

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(5, "BTC")):
			result = wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0)

		self.assertFalse(result)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)

	def test_withdraw_from_empty_currency(self):
		"""Test withdrawing from a currency with no balance."""
		wallet = Wallet(transaction_list=[])

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(1, "BTC")):
			result = wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 1.0)

		self.assertFalse(result)

	def test_withdraw_with_verbose_false(self):
		"""Test that verbose=False suppresses warnings."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0)]
		wallet = Wallet(transaction_list=transactions)

		with patch("warnings.warn") as mock_warn:
			result = wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0, verbose=False)
			mock_warn.assert_not_called()

		self.assertFalse(result)
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)

	def test_sequential_deposits_and_withdrawals(self):
		"""Test sequential deposits and withdrawals."""
		wallet = Wallet(transaction_list=[])

		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000.0)
		wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.USD, 200.0)
		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 500.0)
		wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.USD, 300.0)

		self.assertEqual(wallet.balance[CurrencyEnum.USD], 1000.0)

	# Validation Tests
	def test_invalid_currency_raises_error(self):
		"""Test that invalid currency raises ValueError."""
		wallet = Wallet(transaction_list=[])

		with self.assertRaises(ValueError) as context:
			wallet.process_transaction(WalletActionEnum.DEPOSIT, "INVALID", 1.0)

		self.assertIn("Unsupported currency", str(context.exception))

	def test_invalid_wallet_action_raises_error(self):
		"""Test that invalid wallet action raises ValueError."""
		wallet = Wallet(transaction_list=[])

		with self.assertRaises(ValueError) as context:
			wallet.process_transaction("INVALID_ACTION", CurrencyEnum.BTC, 1.0)

		self.assertIn("Unsupported wallet action", str(context.exception))

	def test_zero_amount_raises_error(self):
		"""Test that zero amount raises ValueError."""
		wallet = Wallet(transaction_list=[])

		with self.assertRaises(ValueError) as context:
			wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 0.0)

		self.assertIn("Amount must be positive", str(context.exception))

	def test_negative_amount_raises_error(self):
		"""Test that negative amount raises ValueError."""
		wallet = Wallet(transaction_list=[])

		with self.assertRaises(ValueError) as context:
			wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, -1.0)

		self.assertIn("Amount must be positive", str(context.exception))

	def test_validation_during_initialization(self):
		"""Test that validation happens during initialization."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, -1.0)]

		with self.assertRaises(ValueError) as context:
			Wallet(transaction_list=transactions)

		self.assertIn("Amount must be positive", str(context.exception))

	# Balance Property Tests
	def test_balance_returns_copy(self):
		"""Test that balance property returns a copy, not reference to internal state."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 10.0)]
		wallet = Wallet(transaction_list=transactions)

		balance = wallet.balance
		balance[CurrencyEnum.BTC] = 999.0

		# Original wallet balance should remain unchanged
		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 10.0)

	def test_balance_single_currency(self):
		"""Test balance with a single currency."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 5.5)]
		wallet = Wallet(transaction_list=transactions)
		balance = wallet.balance

		self.assertEqual(len(balance), 1)
		self.assertEqual(balance[CurrencyEnum.ETH], 5.5)

	def test_balance_multiple_currencies(self):
		"""Test balance with multiple currencies."""
		transactions = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 10.0),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000.0),
		]
		wallet = Wallet(transaction_list=transactions)
		balance = wallet.balance

		self.assertEqual(len(balance), 3)
		self.assertEqual(balance[CurrencyEnum.BTC], 1.0)
		self.assertEqual(balance[CurrencyEnum.ETH], 10.0)
		self.assertEqual(balance[CurrencyEnum.USD], 1000.0)

	# Edge Cases
	def test_very_large_amounts(self):
		"""Test handling of very large amounts."""
		wallet = Wallet(transaction_list=[])
		large_amount = 1_000_000_000.0

		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, large_amount)
		self.assertEqual(wallet.balance[CurrencyEnum.USD], large_amount)

	def test_multiple_failed_withdrawals(self):
		"""Test multiple failed withdrawals don't affect balance."""
		transactions = [(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.0)]
		wallet = Wallet(transaction_list=transactions)

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(10, "BTC")):
			wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 10.0)

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(5, "BTC")):
			wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0)

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(2, "BTC")):
			wallet.process_transaction(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 2.0)

		self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)

	def test_very_small_decimal_amounts(self):
		"""Test handling of very small decimal amounts."""
		wallet = Wallet(transaction_list=[])
		small_amount = 0.00000001

		wallet.process_transaction(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, small_amount)
		self.assertAlmostEqual(wallet.balance[CurrencyEnum.BTC], small_amount, places=8)

	def test_transaction_order_matters(self):
		"""Test that transaction order affects final balance."""
		transactions_1 = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 10.0),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0),
		]
		wallet_1 = Wallet(transaction_list=transactions_1)

		transactions_2 = [
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 5.0),  # Will fail
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 10.0),
		]

		with self.assertWarns(UserWarning, msg=self.WARN_MSG.format(5, "BTC")):
			wallet_2 = Wallet(transaction_list=transactions_2)

		# First wallet should have 5.0, second should have 10.0
		self.assertEqual(wallet_1.balance[CurrencyEnum.BTC], 5.0)
		self.assertEqual(wallet_2.balance[CurrencyEnum.BTC], 10.0)
