import csv
import json
import pathlib
import sys
import tkinter as tk
from collections.abc import Iterable
from dataclasses import dataclass
from tkinter import filedialog

from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog, yes_no_dialog
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from common.enums import CurrencyEnum, WalletActionEnum
from common.types import Transaction
from wallet import Wallet

console = Console()


@dataclass
class TxRow:
	action: WalletActionEnum
	currency: CurrencyEnum
	amount: float

	def to_transaction(self) -> Transaction:
		return Transaction(self.action, self.currency, float(self.amount))


def pick_main_flow() -> str:
	result = radiolist_dialog(
		title="Wallet CLI",
		text="How would you like to provide transactions?",
		values=[
			("file", "Load from file (CSV/JSON)"),
			("manual", "Manually input transactions"),
		],
		ok_text="Continue",
		cancel_text="Exit",
	).run()

	if result is None:
		sys.exit(0)

	return result


def pick_action() -> WalletActionEnum:
	values = [(a, a.value.title()) for a in WalletActionEnum]

	choice = radiolist_dialog(
		title="Choose Action",
		text="Select a wallet action:",
		values=values,
	).run()

	if choice is None:
		raise KeyboardInterrupt

	return choice


def pick_currency() -> CurrencyEnum:
	values = [(c, c.value) for c in CurrencyEnum]

	choice = radiolist_dialog(
		title="Choose Currency",
		text="Select a currency:",
		values=values,
	).run()

	if choice is None:
		raise KeyboardInterrupt

	return choice


def prompt_amount() -> float:
	while True:
		value = input_dialog(
			title="Amount",
			text="Enter a positive amount:",
		).run()

		if value is None:
			raise KeyboardInterrupt

		try:
			amt = float(value)

			if amt <= 0:
				raise ValueError

			return amt

		except ValueError:
			console.print("[red]Invalid amount. Please enter a positive number.[/red]")


def confirm_add_another() -> bool:
	res = yes_no_dialog(
		title="Add Another?",
		text="Add another transaction?",
		yes_text="Yes",
		no_text="No",
	).run()

	return bool(res)


def file_open_dialog() -> str | None:
	root = tk.Tk()
	root.withdraw()
	root.update()

	path = filedialog.askopenfilename(
		title="Select a transactions file",
		filetypes=[("CSV", "*.csv"), ("JSON", "*.json"), ("All Files", "*.*")],
	)

	root.destroy()

	return path or None


def parse_csv(path: str) -> list[TxRow]:
	txs: list[TxRow] = []

	with pathlib.Path(path).open("r", newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		required = {"action", "currency", "amount"}

		if not required.issubset({h.lower() for h in reader.fieldnames or []}):
			raise ValueError("CSV must include headers: action,currency,amount")

		for i, row in enumerate(reader, start=2):
			try:
				action = WalletActionEnum[row["action"].strip().upper()]
				currency = CurrencyEnum[row["currency"].strip().upper()]
				amount = float(row["amount"])

				if amount <= 0:
					raise ValueError("Amount must be positive.")

				txs.append(TxRow(action, currency, amount))

			except Exception as e:
				raise ValueError(f"Invalid row {i}: {e}") from e

	return txs


def parse_json(path: str) -> list[TxRow]:
	with pathlib.Path(path).open("r", encoding="utf-8") as f:
		data = json.load(f)

	if not isinstance(data, list):
		raise TypeError("JSON must be a list of transactions.")

	txs: list[TxRow] = []

	for i, item in enumerate(data, start=1):
		try:
			action = WalletActionEnum[str(item["action"]).strip().upper()]
			currency = CurrencyEnum[str(item["currency"]).strip().upper()]
			amount = float(item["amount"])

			if amount <= 0:
				raise ValueError("Amount must be positive.")

			txs.append(TxRow(action, currency, amount))

		except Exception as e:
			raise ValueError(f"Invalid item at index {i}: {e}") from e

	return txs


def load_from_file_flow() -> list[TxRow]:
	path = file_open_dialog()

	if not path:
		console.print("[yellow]No file selected. Exiting.[/yellow]")
		sys.exit(0)

	path = pathlib.Path(path)
	ext = path.suffix

	try:
		if ext == ".csv":
			return parse_csv(path)

		if ext == ".json":
			return parse_json(path)

		with pathlib.Path(path).open("r", encoding="utf-8") as f:
			head = f.read(1)
			f.seek(0)

			if head == "[":
				return parse_json(path)

			return parse_csv(path)

	except Exception as e:
		console.print(f"[red]Failed to parse '{path}': {e}[/red]")
		sys.exit(1)


def manual_input_flow() -> list[TxRow]:
	txs: list[TxRow] = []

	while True:
		action = pick_action()
		currency = pick_currency()
		amount = prompt_amount()

		txs.append(TxRow(action, currency, amount))

		if not confirm_add_another():
			break

	return txs


def render_summary(transactions: Iterable[TxRow], wallet: Wallet) -> None:
	t = Table(title="Transactions", box=box.SIMPLE_HEAVY)

	t.add_column("#", justify="right", style="cyan", no_wrap=True)
	t.add_column("Action", style="magenta")
	t.add_column("Currency", style="green")
	t.add_column("Amount", justify="right")

	for i, tx in enumerate(transactions, start=1):
		t.add_row(str(i), tx.action.value, tx.currency.value, f"{tx.amount:g}")

	b = Table(title="Wallet Balances", box=box.SIMPLE_HEAVY)

	b.add_column("Currency", style="green")
	b.add_column("Balance", justify="right", style="bold")

	for ccy, amt in wallet.balance.items():
		name = getattr(ccy, "value", str(ccy))
		b.add_row(name, f"{amt:g}")

	console.print(Panel.fit(t, title="[bold]Review[/bold]", border_style="blue"))
	console.print(Panel.fit(b, title="[bold]Result[/bold]", border_style="green"))


def main() -> None:
	console.print("[bold blue]Welcome to Hedix Crypto Wallet CLI![/bold blue]")
	flow = pick_main_flow()

	tx_rows = load_from_file_flow() if flow == "file" else manual_input_flow()

	txs = [row.to_transaction() for row in tx_rows]

	try:
		wallet = Wallet(transaction_list=txs)

	except Exception as e:
		console.print(f"[red]Failed to create wallet: {e}[/red]")
		sys.exit(1)

	render_summary(tx_rows, wallet)


if __name__ == "__main__":
	try:
		main()

	except KeyboardInterrupt:
		console.print("\n[yellow]Interrupted by user.[/yellow]")
