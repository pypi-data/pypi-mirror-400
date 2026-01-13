"""
Beneficiary Models - Contacts for transfers, Standing Orders, SEPA Mandates
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List
import uuid


class MandateStatus(Enum):
    """SEPA Mandate status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MandateType(Enum):
    """SEPA Mandate type"""
    CORE = "core"      # Particuliers
    B2B = "b2b"        # Entreprises


class OrderFrequency(Enum):
    """Standing order frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class OrderStatus(Enum):
    """Standing order status"""
    ACTIVE = "active"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass
class Beneficiary:
    """
    Saved beneficiary for quick transfers
    """
    beneficiary_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    customer_id: str = ""  # Owner of this beneficiary

    # Beneficiary info
    name: str = ""
    iban: str = ""
    bic: str = ""

    # Additional info
    alias: str = ""  # Nickname (e.g., "Mom", "Landlord")
    email: str = ""
    phone: str = ""
    address: str = ""
    country: str = "FR"

    # Categorization
    category: str = ""  # "family", "business", "bills", etc.
    is_favorite: bool = False

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_used: Optional[datetime] = None
    use_count: int = 0

    def to_dict(self) -> dict:
        return {
            "beneficiary_id": self.beneficiary_id,
            "customer_id": self.customer_id,
            "name": self.name,
            "iban": self.iban,
            "iban_formatted": self.format_iban(),
            "bic": self.bic,
            "alias": self.alias,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "country": self.country,
            "category": self.category,
            "is_favorite": self.is_favorite,
            "created_at": self.created_at.isoformat(),
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "use_count": self.use_count,
        }

    def format_iban(self) -> str:
        """Format IBAN with spaces"""
        return " ".join([self.iban[i:i+4] for i in range(0, len(self.iban), 4)])


@dataclass
class StandingOrder:
    """
    Recurring transfer order (virement permanent)
    """
    order_id: str = field(default_factory=lambda: f"SO{uuid.uuid4().hex[:10].upper()}")

    # Source
    from_iban: str = ""
    customer_id: str = ""

    # Destination
    to_iban: str = ""
    to_bic: str = ""
    to_name: str = ""
    beneficiary_id: Optional[str] = None  # Link to saved beneficiary

    # Amount
    amount: Decimal = Decimal("0.00")
    currency: str = "EUR"

    # Schedule
    frequency: OrderFrequency = OrderFrequency.MONTHLY
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None  # None = no end
    next_execution: Optional[date] = None
    execution_day: int = 1  # Day of month (1-28)

    # Details
    label: str = ""
    reference: str = ""
    category: str = ""

    # Status
    status: OrderStatus = OrderStatus.ACTIVE
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    last_status: str = ""  # "success", "failed", "insufficient_funds"

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.next_execution:
            self.next_execution = self.start_date

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "from_iban": self.from_iban,
            "customer_id": self.customer_id,
            "to_iban": self.to_iban,
            "to_bic": self.to_bic,
            "to_name": self.to_name,
            "beneficiary_id": self.beneficiary_id,
            "amount": str(self.amount),
            "currency": self.currency,
            "frequency": self.frequency.value,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "execution_day": self.execution_day,
            "label": self.label,
            "reference": self.reference,
            "category": self.category,
            "status": self.status.value,
            "execution_count": self.execution_count,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "last_status": self.last_status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class SEPAMandate:
    """
    SEPA Direct Debit Mandate (Mandat de prélèvement)
    """
    mandate_id: str = field(default_factory=lambda: f"MNDT{uuid.uuid4().hex[:12].upper()}")

    # Debtor (the account holder giving permission)
    debtor_iban: str = ""
    debtor_bic: str = ""
    debtor_name: str = ""
    customer_id: str = ""

    # Creditor (the one who will collect)
    creditor_id: str = ""  # SEPA Creditor Identifier
    creditor_name: str = ""
    creditor_iban: str = ""
    creditor_bic: str = ""

    # Mandate details
    mandate_type: MandateType = MandateType.CORE
    signature_date: date = field(default_factory=date.today)
    signature_location: str = ""

    # Limits
    max_amount: Optional[Decimal] = None  # Max per debit
    max_frequency: Optional[str] = None   # "monthly", "quarterly", etc.

    # Status
    status: MandateStatus = MandateStatus.ACTIVE

    # Sequence tracking
    sequence_type: str = "FRST"  # FRST, RCUR, OOFF, FNAL
    first_collection_date: Optional[date] = None
    last_collection_date: Optional[date] = None
    collection_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    cancellation_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "mandate_id": self.mandate_id,
            "debtor_iban": self.debtor_iban,
            "debtor_bic": self.debtor_bic,
            "debtor_name": self.debtor_name,
            "customer_id": self.customer_id,
            "creditor_id": self.creditor_id,
            "creditor_name": self.creditor_name,
            "creditor_iban": self.creditor_iban,
            "creditor_bic": self.creditor_bic,
            "mandate_type": self.mandate_type.value,
            "signature_date": self.signature_date.isoformat(),
            "signature_location": self.signature_location,
            "max_amount": str(self.max_amount) if self.max_amount else None,
            "max_frequency": self.max_frequency,
            "status": self.status.value,
            "sequence_type": self.sequence_type,
            "first_collection_date": self.first_collection_date.isoformat() if self.first_collection_date else None,
            "last_collection_date": self.last_collection_date.isoformat() if self.last_collection_date else None,
            "collection_count": self.collection_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancellation_reason": self.cancellation_reason,
        }

    def can_collect(self, amount: Decimal) -> bool:
        """Check if a collection is allowed"""
        if self.status != MandateStatus.ACTIVE:
            return False
        if self.max_amount and amount > self.max_amount:
            return False
        return True

    def update_sequence(self):
        """Update sequence type after collection"""
        self.collection_count += 1
        if self.sequence_type == "FRST":
            self.sequence_type = "RCUR"
        self.last_collection_date = date.today()
        self.updated_at = datetime.now()
