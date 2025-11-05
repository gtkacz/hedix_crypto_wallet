from unittest import TestCase

from src.common.enums import CurrencyEnum, WalletActionEnum
from src.wallet import Wallet


class TestWallet(TestCase):
	def test_simple_wallet_initialization(self):
		transactions = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.5),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.USD, 300),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 2),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 5),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 0.5),
		]

		with self.assertWarns(UserWarning, msg="Insufficient funds for withdrawal: 2 BTC, transaction skipped."):
			wallet = Wallet(transaction_list=transactions)

			self.assertEqual(wallet.balance[CurrencyEnum.BTC], 1.0)
			self.assertEqual(wallet.balance[CurrencyEnum.ETH], 5.0)
			self.assertEqual(wallet.balance[CurrencyEnum.USD], 700.0)
