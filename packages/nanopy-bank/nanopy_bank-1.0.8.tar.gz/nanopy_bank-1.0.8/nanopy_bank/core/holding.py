"""
Holding and Group Management Models
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict
import uuid


class SubsidiaryType(Enum):
    """Types of subsidiaries"""
    BANK = "bank"
    ASSET_MANAGEMENT = "asset_management"
    INSURANCE = "insurance"
    LEASING = "leasing"
    FINTECH = "fintech"
    SERVICES = "services"


class SubsidiaryStatus(Enum):
    """Subsidiary status"""
    ACTIVE = "active"
    STARTUP = "startup"
    RESTRUCTURING = "restructuring"
    DIVESTING = "divesting"
    CLOSED = "closed"


class LoanDirection(Enum):
    """Direction of intra-group loan"""
    DOWNSTREAM = "downstream"  # Holding -> Filiale
    UPSTREAM = "upstream"      # Filiale -> Holding
    LATERAL = "lateral"        # Filiale -> Filiale


@dataclass
class Holding:
    """
    Holding company (maison mere)
    """
    holding_id: str = field(default_factory=lambda: f"HOLD{uuid.uuid4().hex[:6].upper()}")

    # Identity
    name: str = "Nova x Genesis"
    legal_name: str = "Nova x Genesis Financial Services SASU"
    registration_number: str = ""  # SIREN
    lei: str = ""  # Legal Entity Identifier

    # Address
    address: str = ""
    city: str = "Paris"
    postal_code: str = "75001"
    country: str = "FR"

    # Contact
    phone: str = ""
    email: str = ""
    website: str = ""

    # Accounts
    main_account_iban: str = ""
    treasury_account_iban: str = ""

    # Financials
    share_capital: Decimal = Decimal("100000000.00")
    total_assets: Decimal = Decimal("0.00")
    total_equity: Decimal = Decimal("0.00")
    consolidated_revenue: Decimal = Decimal("0.00")
    consolidated_profit: Decimal = Decimal("0.00")

    # Metadata
    founded_date: date = field(default_factory=date.today)
    fiscal_year_end: str = "12-31"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "holding_id": self.holding_id,
            "name": self.name,
            "legal_name": self.legal_name,
            "registration_number": self.registration_number,
            "lei": self.lei,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "main_account_iban": self.main_account_iban,
            "treasury_account_iban": self.treasury_account_iban,
            "share_capital": str(self.share_capital),
            "total_assets": str(self.total_assets),
            "total_equity": str(self.total_equity),
            "consolidated_revenue": str(self.consolidated_revenue),
            "consolidated_profit": str(self.consolidated_profit),
            "founded_date": self.founded_date.isoformat(),
            "fiscal_year_end": self.fiscal_year_end,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Subsidiary:
    """
    Subsidiary company (filiale)
    """
    subsidiary_id: str = field(default_factory=lambda: f"SUB{uuid.uuid4().hex[:6].upper()}")
    holding_id: str = ""

    # Identity
    name: str = ""
    legal_name: str = ""
    subsidiary_type: SubsidiaryType = SubsidiaryType.BANK
    registration_number: str = ""

    # Ownership
    ownership_percent: Decimal = Decimal("100.00")
    voting_rights_percent: Decimal = Decimal("100.00")
    acquisition_date: date = field(default_factory=date.today)
    acquisition_price: Decimal = Decimal("0.00")

    # Address
    address: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "FR"

    # Financials
    share_capital: Decimal = Decimal("0.00")
    total_assets: Decimal = Decimal("0.00")
    total_equity: Decimal = Decimal("0.00")
    revenue: Decimal = Decimal("0.00")
    net_income: Decimal = Decimal("0.00")
    employees: int = 0

    # Inter-company
    account_with_holding_iban: str = ""  # Compte courant d'associe
    dividend_policy: str = ""
    last_dividend_date: Optional[date] = None
    last_dividend_amount: Decimal = Decimal("0.00")

    # Status
    status: SubsidiaryStatus = SubsidiaryStatus.ACTIVE
    consolidation_method: str = "full"  # full, proportional, equity

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "subsidiary_id": self.subsidiary_id,
            "holding_id": self.holding_id,
            "name": self.name,
            "legal_name": self.legal_name,
            "subsidiary_type": self.subsidiary_type.value,
            "registration_number": self.registration_number,
            "ownership_percent": str(self.ownership_percent),
            "voting_rights_percent": str(self.voting_rights_percent),
            "acquisition_date": self.acquisition_date.isoformat(),
            "acquisition_price": str(self.acquisition_price),
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "share_capital": str(self.share_capital),
            "total_assets": str(self.total_assets),
            "total_equity": str(self.total_equity),
            "revenue": str(self.revenue),
            "net_income": str(self.net_income),
            "employees": self.employees,
            "account_with_holding_iban": self.account_with_holding_iban,
            "dividend_policy": self.dividend_policy,
            "last_dividend_date": self.last_dividend_date.isoformat() if self.last_dividend_date else None,
            "last_dividend_amount": str(self.last_dividend_amount),
            "status": self.status.value,
            "consolidation_method": self.consolidation_method,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class IntraGroupLoan:
    """
    Intra-group loan (pret intra-groupe)
    """
    loan_id: str = field(default_factory=lambda: f"IGL{uuid.uuid4().hex[:8].upper()}")

    # Parties
    lender_id: str = ""  # holding_id or subsidiary_id
    lender_name: str = ""
    borrower_id: str = ""
    borrower_name: str = ""
    direction: LoanDirection = LoanDirection.DOWNSTREAM

    # Loan details
    principal: Decimal = Decimal("0.00")
    interest_rate: Decimal = Decimal("0.00")  # Annual rate
    currency: str = "EUR"

    # Schedule
    start_date: date = field(default_factory=date.today)
    maturity_date: Optional[date] = None
    repayment_frequency: str = "quarterly"  # monthly, quarterly, annual, bullet

    # Current state
    outstanding_principal: Decimal = Decimal("0.00")
    accrued_interest: Decimal = Decimal("0.00")
    total_interest_paid: Decimal = Decimal("0.00")
    total_principal_paid: Decimal = Decimal("0.00")

    # Status
    status: str = "active"  # active, repaid, defaulted, restructured

    # Documentation
    contract_reference: str = ""
    purpose: str = ""
    collateral: str = ""

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.outstanding_principal == 0:
            self.outstanding_principal = self.principal

    def to_dict(self) -> dict:
        return {
            "loan_id": self.loan_id,
            "lender_id": self.lender_id,
            "lender_name": self.lender_name,
            "borrower_id": self.borrower_id,
            "borrower_name": self.borrower_name,
            "direction": self.direction.value,
            "principal": str(self.principal),
            "interest_rate": str(self.interest_rate),
            "currency": self.currency,
            "start_date": self.start_date.isoformat(),
            "maturity_date": self.maturity_date.isoformat() if self.maturity_date else None,
            "repayment_frequency": self.repayment_frequency,
            "outstanding_principal": str(self.outstanding_principal),
            "accrued_interest": str(self.accrued_interest),
            "total_interest_paid": str(self.total_interest_paid),
            "total_principal_paid": str(self.total_principal_paid),
            "status": self.status,
            "contract_reference": self.contract_reference,
            "purpose": self.purpose,
            "collateral": self.collateral,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CashPool:
    """
    Cash pooling arrangement (centralisation tresorerie)
    """
    pool_id: str = field(default_factory=lambda: f"POOL{uuid.uuid4().hex[:6].upper()}")
    holding_id: str = ""

    # Pool details
    name: str = "Cash Pool Principal"
    pool_type: str = "notional"  # notional, physical, hybrid

    # Master account (compte centralisateur)
    master_account_iban: str = ""
    master_account_balance: Decimal = Decimal("0.00")

    # Participants
    participant_accounts: List[str] = field(default_factory=list)  # List of IBANs

    # Interest rates
    credit_rate: Decimal = Decimal("0.50")  # Rate paid on positive balances
    debit_rate: Decimal = Decimal("2.00")   # Rate charged on negative balances

    # Limits
    max_debit_per_participant: Decimal = Decimal("10000000.00")

    # Current state
    total_credit_balance: Decimal = Decimal("0.00")
    total_debit_balance: Decimal = Decimal("0.00")
    net_position: Decimal = Decimal("0.00")

    # Status
    is_active: bool = True
    start_date: date = field(default_factory=date.today)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "pool_id": self.pool_id,
            "holding_id": self.holding_id,
            "name": self.name,
            "pool_type": self.pool_type,
            "master_account_iban": self.master_account_iban,
            "master_account_balance": str(self.master_account_balance),
            "participant_accounts": self.participant_accounts,
            "credit_rate": str(self.credit_rate),
            "debit_rate": str(self.debit_rate),
            "max_debit_per_participant": str(self.max_debit_per_participant),
            "total_credit_balance": str(self.total_credit_balance),
            "total_debit_balance": str(self.total_debit_balance),
            "net_position": str(self.net_position),
            "is_active": self.is_active,
            "start_date": self.start_date.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Dividend:
    """
    Dividend payment from subsidiary to holding
    """
    dividend_id: str = field(default_factory=lambda: f"DIV{uuid.uuid4().hex[:8].upper()}")

    # Parties
    subsidiary_id: str = ""
    subsidiary_name: str = ""
    holding_id: str = ""

    # Amount
    gross_amount: Decimal = Decimal("0.00")
    withholding_tax: Decimal = Decimal("0.00")
    net_amount: Decimal = Decimal("0.00")
    currency: str = "EUR"

    # Dates
    declaration_date: date = field(default_factory=date.today)
    record_date: Optional[date] = None
    payment_date: Optional[date] = None

    # Details
    fiscal_year: str = ""
    dividend_type: str = "ordinary"  # ordinary, exceptional, interim

    # Status
    status: str = "declared"  # declared, approved, paid

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "dividend_id": self.dividend_id,
            "subsidiary_id": self.subsidiary_id,
            "subsidiary_name": self.subsidiary_name,
            "holding_id": self.holding_id,
            "gross_amount": str(self.gross_amount),
            "withholding_tax": str(self.withholding_tax),
            "net_amount": str(self.net_amount),
            "currency": self.currency,
            "declaration_date": self.declaration_date.isoformat(),
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "fiscal_year": self.fiscal_year,
            "dividend_type": self.dividend_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ManagementFee:
    """
    Management fee (frais de siege) from holding to subsidiary
    """
    fee_id: str = field(default_factory=lambda: f"MGT{uuid.uuid4().hex[:8].upper()}")

    # Parties
    holding_id: str = ""
    subsidiary_id: str = ""
    subsidiary_name: str = ""

    # Amount
    amount: Decimal = Decimal("0.00")
    currency: str = "EUR"

    # Details
    service_type: str = ""  # IT, HR, Legal, Finance, Strategy
    period: str = ""  # "2025-Q1", "2025-01", etc.
    description: str = ""

    # Invoice
    invoice_number: str = ""
    invoice_date: date = field(default_factory=date.today)
    due_date: Optional[date] = None

    # Status
    status: str = "invoiced"  # invoiced, paid, cancelled

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "fee_id": self.fee_id,
            "holding_id": self.holding_id,
            "subsidiary_id": self.subsidiary_id,
            "subsidiary_name": self.subsidiary_name,
            "amount": str(self.amount),
            "currency": self.currency,
            "service_type": self.service_type,
            "period": self.period,
            "description": self.description,
            "invoice_number": self.invoice_number,
            "invoice_date": self.invoice_date.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
