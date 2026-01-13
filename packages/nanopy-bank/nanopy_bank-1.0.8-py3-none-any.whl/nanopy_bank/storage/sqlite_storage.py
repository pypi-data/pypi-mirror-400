"""
SQLite Storage - Database persistence for banking data
"""

import sqlite3
import json
from pathlib import Path
from typing import Any, Optional, Dict, List
from datetime import datetime
from decimal import Decimal
from contextlib import contextmanager


class SQLiteStorage:
    """
    SQLite database storage for banking data
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path.home() / ".nanopy-bank"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.data_dir / "bank.db"
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    city TEXT,
                    postal_code TEXT,
                    country TEXT DEFAULT 'FR',
                    birth_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    data JSON
                )
            """)

            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    iban TEXT PRIMARY KEY,
                    bic TEXT DEFAULT 'NANPFRPP',
                    account_type TEXT DEFAULT 'checking',
                    currency TEXT DEFAULT 'EUR',
                    balance TEXT DEFAULT '0.00',
                    available_balance TEXT DEFAULT '0.00',
                    overdraft_limit TEXT DEFAULT '0.00',
                    customer_id TEXT,
                    account_name TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_transaction TEXT,
                    data JSON,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id TEXT PRIMARY KEY,
                    reference TEXT,
                    transaction_type TEXT,
                    amount TEXT,
                    currency TEXT DEFAULT 'EUR',
                    from_iban TEXT,
                    to_iban TEXT,
                    account_iban TEXT,
                    label TEXT,
                    description TEXT,
                    category TEXT,
                    counterparty_name TEXT,
                    counterparty_iban TEXT,
                    counterparty_bic TEXT,
                    status TEXT DEFAULT 'completed',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    executed_at TEXT,
                    value_date TEXT,
                    end_to_end_id TEXT,
                    mandate_id TEXT,
                    balance_after TEXT,
                    data JSON,
                    FOREIGN KEY (account_iban) REFERENCES accounts(iban)
                )
            """)

            # Cards table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    card_id TEXT PRIMARY KEY,
                    card_number TEXT,
                    card_type TEXT DEFAULT 'visa',
                    expiry_month INTEGER,
                    expiry_year INTEGER,
                    status TEXT DEFAULT 'active',
                    account_iban TEXT,
                    daily_limit TEXT DEFAULT '1000.00',
                    monthly_limit TEXT DEFAULT '5000.00',
                    contactless_enabled INTEGER DEFAULT 1,
                    online_payments_enabled INTEGER DEFAULT 1,
                    data JSON,
                    FOREIGN KEY (account_iban) REFERENCES accounts(iban)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_iban)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_customer ON accounts(customer_id)")

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # ========== CUSTOMERS ==========

    def save_customer(self, customer: Dict):
        """Save or update customer"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO customers
                (customer_id, first_name, last_name, email, phone, address, city, postal_code, country, birth_date, created_at, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.get("customer_id"),
                customer.get("first_name"),
                customer.get("last_name"),
                customer.get("email"),
                customer.get("phone"),
                customer.get("address"),
                customer.get("city"),
                customer.get("postal_code"),
                customer.get("country", "FR"),
                customer.get("birth_date"),
                customer.get("created_at", datetime.now().isoformat()),
                json.dumps(customer)
            ))
            conn.commit()

    def get_customer(self, customer_id: str) -> Optional[Dict]:
        """Get customer by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM customers WHERE customer_id = ?", (customer_id,))
            row = cursor.fetchone()
            return json.loads(row["data"]) if row else None

    def get_all_customers(self) -> List[Dict]:
        """Get all customers"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM customers ORDER BY created_at DESC")
            return [json.loads(row["data"]) for row in cursor.fetchall()]

    # ========== ACCOUNTS ==========

    def save_account(self, account: Dict):
        """Save or update account"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO accounts
                (iban, bic, account_type, currency, balance, available_balance, overdraft_limit,
                 customer_id, account_name, status, created_at, last_transaction, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.get("iban"),
                account.get("bic", "NANPFRPP"),
                account.get("account_type", "checking"),
                account.get("currency", "EUR"),
                str(account.get("balance", "0.00")),
                str(account.get("available_balance", "0.00")),
                str(account.get("overdraft_limit", "0.00")),
                account.get("customer_id"),
                account.get("account_name"),
                account.get("status", "active"),
                account.get("created_at", datetime.now().isoformat()),
                account.get("last_transaction"),
                json.dumps(account)
            ))
            conn.commit()

    def get_account(self, iban: str) -> Optional[Dict]:
        """Get account by IBAN"""
        iban = iban.replace(" ", "").upper()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM accounts WHERE iban = ?", (iban,))
            row = cursor.fetchone()
            return json.loads(row["data"]) if row else None

    def get_all_accounts(self) -> List[Dict]:
        """Get all accounts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM accounts ORDER BY created_at DESC")
            return [json.loads(row["data"]) for row in cursor.fetchall()]

    def get_customer_accounts(self, customer_id: str) -> List[Dict]:
        """Get accounts for a customer"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM accounts WHERE customer_id = ?", (customer_id,))
            return [json.loads(row["data"]) for row in cursor.fetchall()]

    # ========== TRANSACTIONS ==========

    def save_transaction(self, transaction: Dict):
        """Save transaction"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO transactions
                (transaction_id, reference, transaction_type, amount, currency, from_iban, to_iban,
                 account_iban, label, description, category, counterparty_name, counterparty_iban,
                 counterparty_bic, status, created_at, executed_at, value_date, end_to_end_id,
                 mandate_id, balance_after, data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction.get("transaction_id"),
                transaction.get("reference"),
                transaction.get("transaction_type"),
                str(transaction.get("amount", "0.00")),
                transaction.get("currency", "EUR"),
                transaction.get("from_iban"),
                transaction.get("to_iban"),
                transaction.get("account_iban"),
                transaction.get("label"),
                transaction.get("description"),
                transaction.get("category"),
                transaction.get("counterparty_name"),
                transaction.get("counterparty_iban"),
                transaction.get("counterparty_bic"),
                transaction.get("status", "completed"),
                transaction.get("created_at", datetime.now().isoformat()),
                transaction.get("executed_at"),
                transaction.get("value_date"),
                transaction.get("end_to_end_id"),
                transaction.get("mandate_id"),
                str(transaction.get("balance_after", "")) if transaction.get("balance_after") else None,
                json.dumps(transaction)
            ))
            conn.commit()

    def get_transaction(self, transaction_id: str) -> Optional[Dict]:
        """Get transaction by ID"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM transactions WHERE transaction_id = ?", (transaction_id,))
            row = cursor.fetchone()
            return json.loads(row["data"]) if row else None

    def get_account_transactions(self, iban: str, limit: int = 50) -> List[Dict]:
        """Get transactions for an account"""
        iban = iban.replace(" ", "").upper()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM transactions WHERE account_iban = ? ORDER BY created_at DESC LIMIT ?",
                (iban, limit)
            )
            return [json.loads(row["data"]) for row in cursor.fetchall()]

    def get_all_transactions(self, limit: int = 100) -> List[Dict]:
        """Get all transactions"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM transactions ORDER BY created_at DESC LIMIT ?", (limit,))
            return [json.loads(row["data"]) for row in cursor.fetchall()]

    # ========== STATS ==========

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM accounts")
            account_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM transactions")
            transaction_count = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(CAST(balance AS REAL)) FROM accounts")
            total_balance = cursor.fetchone()[0] or 0

            return {
                "customers": customer_count,
                "accounts": account_count,
                "transactions": transaction_count,
                "total_balance": f"{total_balance:.2f}",
            }


# Singleton
_sqlite_instance: Optional[SQLiteStorage] = None


def get_sqlite_storage(data_dir: Optional[str] = None) -> SQLiteStorage:
    """Get or create SQLite storage instance"""
    global _sqlite_instance
    if _sqlite_instance is None:
        _sqlite_instance = SQLiteStorage(data_dir)
    return _sqlite_instance
