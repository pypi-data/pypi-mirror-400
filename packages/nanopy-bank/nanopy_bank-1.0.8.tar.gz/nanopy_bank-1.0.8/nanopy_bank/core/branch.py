"""
Branch and Employee models - Bank organization structure
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict
import uuid


class BranchType(Enum):
    """Types of branches"""
    HEADQUARTERS = "headquarters"   # Siège social
    REGIONAL = "regional"           # Direction régionale
    BRANCH = "branch"               # Agence
    ONLINE = "online"               # Banque en ligne
    ATM_ONLY = "atm_only"           # Point automatique


class EmployeeRole(Enum):
    """Employee roles"""
    DIRECTOR = "director"           # Directeur
    MANAGER = "manager"             # Responsable
    ADVISOR = "advisor"             # Conseiller
    TELLER = "teller"               # Guichetier
    ANALYST = "analyst"             # Analyste
    SUPPORT = "support"             # Support client
    IT = "it"                       # Informatique
    COMPLIANCE = "compliance"       # Conformité
    RISK = "risk"                   # Risques


class EmployeeStatus(Enum):
    """Employee status"""
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


@dataclass
class Branch:
    """
    Bank branch / Agency
    """
    branch_id: str = field(default_factory=lambda: f"BR{uuid.uuid4().hex[:6].upper()}")
    branch_code: str = ""  # Code guichet (5 digits in France)

    # Branch info
    name: str = ""
    branch_type: BranchType = BranchType.BRANCH

    # Location
    address: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "FR"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Contact
    phone: str = ""
    fax: str = ""
    email: str = ""

    # Opening hours
    opening_hours: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "monday": {"open": "09:00", "close": "17:00"},
        "tuesday": {"open": "09:00", "close": "17:00"},
        "wednesday": {"open": "09:00", "close": "17:00"},
        "thursday": {"open": "09:00", "close": "17:00"},
        "friday": {"open": "09:00", "close": "17:00"},
        "saturday": {"open": "09:00", "close": "12:00"},
        "sunday": {"open": "", "close": ""},  # Closed
    })

    # Services
    services: List[str] = field(default_factory=lambda: [
        "accounts", "cards", "loans", "insurance", "savings"
    ])
    has_atm: bool = True
    has_safe_deposit: bool = False  # Coffres
    wheelchair_accessible: bool = True

    # Hierarchy
    parent_branch_id: Optional[str] = None  # For regional structure
    manager_employee_id: Optional[str] = None

    # Statistics
    customer_count: int = 0
    account_count: int = 0
    total_deposits: Decimal = Decimal("0.00")
    total_loans: Decimal = Decimal("0.00")

    # Status
    is_active: bool = True
    opened_date: date = field(default_factory=date.today)
    closed_date: Optional[date] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def is_open_now(self) -> bool:
        """Check if branch is currently open"""
        now = datetime.now()
        day = now.strftime("%A").lower()
        hours = self.opening_hours.get(day, {})

        if not hours.get("open") or not hours.get("close"):
            return False

        open_time = datetime.strptime(hours["open"], "%H:%M").time()
        close_time = datetime.strptime(hours["close"], "%H:%M").time()
        current_time = now.time()

        return open_time <= current_time <= close_time

    def to_dict(self) -> dict:
        return {
            "branch_id": self.branch_id,
            "branch_code": self.branch_code,
            "name": self.name,
            "branch_type": self.branch_type.value,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "fax": self.fax,
            "email": self.email,
            "opening_hours": self.opening_hours,
            "services": self.services,
            "has_atm": self.has_atm,
            "has_safe_deposit": self.has_safe_deposit,
            "wheelchair_accessible": self.wheelchair_accessible,
            "parent_branch_id": self.parent_branch_id,
            "manager_employee_id": self.manager_employee_id,
            "customer_count": self.customer_count,
            "account_count": self.account_count,
            "total_deposits": str(self.total_deposits),
            "total_loans": str(self.total_loans),
            "is_active": self.is_active,
            "is_open_now": self.is_open_now(),
            "opened_date": self.opened_date.isoformat(),
            "closed_date": self.closed_date.isoformat() if self.closed_date else None,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Employee:
    """
    Bank employee
    """
    employee_id: str = field(default_factory=lambda: f"EMP{uuid.uuid4().hex[:8].upper()}")
    employee_number: str = ""  # Matricule

    # Personal info
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    mobile: str = ""

    # Role
    role: EmployeeRole = EmployeeRole.ADVISOR
    title: str = ""  # Job title
    department: str = ""
    branch_id: Optional[str] = None
    manager_id: Optional[str] = None

    # Permissions
    permissions: List[str] = field(default_factory=list)
    max_approval_amount: Decimal = Decimal("0.00")  # Max amount they can approve
    can_approve_loans: bool = False
    can_manage_accounts: bool = True
    can_view_all_customers: bool = False

    # Work info
    hire_date: date = field(default_factory=date.today)
    contract_type: str = "permanent"  # permanent, temporary, intern
    work_schedule: str = "full_time"  # full_time, part_time

    # Status
    status: EmployeeStatus = EmployeeStatus.ACTIVE

    # Performance
    customers_managed: int = 0
    transactions_processed: int = 0
    loans_approved: int = 0
    total_loan_amount_approved: Decimal = Decimal("0.00")

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def can_approve(self, amount: Decimal) -> bool:
        """Check if employee can approve this amount"""
        return self.can_approve_loans and amount <= self.max_approval_amount

    def to_dict(self) -> dict:
        return {
            "employee_id": self.employee_id,
            "employee_number": self.employee_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
            "role": self.role.value,
            "title": self.title,
            "department": self.department,
            "branch_id": self.branch_id,
            "manager_id": self.manager_id,
            "permissions": self.permissions,
            "max_approval_amount": str(self.max_approval_amount),
            "can_approve_loans": self.can_approve_loans,
            "can_manage_accounts": self.can_manage_accounts,
            "can_view_all_customers": self.can_view_all_customers,
            "hire_date": self.hire_date.isoformat(),
            "contract_type": self.contract_type,
            "work_schedule": self.work_schedule,
            "status": self.status.value,
            "customers_managed": self.customers_managed,
            "transactions_processed": self.transactions_processed,
            "loans_approved": self.loans_approved,
            "total_loan_amount_approved": str(self.total_loan_amount_approved),
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


@dataclass
class ATM:
    """
    ATM / Distributeur automatique
    """
    atm_id: str = field(default_factory=lambda: f"ATM{uuid.uuid4().hex[:6].upper()}")
    branch_id: Optional[str] = None

    # Location
    name: str = ""
    address: str = ""
    city: str = ""
    postal_code: str = ""
    country: str = "FR"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_type: str = "indoor"  # indoor, outdoor, mall, station

    # Services
    can_withdraw: bool = True
    can_deposit_cash: bool = False
    can_deposit_check: bool = False
    can_check_balance: bool = True
    can_transfer: bool = False
    can_print_statement: bool = True

    # Limits
    max_withdrawal: Decimal = Decimal("500.00")
    max_deposit: Decimal = Decimal("3000.00")

    # Status
    is_active: bool = True
    is_online: bool = True
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[date] = None

    # Cash levels
    cash_level: int = 100  # Percentage
    low_cash_threshold: int = 20

    # Statistics
    transactions_today: int = 0
    total_withdrawn_today: Decimal = Decimal("0.00")

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "atm_id": self.atm_id,
            "branch_id": self.branch_id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "postal_code": self.postal_code,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_type": self.location_type,
            "can_withdraw": self.can_withdraw,
            "can_deposit_cash": self.can_deposit_cash,
            "can_deposit_check": self.can_deposit_check,
            "can_check_balance": self.can_check_balance,
            "can_transfer": self.can_transfer,
            "can_print_statement": self.can_print_statement,
            "max_withdrawal": str(self.max_withdrawal),
            "max_deposit": str(self.max_deposit),
            "is_active": self.is_active,
            "is_online": self.is_online,
            "last_maintenance": self.last_maintenance.isoformat() if self.last_maintenance else None,
            "next_maintenance": self.next_maintenance.isoformat() if self.next_maintenance else None,
            "cash_level": self.cash_level,
            "low_cash_threshold": self.low_cash_threshold,
            "needs_cash": self.cash_level < self.low_cash_threshold,
            "transactions_today": self.transactions_today,
            "total_withdrawn_today": str(self.total_withdrawn_today),
            "created_at": self.created_at.isoformat(),
        }
