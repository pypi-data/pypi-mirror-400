"""
Bank - Core banking logic
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from pathlib import Path

from .models import (
    Account, Transaction, Customer, Card,
    TransactionType, AccountType, AccountStatus, Currency
)


class Bank:
    """
    Core banking system - manages accounts, transactions, customers
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".nanopy-bank"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage (loaded from JSON files)
        self.customers: Dict[str, Customer] = {}
        self.accounts: Dict[str, Account] = {}  # Key = IBAN
        self.transactions: Dict[str, Transaction] = {}
        self.cards: Dict[str, Card] = {}

        # Load existing data
        self._load_data()

    # ========== DATA PERSISTENCE ==========

    def _load_data(self):
        """Load data from JSON files"""
        # Load customers
        customers_file = self.data_dir / "customers.json"
        if customers_file.exists():
            with open(customers_file, "r") as f:
                data = json.load(f)
                for cust_data in data:
                    # Remove computed properties that shouldn't be passed to constructor
                    cust_data.pop("full_name", None)
                    if cust_data.get("created_at"):
                        cust_data["created_at"] = datetime.fromisoformat(cust_data["created_at"])
                    if cust_data.get("birth_date"):
                        cust_data["birth_date"] = datetime.fromisoformat(cust_data["birth_date"])
                    cust = Customer(**cust_data)
                    self.customers[cust.customer_id] = cust

        # Load accounts
        accounts_file = self.data_dir / "accounts.json"
        if accounts_file.exists():
            with open(accounts_file, "r") as f:
                data = json.load(f)
                for acc_data in data:
                    # Remove computed properties
                    acc_data.pop("iban_formatted", None)
                    acc_data["account_type"] = AccountType(acc_data["account_type"])
                    acc_data["currency"] = Currency(acc_data["currency"])
                    acc_data["status"] = AccountStatus(acc_data["status"])
                    acc_data["balance"] = Decimal(acc_data["balance"])
                    acc_data["available_balance"] = Decimal(acc_data["available_balance"])
                    acc_data["overdraft_limit"] = Decimal(acc_data["overdraft_limit"])
                    if acc_data.get("created_at"):
                        acc_data["created_at"] = datetime.fromisoformat(acc_data["created_at"])
                    if acc_data.get("last_transaction"):
                        acc_data["last_transaction"] = datetime.fromisoformat(acc_data["last_transaction"])
                    acc = Account(**acc_data)
                    self.accounts[acc.iban] = acc

        # Load transactions
        transactions_file = self.data_dir / "transactions.json"
        if transactions_file.exists():
            with open(transactions_file, "r") as f:
                data = json.load(f)
                for tx_data in data:
                    # Remove computed properties
                    tx_data.pop("signed_amount", None)
                    tx_data.pop("is_credit", None)
                    tx_data.pop("is_debit", None)
                    tx_data["transaction_type"] = TransactionType(tx_data["transaction_type"])
                    tx_data["currency"] = Currency(tx_data["currency"])
                    tx_data["amount"] = Decimal(tx_data["amount"])
                    if tx_data.get("balance_after"):
                        tx_data["balance_after"] = Decimal(tx_data["balance_after"])
                    if tx_data.get("created_at"):
                        tx_data["created_at"] = datetime.fromisoformat(tx_data["created_at"])
                    if tx_data.get("executed_at"):
                        tx_data["executed_at"] = datetime.fromisoformat(tx_data["executed_at"])
                    if tx_data.get("value_date"):
                        tx_data["value_date"] = datetime.fromisoformat(tx_data["value_date"])
                    tx = Transaction(**tx_data)
                    self.transactions[tx.transaction_id] = tx

        print(f"[BANK] Loaded {len(self.customers)} customers, {len(self.accounts)} accounts, {len(self.transactions)} transactions")

    def _save_data(self):
        """Save data to JSON files"""
        # Save customers
        customers_data = [c.to_dict() for c in self.customers.values()]
        with open(self.data_dir / "customers.json", "w") as f:
            json.dump(customers_data, f, indent=2, default=str)

        # Save accounts
        accounts_data = []
        for acc in self.accounts.values():
            d = acc.to_dict()
            d["account_type"] = acc.account_type.value
            d["currency"] = acc.currency.value
            d["status"] = acc.status.value
            accounts_data.append(d)
        with open(self.data_dir / "accounts.json", "w") as f:
            json.dump(accounts_data, f, indent=2, default=str)

        # Save transactions
        transactions_data = []
        for tx in self.transactions.values():
            d = tx.to_dict()
            d["transaction_type"] = tx.transaction_type.value
            d["currency"] = tx.currency.value
            transactions_data.append(d)
        with open(self.data_dir / "transactions.json", "w") as f:
            json.dump(transactions_data, f, indent=2, default=str)

    # ========== CUSTOMERS ==========

    def create_customer(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str = "",
        address: str = "",
        city: str = "",
        postal_code: str = "",
        country: str = "FR"
    ) -> Customer:
        """Create a new customer"""
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            postal_code=postal_code,
            country=country
        )
        self.customers[customer.customer_id] = customer
        self._save_data()
        print(f"[BANK] Created customer: {customer.full_name} ({customer.customer_id})")
        return customer

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        return self.customers.get(customer_id)

    def get_customer_accounts(self, customer_id: str) -> List[Account]:
        """Get all accounts for a customer"""
        return [acc for acc in self.accounts.values() if acc.customer_id == customer_id]

    # ========== ACCOUNTS ==========

    def create_account(
        self,
        customer_id: str,
        account_type: AccountType = AccountType.CHECKING,
        currency: Currency = Currency.EUR,
        initial_balance: Decimal = Decimal("0.00"),
        overdraft_limit: Decimal = Decimal("0.00"),
        account_name: str = ""
    ) -> Account:
        """Create a new account"""
        if customer_id not in self.customers:
            raise ValueError(f"Customer {customer_id} not found")

        account = Account(
            customer_id=customer_id,
            account_type=account_type,
            currency=currency,
            balance=initial_balance,
            available_balance=initial_balance,
            overdraft_limit=overdraft_limit,
            account_name=account_name
        )
        self.accounts[account.iban] = account
        self._save_data()
        print(f"[BANK] Created account: {account.iban} for customer {customer_id}")
        return account

    def get_account(self, iban: str) -> Optional[Account]:
        """Get account by IBAN"""
        # Normalize IBAN (remove spaces)
        iban = iban.replace(" ", "").upper()
        return self.accounts.get(iban)

    def get_account_balance(self, iban: str) -> Optional[Decimal]:
        """Get account balance"""
        account = self.get_account(iban)
        return account.balance if account else None

    def get_account_transactions(self, iban: str, limit: int = 50) -> List[Transaction]:
        """Get transactions for an account"""
        iban = iban.replace(" ", "").upper()
        txs = [tx for tx in self.transactions.values() if tx.account_iban == iban]
        txs.sort(key=lambda x: x.created_at, reverse=True)
        return txs[:limit]

    # ========== TRANSACTIONS ==========

    def credit(
        self,
        iban: str,
        amount: Decimal,
        label: str,
        counterparty_name: str = "",
        counterparty_iban: str = "",
        transaction_type: TransactionType = TransactionType.CREDIT,
        description: str = "",
        category: str = ""
    ) -> Transaction:
        """Credit an account (add money)"""
        account = self.get_account(iban)
        if not account:
            raise ValueError(f"Account {iban} not found")

        if account.status != AccountStatus.ACTIVE:
            raise ValueError(f"Account {iban} is not active")

        # Update balance
        account.balance += amount
        account.available_balance += amount
        account.last_transaction = datetime.now()

        # Create transaction
        tx = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            currency=account.currency,
            account_iban=account.iban,
            to_iban=account.iban,
            from_iban=counterparty_iban or None,
            label=label,
            description=description,
            category=category,
            counterparty_name=counterparty_name,
            counterparty_iban=counterparty_iban or None,
            balance_after=account.balance
        )
        self.transactions[tx.transaction_id] = tx
        self._save_data()

        print(f"[BANK] Credit {amount} {account.currency.value} to {iban}: {label}")
        return tx

    def debit(
        self,
        iban: str,
        amount: Decimal,
        label: str,
        counterparty_name: str = "",
        counterparty_iban: str = "",
        transaction_type: TransactionType = TransactionType.DEBIT,
        description: str = "",
        category: str = ""
    ) -> Transaction:
        """Debit an account (remove money)"""
        account = self.get_account(iban)
        if not account:
            raise ValueError(f"Account {iban} not found")

        if not account.can_debit(amount):
            raise ValueError(f"Insufficient funds in account {iban}")

        # Update balance
        account.balance -= amount
        account.available_balance -= amount
        account.last_transaction = datetime.now()

        # Create transaction
        tx = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            currency=account.currency,
            account_iban=account.iban,
            from_iban=account.iban,
            to_iban=counterparty_iban or None,
            label=label,
            description=description,
            category=category,
            counterparty_name=counterparty_name,
            counterparty_iban=counterparty_iban or None,
            balance_after=account.balance
        )
        self.transactions[tx.transaction_id] = tx
        self._save_data()

        print(f"[BANK] Debit {amount} {account.currency.value} from {iban}: {label}")
        return tx

    def transfer(
        self,
        from_iban: str,
        to_iban: str,
        amount: Decimal,
        label: str,
        description: str = ""
    ) -> tuple:
        """Transfer money between accounts"""
        from_account = self.get_account(from_iban)
        to_account = self.get_account(to_iban)

        if not from_account:
            raise ValueError(f"Source account {from_iban} not found")

        # Debit source account
        debit_tx = self.debit(
            from_iban,
            amount,
            f"Virement vers {to_iban[-4:]}",
            counterparty_name=to_account.account_name if to_account else "",
            counterparty_iban=to_iban,
            transaction_type=TransactionType.TRANSFER,
            description=description
        )

        # Credit destination account (if internal)
        credit_tx = None
        if to_account:
            credit_tx = self.credit(
                to_iban,
                amount,
                f"Virement de {from_iban[-4:]}",
                counterparty_name=from_account.account_name,
                counterparty_iban=from_iban,
                transaction_type=TransactionType.TRANSFER,
                description=description
            )

        print(f"[BANK] Transfer {amount} EUR from {from_iban} to {to_iban}")
        return debit_tx, credit_tx

    # ========== SEPA ==========

    def sepa_credit_transfer(
        self,
        from_iban: str,
        to_iban: str,
        to_bic: str,
        to_name: str,
        amount: Decimal,
        label: str,
        end_to_end_id: str = ""
    ) -> Transaction:
        """Execute a SEPA Credit Transfer"""
        tx = self.debit(
            from_iban,
            amount,
            label,
            counterparty_name=to_name,
            counterparty_iban=to_iban,
            transaction_type=TransactionType.SEPA_CREDIT,
            description=f"SEPA Credit Transfer to {to_name}"
        )
        tx.counterparty_bic = to_bic
        tx.end_to_end_id = end_to_end_id or tx.reference
        self._save_data()
        return tx

    # ========== STATISTICS ==========

    def get_stats(self) -> dict:
        """Get bank statistics"""
        total_balance = sum(acc.balance for acc in self.accounts.values())
        total_transactions = len(self.transactions)

        return {
            "total_customers": len(self.customers),
            "total_accounts": len(self.accounts),
            "total_transactions": total_transactions,
            "total_balance": str(total_balance),
            "accounts_by_type": {
                at.value: len([a for a in self.accounts.values() if a.account_type == at])
                for at in AccountType
            },
            "transactions_today": len([
                tx for tx in self.transactions.values()
                if tx.created_at.date() == datetime.now().date()
            ])
        }


# Singleton instance
_bank_instance: Optional[Bank] = None


def get_bank(data_dir: Optional[str] = None) -> Bank:
    """Get or create bank instance"""
    global _bank_instance
    if _bank_instance is None:
        _bank_instance = Bank(data_dir)
    return _bank_instance
