from unittest import TestCase

from src.common.enums import CurrencyEnum, WalletActionEnum
from src.common.types import Transaction
from src.wallet import Wallet


class TestWallet(TestCase):
	def test_simple_wallet_initialization(self):
		transactions: list[Transaction] = [
			(WalletActionEnum.DEPOSIT, CurrencyEnum.BTC, 1.5),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.USD, 1000),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.USD, 300),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 2),
			(WalletActionEnum.DEPOSIT, CurrencyEnum.ETH, 5),
			(WalletActionEnum.WITHDRAW, CurrencyEnum.BTC, 0.5),
		]
		wallet = Wallet(transaction_list=transactions)
		self.assertEqual(wallet.state[CurrencyEnum.BTC], 1.0)
		self.assertEqual(wallet.state[CurrencyEnum.ETH], 5.0)
		self.assertEqual(wallet.state[CurrencyEnum.USD], 700.0)
