"""
REST API Server for NanoPy Bank
"""

from aiohttp import web
from decimal import Decimal
from typing import Optional
import json

from ..core import Bank, get_bank, TransactionType, AccountType, Currency


class BankAPI:
    """
    REST API for banking operations
    """

    def __init__(self, bank: Optional[Bank] = None, host: str = "0.0.0.0", port: int = 8888):
        self.bank = bank or get_bank()
        self.host = host
        self.port = port
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Setup API routes"""
        # Health
        self.app.router.add_get("/api/health", self.api_health)
        self.app.router.add_get("/api/stats", self.api_stats)

        # Customers
        self.app.router.add_get("/api/customers", self.api_customers)
        self.app.router.add_post("/api/customers", self.api_create_customer)
        self.app.router.add_get("/api/customers/{customer_id}", self.api_get_customer)

        # Accounts
        self.app.router.add_get("/api/accounts", self.api_accounts)
        self.app.router.add_post("/api/accounts", self.api_create_account)
        self.app.router.add_get("/api/accounts/{iban}", self.api_get_account)
        self.app.router.add_get("/api/accounts/{iban}/balance", self.api_get_balance)
        self.app.router.add_get("/api/accounts/{iban}/transactions", self.api_get_transactions)

        # Transactions
        self.app.router.add_post("/api/credit", self.api_credit)
        self.app.router.add_post("/api/debit", self.api_debit)
        self.app.router.add_post("/api/transfer", self.api_transfer)
        self.app.router.add_post("/api/sepa/credit-transfer", self.api_sepa_credit_transfer)

    # ========== HEALTH ==========

    async def api_health(self, request):
        """Health check"""
        return web.json_response({"status": "ok", "service": "nanopy-bank"})

    async def api_stats(self, request):
        """Get bank statistics"""
        stats = self.bank.get_stats()
        return web.json_response(stats)

    # ========== CUSTOMERS ==========

    async def api_customers(self, request):
        """List all customers"""
        customers = [c.to_dict() for c in self.bank.customers.values()]
        return web.json_response({"customers": customers, "count": len(customers)})

    async def api_create_customer(self, request):
        """Create a new customer"""
        try:
            data = await request.json()
            customer = self.bank.create_customer(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                phone=data.get("phone", ""),
                address=data.get("address", ""),
                city=data.get("city", ""),
                postal_code=data.get("postal_code", ""),
                country=data.get("country", "FR")
            )
            return web.json_response({"ok": True, "customer": customer.to_dict()})
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def api_get_customer(self, request):
        """Get customer by ID"""
        customer_id = request.match_info["customer_id"]
        customer = self.bank.get_customer(customer_id)
        if not customer:
            return web.json_response({"error": "Customer not found"}, status=404)
        return web.json_response(customer.to_dict())

    # ========== ACCOUNTS ==========

    async def api_accounts(self, request):
        """List all accounts"""
        accounts = [a.to_dict() for a in self.bank.accounts.values()]
        return web.json_response({"accounts": accounts, "count": len(accounts)})

    async def api_create_account(self, request):
        """Create a new account"""
        try:
            data = await request.json()
            account = self.bank.create_account(
                customer_id=data["customer_id"],
                account_type=AccountType(data.get("account_type", "checking")),
                currency=Currency(data.get("currency", "EUR")),
                initial_balance=Decimal(str(data.get("initial_balance", "0.00"))),
                overdraft_limit=Decimal(str(data.get("overdraft_limit", "0.00"))),
                account_name=data.get("account_name", "")
            )
            return web.json_response({"ok": True, "account": account.to_dict()})
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def api_get_account(self, request):
        """Get account by IBAN"""
        iban = request.match_info["iban"]
        account = self.bank.get_account(iban)
        if not account:
            return web.json_response({"error": "Account not found"}, status=404)
        return web.json_response(account.to_dict())

    async def api_get_balance(self, request):
        """Get account balance"""
        iban = request.match_info["iban"]
        account = self.bank.get_account(iban)
        if not account:
            return web.json_response({"error": "Account not found"}, status=404)
        return web.json_response({
            "iban": account.iban,
            "balance": str(account.balance),
            "available_balance": str(account.available_balance),
            "currency": account.currency.value
        })

    async def api_get_transactions(self, request):
        """Get account transactions"""
        iban = request.match_info["iban"]
        limit = int(request.query.get("limit", 50))
        transactions = self.bank.get_account_transactions(iban, limit)
        return web.json_response({
            "iban": iban,
            "transactions": [tx.to_dict() for tx in transactions],
            "count": len(transactions)
        })

    # ========== TRANSACTIONS ==========

    async def api_credit(self, request):
        """Credit an account"""
        try:
            data = await request.json()
            tx = self.bank.credit(
                iban=data["iban"],
                amount=Decimal(str(data["amount"])),
                label=data["label"],
                counterparty_name=data.get("counterparty_name", ""),
                counterparty_iban=data.get("counterparty_iban", ""),
                description=data.get("description", ""),
                category=data.get("category", "")
            )
            return web.json_response({"ok": True, "transaction": tx.to_dict()})
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def api_debit(self, request):
        """Debit an account"""
        try:
            data = await request.json()
            tx = self.bank.debit(
                iban=data["iban"],
                amount=Decimal(str(data["amount"])),
                label=data["label"],
                counterparty_name=data.get("counterparty_name", ""),
                counterparty_iban=data.get("counterparty_iban", ""),
                description=data.get("description", ""),
                category=data.get("category", "")
            )
            return web.json_response({"ok": True, "transaction": tx.to_dict()})
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def api_transfer(self, request):
        """Transfer between accounts"""
        try:
            data = await request.json()
            debit_tx, credit_tx = self.bank.transfer(
                from_iban=data["from_iban"],
                to_iban=data["to_iban"],
                amount=Decimal(str(data["amount"])),
                label=data["label"],
                description=data.get("description", "")
            )
            return web.json_response({
                "ok": True,
                "debit_transaction": debit_tx.to_dict(),
                "credit_transaction": credit_tx.to_dict() if credit_tx else None
            })
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    async def api_sepa_credit_transfer(self, request):
        """Execute SEPA Credit Transfer"""
        try:
            data = await request.json()
            tx = self.bank.sepa_credit_transfer(
                from_iban=data["from_iban"],
                to_iban=data["to_iban"],
                to_bic=data.get("to_bic", ""),
                to_name=data["to_name"],
                amount=Decimal(str(data["amount"])),
                label=data["label"],
                end_to_end_id=data.get("end_to_end_id", "")
            )
            return web.json_response({"ok": True, "transaction": tx.to_dict()})
        except KeyError as e:
            return web.json_response({"error": f"Missing field: {e}"}, status=400)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)

    def run(self):
        """Run the API server"""
        print(f"Starting NanoPy Bank API on http://{self.host}:{self.port}")
        web.run_app(self.app, host=self.host, port=self.port, print=None)


def run_api(host: str = "0.0.0.0", port: int = 8888, data_dir: str = None):
    """Run the API server"""
    bank = get_bank(data_dir)
    api = BankAPI(bank, host, port)
    api.run()
