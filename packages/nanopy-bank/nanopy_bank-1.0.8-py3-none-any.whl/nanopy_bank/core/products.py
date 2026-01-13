"""
Banking Products - Loans, Credits, Insurance, Savings
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import uuid


class LoanType(Enum):
    """Types of loans"""
    PERSONAL = "personal"           # Prêt personnel
    MORTGAGE = "mortgage"           # Prêt immobilier
    AUTO = "auto"                   # Crédit auto
    STUDENT = "student"             # Prêt étudiant
    BUSINESS = "business"           # Prêt professionnel
    REVOLVING = "revolving"         # Crédit renouvelable


class LoanStatus(Enum):
    """Loan status"""
    PENDING = "pending"             # En attente d'approbation
    APPROVED = "approved"           # Approuvé
    ACTIVE = "active"               # En cours
    LATE = "late"                   # En retard
    DEFAULT = "default"             # Défaut de paiement
    PAID_OFF = "paid_off"           # Remboursé
    CANCELLED = "cancelled"         # Annulé


class InsuranceType(Enum):
    """Types of insurance"""
    LIFE = "life"                   # Assurance vie
    HOME = "home"                   # Assurance habitation
    AUTO = "auto"                   # Assurance auto
    HEALTH = "health"               # Mutuelle santé
    CREDIT = "credit"               # Assurance emprunteur
    SAVINGS = "savings"             # Assurance épargne


class SavingsType(Enum):
    """Types of savings products"""
    LIVRET_A = "livret_a"           # Livret A
    LDDS = "ldds"                   # Livret Développement Durable
    LEP = "lep"                     # Livret d'Épargne Populaire
    PEL = "pel"                     # Plan Épargne Logement
    CEL = "cel"                     # Compte Épargne Logement
    TERM_DEPOSIT = "term_deposit"   # Dépôt à terme
    PEA = "pea"                     # Plan d'Épargne en Actions


@dataclass
class Loan:
    """
    Loan / Credit product
    """
    loan_id: str = field(default_factory=lambda: f"LN{uuid.uuid4().hex[:10].upper()}")
    customer_id: str = ""
    account_iban: str = ""  # Account for repayments

    # Loan details
    loan_type: LoanType = LoanType.PERSONAL
    purpose: str = ""  # Description of loan purpose

    # Amounts
    principal: Decimal = Decimal("0.00")      # Montant emprunté
    interest_rate: Decimal = Decimal("0.00")  # Taux annuel (ex: 3.5 = 3.5%)
    total_interest: Decimal = Decimal("0.00") # Total des intérêts
    total_amount: Decimal = Decimal("0.00")   # Principal + intérêts

    # Current state
    remaining_principal: Decimal = Decimal("0.00")
    remaining_interest: Decimal = Decimal("0.00")
    paid_principal: Decimal = Decimal("0.00")
    paid_interest: Decimal = Decimal("0.00")

    # Schedule
    duration_months: int = 12
    monthly_payment: Decimal = Decimal("0.00")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    next_payment_date: Optional[date] = None

    # Status
    status: LoanStatus = LoanStatus.PENDING
    payments_made: int = 0
    payments_late: int = 0
    days_overdue: int = 0

    # Insurance
    has_insurance: bool = False
    insurance_premium: Decimal = Decimal("0.00")

    # Collateral (for secured loans)
    collateral_type: str = ""
    collateral_value: Decimal = Decimal("0.00")

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    approved_at: Optional[datetime] = None
    approved_by: str = ""

    def __post_init__(self):
        if self.principal > 0 and self.remaining_principal == 0:
            self.remaining_principal = self.principal
            self._calculate_loan()

    def _calculate_loan(self):
        """Calculate loan schedule"""
        if self.principal <= 0 or self.duration_months <= 0:
            return

        # Monthly interest rate
        monthly_rate = self.interest_rate / 100 / 12

        if monthly_rate > 0:
            # Amortization formula
            self.monthly_payment = self.principal * (
                monthly_rate * (1 + monthly_rate) ** self.duration_months
            ) / ((1 + monthly_rate) ** self.duration_months - 1)
        else:
            self.monthly_payment = self.principal / self.duration_months

        self.total_amount = self.monthly_payment * self.duration_months
        self.total_interest = self.total_amount - self.principal
        self.remaining_interest = self.total_interest

    def to_dict(self) -> dict:
        return {
            "loan_id": self.loan_id,
            "customer_id": self.customer_id,
            "account_iban": self.account_iban,
            "loan_type": self.loan_type.value,
            "purpose": self.purpose,
            "principal": str(self.principal),
            "interest_rate": str(self.interest_rate),
            "total_interest": str(self.total_interest),
            "total_amount": str(self.total_amount),
            "remaining_principal": str(self.remaining_principal),
            "remaining_interest": str(self.remaining_interest),
            "paid_principal": str(self.paid_principal),
            "paid_interest": str(self.paid_interest),
            "duration_months": self.duration_months,
            "monthly_payment": str(self.monthly_payment),
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_payment_date": self.next_payment_date.isoformat() if self.next_payment_date else None,
            "status": self.status.value,
            "payments_made": self.payments_made,
            "payments_late": self.payments_late,
            "days_overdue": self.days_overdue,
            "has_insurance": self.has_insurance,
            "insurance_premium": str(self.insurance_premium),
            "collateral_type": self.collateral_type,
            "collateral_value": str(self.collateral_value),
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "progress_percent": self.progress_percent,
        }

    @property
    def progress_percent(self) -> float:
        """Percentage of loan paid off"""
        if self.total_amount <= 0:
            return 0
        paid = self.paid_principal + self.paid_interest
        return min(100, float(paid / self.total_amount * 100))


@dataclass
class Insurance:
    """
    Insurance product
    """
    insurance_id: str = field(default_factory=lambda: f"INS{uuid.uuid4().hex[:10].upper()}")
    customer_id: str = ""
    policy_number: str = field(default_factory=lambda: f"POL{uuid.uuid4().hex[:8].upper()}")

    # Insurance details
    insurance_type: InsuranceType = InsuranceType.HOME
    provider: str = "NanoPy Assurance"
    product_name: str = ""

    # Coverage
    coverage_amount: Decimal = Decimal("0.00")
    deductible: Decimal = Decimal("0.00")  # Franchise
    coverage_details: str = ""

    # Premium
    premium_amount: Decimal = Decimal("0.00")
    premium_frequency: str = "monthly"  # monthly, quarterly, yearly
    account_iban: str = ""  # For premium payments

    # Dates
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    next_payment_date: Optional[date] = None

    # Status
    status: str = "active"  # active, suspended, cancelled, expired
    is_auto_renew: bool = True

    # Claims
    claims_count: int = 0
    total_claimed: Decimal = Decimal("0.00")

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "insurance_id": self.insurance_id,
            "customer_id": self.customer_id,
            "policy_number": self.policy_number,
            "insurance_type": self.insurance_type.value,
            "provider": self.provider,
            "product_name": self.product_name,
            "coverage_amount": str(self.coverage_amount),
            "deductible": str(self.deductible),
            "coverage_details": self.coverage_details,
            "premium_amount": str(self.premium_amount),
            "premium_frequency": self.premium_frequency,
            "account_iban": self.account_iban,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_payment_date": self.next_payment_date.isoformat() if self.next_payment_date else None,
            "status": self.status,
            "is_auto_renew": self.is_auto_renew,
            "claims_count": self.claims_count,
            "total_claimed": str(self.total_claimed),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SavingsProduct:
    """
    Savings product (Livret A, PEL, etc.)
    """
    savings_id: str = field(default_factory=lambda: f"SAV{uuid.uuid4().hex[:10].upper()}")
    customer_id: str = ""
    account_iban: str = ""  # The savings account

    # Product details
    savings_type: SavingsType = SavingsType.LIVRET_A
    product_name: str = ""

    # Interest
    interest_rate: Decimal = Decimal("3.00")  # Current rate
    interest_frequency: str = "yearly"  # When interest is paid
    interest_earned: Decimal = Decimal("0.00")
    last_interest_date: Optional[date] = None

    # Limits
    min_balance: Decimal = Decimal("0.00")
    max_balance: Decimal = Decimal("22950.00")  # Livret A ceiling
    min_deposit: Decimal = Decimal("10.00")
    max_withdrawal_per_month: Optional[Decimal] = None

    # Tax
    is_tax_exempt: bool = True  # Livret A, LDDS are tax-free
    tax_rate: Decimal = Decimal("0.00")  # Flat tax rate if applicable

    # Status
    status: str = "active"
    opened_date: date = field(default_factory=date.today)
    closed_date: Optional[date] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "savings_id": self.savings_id,
            "customer_id": self.customer_id,
            "account_iban": self.account_iban,
            "savings_type": self.savings_type.value,
            "product_name": self.product_name,
            "interest_rate": str(self.interest_rate),
            "interest_frequency": self.interest_frequency,
            "interest_earned": str(self.interest_earned),
            "last_interest_date": self.last_interest_date.isoformat() if self.last_interest_date else None,
            "min_balance": str(self.min_balance),
            "max_balance": str(self.max_balance),
            "min_deposit": str(self.min_deposit),
            "max_withdrawal_per_month": str(self.max_withdrawal_per_month) if self.max_withdrawal_per_month else None,
            "is_tax_exempt": self.is_tax_exempt,
            "tax_rate": str(self.tax_rate),
            "status": self.status,
            "opened_date": self.opened_date.isoformat(),
            "closed_date": self.closed_date.isoformat() if self.closed_date else None,
            "created_at": self.created_at.isoformat(),
        }


# Note: Demo savings products are in nanopy_bank/data/demo.py
