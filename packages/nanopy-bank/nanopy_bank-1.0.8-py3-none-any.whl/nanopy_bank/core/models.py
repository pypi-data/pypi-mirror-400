"""
Banking Models - Account, Transaction, Customer
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import uuid
import hashlib


class TransactionType(Enum):
    """Transaction types"""
    CREDIT = "credit"  # Money in
    DEBIT = "debit"    # Money out
    TRANSFER = "transfer"
    CREDIT_TRANSFER = "credit_transfer"  # Virement
    DIRECT_DEBIT = "direct_debit"  # Prelevement
    SEPA_CREDIT = "sepa_credit"
    SEPA_DEBIT = "sepa_debit"
    CARD_PAYMENT = "card_payment"
    ATM_WITHDRAWAL = "atm_withdrawal"
    FEE = "fee"
    INTEREST = "interest"
    REFUND = "refund"


class AccountType(Enum):
    """Account types"""
    CHECKING = "checking"      # Compte courant
    SAVINGS = "savings"        # Livret d'épargne
    BUSINESS = "business"      # Compte professionnel
    JOINT = "joint"            # Compte joint


class AccountStatus(Enum):
    """Account status"""
    ACTIVE = "active"
    BLOCKED = "blocked"
    CLOSED = "closed"
    PENDING = "pending"


class Currency(Enum):
    """Supported currencies"""
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"


class CardType(Enum):
    """Card types"""
    DEBIT = "debit"
    CREDIT = "credit"
    PREPAID = "prepaid"
    BUSINESS = "business"


class CardStatus(Enum):
    """Card status"""
    ACTIVE = "active"
    BLOCKED = "blocked"
    EXPIRED = "expired"
    PENDING = "pending"


@dataclass
class Customer:
    """Bank customer"""
    customer_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "FR"
    birth_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def to_dict(self) -> dict:
        return {
            "customer_id": self.customer_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Account:
    """Bank account"""
    iban: str = ""
    bic: str = "NANPFRPP"  # Default BIC for NanoPy Bank
    account_type: AccountType = AccountType.CHECKING
    currency: Currency = Currency.EUR
    balance: Decimal = Decimal("0.00")
    available_balance: Decimal = Decimal("0.00")
    overdraft_limit: Decimal = Decimal("0.00")
    customer_id: str = ""
    account_name: str = ""
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    last_transaction: Optional[datetime] = None

    # Card info (optional)
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None

    def __post_init__(self):
        if not self.iban:
            self.iban = self._generate_iban()
        if not self.account_name:
            self.account_name = f"Compte {self.account_type.value}"

    def _generate_iban(self) -> str:
        """Generate a valid French IBAN"""
        # Bank code (5 digits) + Branch code (5 digits) + Account number (11 digits) + Key (2 digits)
        bank_code = "30001"  # NanoPy Bank code
        branch_code = "00001"
        account_num = str(uuid.uuid4().int)[:11].zfill(11)

        # Calculate check digits (simplified)
        bban = f"{bank_code}{branch_code}{account_num}00"
        # Convert letters to numbers (A=10, B=11, etc.)
        numeric = ""
        for char in f"{bban}FR00":
            if char.isalpha():
                numeric += str(ord(char.upper()) - 55)
            else:
                numeric += char

        check = 98 - (int(numeric) % 97)
        return f"FR{check:02d}{bank_code}{branch_code}{account_num}00"

    def can_debit(self, amount: Decimal) -> bool:
        """Check if account can be debited"""
        return self.status == AccountStatus.ACTIVE and \
               (self.available_balance + self.overdraft_limit) >= amount

    def to_dict(self) -> dict:
        return {
            "iban": self.iban,
            "iban_formatted": self.format_iban(),
            "bic": self.bic,
            "account_type": self.account_type.value,
            "currency": self.currency.value,
            "balance": str(self.balance),
            "available_balance": str(self.available_balance),
            "overdraft_limit": str(self.overdraft_limit),
            "customer_id": self.customer_id,
            "account_name": self.account_name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_transaction": self.last_transaction.isoformat() if self.last_transaction else None,
        }

    def format_iban(self) -> str:
        """Format IBAN with spaces every 4 characters"""
        return " ".join([self.iban[i:i+4] for i in range(0, len(self.iban), 4)])


@dataclass
class Transaction:
    """Bank transaction"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    reference: str = field(default_factory=lambda: f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}")
    transaction_type: TransactionType = TransactionType.CREDIT
    amount: Decimal = Decimal("0.00")
    currency: Currency = Currency.EUR

    # Accounts
    from_iban: Optional[str] = None
    to_iban: Optional[str] = None
    account_iban: str = ""  # The account this transaction belongs to

    # Details
    label: str = ""
    description: str = ""
    category: str = ""

    # Counterparty
    counterparty_name: str = ""
    counterparty_iban: Optional[str] = None
    counterparty_bic: Optional[str] = None

    # Metadata
    status: str = "completed"  # pending, completed, failed, cancelled
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    value_date: Optional[datetime] = None

    # SEPA specific
    end_to_end_id: Optional[str] = None
    mandate_id: Optional[str] = None

    # Balance after transaction
    balance_after: Optional[Decimal] = None

    def __post_init__(self):
        if not self.end_to_end_id:
            self.end_to_end_id = self.reference
        if not self.executed_at:
            self.executed_at = self.created_at
        if not self.value_date:
            self.value_date = self.created_at

    @property
    def is_credit(self) -> bool:
        return self.transaction_type in [
            TransactionType.CREDIT,
            TransactionType.SEPA_CREDIT,
            TransactionType.REFUND,
            TransactionType.INTEREST,
        ]

    @property
    def is_debit(self) -> bool:
        return not self.is_credit

    @property
    def signed_amount(self) -> Decimal:
        """Return amount with sign (positive for credit, negative for debit)"""
        return self.amount if self.is_credit else -self.amount

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "reference": self.reference,
            "transaction_type": self.transaction_type.value,
            "amount": str(self.amount),
            "signed_amount": str(self.signed_amount),
            "currency": self.currency.value,
            "from_iban": self.from_iban,
            "to_iban": self.to_iban,
            "account_iban": self.account_iban,
            "label": self.label,
            "description": self.description,
            "category": self.category,
            "counterparty_name": self.counterparty_name,
            "counterparty_iban": self.counterparty_iban,
            "counterparty_bic": self.counterparty_bic,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "value_date": self.value_date.isoformat() if self.value_date else None,
            "end_to_end_id": self.end_to_end_id,
            "mandate_id": self.mandate_id,
            "balance_after": str(self.balance_after) if self.balance_after else None,
            "is_credit": self.is_credit,
            "is_debit": self.is_debit,
        }


@dataclass
class Card:
    """Bank card"""
    card_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    card_number: str = ""  # Last 4 digits only for display
    card_type: str = "visa"  # visa, mastercard
    expiry_month: int = 12
    expiry_year: int = 2027
    status: str = "active"  # active, blocked, expired
    account_iban: str = ""
    daily_limit: Decimal = Decimal("1000.00")
    monthly_limit: Decimal = Decimal("5000.00")
    contactless_enabled: bool = True
    online_payments_enabled: bool = True

    def __post_init__(self):
        if not self.card_number:
            # Generate last 4 digits
            self.card_number = f"**** **** **** {uuid.uuid4().int % 10000:04d}"

    @property
    def expiry(self) -> str:
        return f"{self.expiry_month:02d}/{self.expiry_year % 100:02d}"

    def to_dict(self) -> dict:
        return {
            "card_id": self.card_id,
            "card_number": self.card_number,
            "card_type": self.card_type,
            "expiry": self.expiry,
            "status": self.status,
            "account_iban": self.account_iban,
            "daily_limit": str(self.daily_limit),
            "monthly_limit": str(self.monthly_limit),
            "contactless_enabled": self.contactless_enabled,
            "online_payments_enabled": self.online_payments_enabled,
        }
