"""
Fees and Rates - Interest rates, commissions, banking fees
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import uuid


class FeeType(Enum):
    """Types of banking fees"""
    # Account fees
    ACCOUNT_MAINTENANCE = "account_maintenance"     # Frais de tenue de compte
    CARD_ANNUAL = "card_annual"                     # Cotisation carte
    CARD_REPLACEMENT = "card_replacement"           # Remplacement carte

    # Transaction fees
    TRANSFER_DOMESTIC = "transfer_domestic"         # Virement national
    TRANSFER_SEPA = "transfer_sepa"                 # Virement SEPA
    TRANSFER_INTERNATIONAL = "transfer_international"  # Virement international
    DIRECT_DEBIT = "direct_debit"                   # Prélèvement
    CHECK_PROCESSING = "check_processing"           # Traitement chèque

    # Overdraft fees
    OVERDRAFT_INTEREST = "overdraft_interest"       # Agios
    OVERDRAFT_FEE = "overdraft_fee"                 # Commission d'intervention
    REJECTED_PAYMENT = "rejected_payment"           # Rejet de prélèvement

    # Service fees
    STATEMENT_PAPER = "statement_paper"             # Relevé papier
    CERTIFICATE = "certificate"                     # Attestation
    WIRE_TRANSFER = "wire_transfer"                 # Virement urgent

    # ATM fees
    ATM_WITHDRAWAL_OTHER = "atm_withdrawal_other"   # Retrait autre banque
    ATM_WITHDRAWAL_FOREIGN = "atm_withdrawal_foreign"  # Retrait étranger

    # FX fees
    CURRENCY_CONVERSION = "currency_conversion"     # Conversion devise


class RateType(Enum):
    """Types of interest rates"""
    SAVINGS = "savings"             # Taux épargne
    LOAN = "loan"                   # Taux crédit
    OVERDRAFT = "overdraft"         # Taux découvert
    MORTGAGE = "mortgage"           # Taux immobilier
    DEPOSIT = "deposit"             # Taux dépôt


@dataclass
class Fee:
    """
    Banking fee definition
    """
    fee_id: str = field(default_factory=lambda: f"FEE{uuid.uuid4().hex[:8].upper()}")

    # Fee details
    fee_type: FeeType = FeeType.ACCOUNT_MAINTENANCE
    name: str = ""
    description: str = ""

    # Amount
    amount: Decimal = Decimal("0.00")
    is_percentage: bool = False  # True = percentage, False = fixed amount
    min_amount: Optional[Decimal] = None  # Minimum if percentage
    max_amount: Optional[Decimal] = None  # Maximum if percentage

    # Applicability
    currency: str = "EUR"
    account_types: List[str] = field(default_factory=list)  # Empty = all types
    customer_types: List[str] = field(default_factory=list)  # "individual", "business"

    # Frequency
    frequency: str = "per_transaction"  # per_transaction, monthly, yearly

    # Tax
    vat_rate: Decimal = Decimal("20.00")  # TVA
    vat_included: bool = True

    # Status
    is_active: bool = True
    effective_from: date = field(default_factory=date.today)
    effective_until: Optional[date] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def calculate(self, base_amount: Decimal = Decimal("0.00")) -> Decimal:
        """Calculate fee amount"""
        if self.is_percentage:
            fee = base_amount * self.amount / 100
            if self.min_amount and fee < self.min_amount:
                fee = self.min_amount
            if self.max_amount and fee > self.max_amount:
                fee = self.max_amount
            return fee
        return self.amount

    def to_dict(self) -> dict:
        return {
            "fee_id": self.fee_id,
            "fee_type": self.fee_type.value,
            "name": self.name,
            "description": self.description,
            "amount": str(self.amount),
            "is_percentage": self.is_percentage,
            "min_amount": str(self.min_amount) if self.min_amount else None,
            "max_amount": str(self.max_amount) if self.max_amount else None,
            "currency": self.currency,
            "account_types": self.account_types,
            "customer_types": self.customer_types,
            "frequency": self.frequency,
            "vat_rate": str(self.vat_rate),
            "vat_included": self.vat_included,
            "is_active": self.is_active,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class InterestRate:
    """
    Interest rate definition
    """
    rate_id: str = field(default_factory=lambda: f"RATE{uuid.uuid4().hex[:8].upper()}")

    # Rate details
    rate_type: RateType = RateType.SAVINGS
    name: str = ""
    description: str = ""

    # Rate value
    rate: Decimal = Decimal("0.00")  # Annual rate (e.g., 3.00 = 3%)
    is_variable: bool = False
    base_rate: str = ""  # Reference rate (EURIBOR, etc.)
    margin: Decimal = Decimal("0.00")  # Margin over base rate

    # Tiered rates (optional)
    tiers: List[dict] = field(default_factory=list)  # [{"min": 0, "max": 10000, "rate": 2.0}, ...]

    # Applicability
    product_types: List[str] = field(default_factory=list)
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None
    min_duration_months: Optional[int] = None
    max_duration_months: Optional[int] = None

    # Status
    is_active: bool = True
    effective_from: date = field(default_factory=date.today)
    effective_until: Optional[date] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def get_rate_for_amount(self, amount: Decimal) -> Decimal:
        """Get applicable rate for an amount (considering tiers)"""
        if not self.tiers:
            return self.rate

        for tier in sorted(self.tiers, key=lambda t: t.get("min", 0)):
            tier_min = Decimal(str(tier.get("min", 0)))
            tier_max = Decimal(str(tier.get("max", float("inf"))))
            if tier_min <= amount < tier_max:
                return Decimal(str(tier.get("rate", self.rate)))

        return self.rate

    def to_dict(self) -> dict:
        return {
            "rate_id": self.rate_id,
            "rate_type": self.rate_type.value,
            "name": self.name,
            "description": self.description,
            "rate": str(self.rate),
            "is_variable": self.is_variable,
            "base_rate": self.base_rate,
            "margin": str(self.margin),
            "tiers": self.tiers,
            "product_types": self.product_types,
            "min_amount": str(self.min_amount) if self.min_amount else None,
            "max_amount": str(self.max_amount) if self.max_amount else None,
            "min_duration_months": self.min_duration_months,
            "max_duration_months": self.max_duration_months,
            "is_active": self.is_active,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": self.effective_until.isoformat() if self.effective_until else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AppliedFee:
    """
    A fee that was applied to an account/transaction
    """
    applied_fee_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fee_id: str = ""
    account_iban: str = ""
    transaction_id: Optional[str] = None

    # Amount
    amount: Decimal = Decimal("0.00")
    vat_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")

    # Details
    description: str = ""
    period: str = ""  # "2024-01" for monthly fees

    # Status
    status: str = "pending"  # pending, applied, reversed
    applied_at: Optional[datetime] = None
    reversed_at: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "applied_fee_id": self.applied_fee_id,
            "fee_id": self.fee_id,
            "account_iban": self.account_iban,
            "transaction_id": self.transaction_id,
            "amount": str(self.amount),
            "vat_amount": str(self.vat_amount),
            "total_amount": str(self.total_amount),
            "description": self.description,
            "period": self.period,
            "status": self.status,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "reversed_at": self.reversed_at.isoformat() if self.reversed_at else None,
            "created_at": self.created_at.isoformat(),
        }


# Note: Demo fees and rates are in nanopy_bank/data/demo.py
