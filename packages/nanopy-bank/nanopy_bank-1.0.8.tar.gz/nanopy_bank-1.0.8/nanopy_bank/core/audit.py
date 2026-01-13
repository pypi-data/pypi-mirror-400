"""
Audit and Security Models - Logging, Events, Compliance
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, Dict, Any
import uuid
import hashlib
import json


class AuditAction(Enum):
    """Types of auditable actions"""
    # Account actions
    ACCOUNT_CREATE = "account_create"
    ACCOUNT_UPDATE = "account_update"
    ACCOUNT_CLOSE = "account_close"
    ACCOUNT_FREEZE = "account_freeze"
    ACCOUNT_UNFREEZE = "account_unfreeze"

    # Transaction actions
    TRANSACTION_CREATE = "transaction_create"
    TRANSACTION_APPROVE = "transaction_approve"
    TRANSACTION_REJECT = "transaction_reject"
    TRANSACTION_REVERSE = "transaction_reverse"

    # Customer actions
    CUSTOMER_CREATE = "customer_create"
    CUSTOMER_UPDATE = "customer_update"
    CUSTOMER_KYC_UPDATE = "customer_kyc_update"
    CUSTOMER_BLOCK = "customer_block"

    # Card actions
    CARD_CREATE = "card_create"
    CARD_ACTIVATE = "card_activate"
    CARD_BLOCK = "card_block"
    CARD_REPLACE = "card_replace"

    # Loan actions
    LOAN_CREATE = "loan_create"
    LOAN_APPROVE = "loan_approve"
    LOAN_REJECT = "loan_reject"
    LOAN_PAYMENT = "loan_payment"

    # Admin actions
    ADMIN_LOGIN = "admin_login"
    ADMIN_LOGOUT = "admin_logout"
    SETTINGS_CHANGE = "settings_change"
    FEE_UPDATE = "fee_update"
    RATE_UPDATE = "rate_update"

    # Security actions
    PASSWORD_CHANGE = "password_change"
    PIN_CHANGE = "pin_change"
    LIMIT_CHANGE = "limit_change"


class SecurityEventType(Enum):
    """Types of security events"""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGIN_BLOCKED = "login_blocked"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    SESSION_EXPIRED = "session_expired"

    # Suspicious activity
    UNUSUAL_LOCATION = "unusual_location"
    UNUSUAL_TIME = "unusual_time"
    UNUSUAL_AMOUNT = "unusual_amount"
    VELOCITY_CHECK = "velocity_check"
    FRAUD_DETECTED = "fraud_detected"

    # Card events
    CARD_STOLEN = "card_stolen"
    CARD_CLONED = "card_cloned"
    CARD_MISUSE = "card_misuse"
    PIN_ATTEMPTS = "pin_attempts"

    # Account events
    ACCOUNT_TAKEOVER = "account_takeover"
    BENEFICIARY_CHANGE = "beneficiary_change"
    CONTACT_CHANGE = "contact_change"
    DEVICE_CHANGE = "device_change"

    # Compliance
    AML_ALERT = "aml_alert"
    SANCTION_CHECK = "sanction_check"
    PEP_CHECK = "pep_check"
    LARGE_TRANSACTION = "large_transaction"


class RiskLevel(Enum):
    """Risk levels for security events"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(Enum):
    """Status of security events"""
    NEW = "new"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


@dataclass
class AuditLog:
    """
    Audit trail for all banking operations
    """
    log_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Action details
    action: AuditAction = AuditAction.ACCOUNT_CREATE
    description: str = ""

    # Who
    actor_type: str = "user"  # user, employee, system, api
    actor_id: str = ""
    actor_name: str = ""
    actor_ip: str = ""
    actor_device: str = ""

    # What
    entity_type: str = ""  # account, transaction, customer, card, loan
    entity_id: str = ""
    entity_name: str = ""

    # Changes
    old_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # When
    timestamp: datetime = field(default_factory=datetime.now)

    # Result
    success: bool = True
    error_message: str = ""

    # Compliance
    requires_review: bool = False
    reviewed_by: str = ""
    reviewed_at: Optional[datetime] = None

    def __post_init__(self):
        # Generate hash for integrity
        self._hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute hash of log entry for integrity verification"""
        data = f"{self.log_id}|{self.action.value}|{self.actor_id}|{self.entity_id}|{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def verify_integrity(self) -> bool:
        """Verify log entry hasn't been tampered with"""
        return self._hash == self._compute_hash()

    def to_dict(self) -> dict:
        return {
            "log_id": self.log_id,
            "action": self.action.value,
            "description": self.description,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "actor_ip": self.actor_ip,
            "actor_device": self.actor_device,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "entity_name": self.entity_name,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error_message": self.error_message,
            "requires_review": self.requires_review,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "hash": self._hash,
        }


@dataclass
class SecurityEvent:
    """
    Security event / alert
    """
    event_id: str = field(default_factory=lambda: f"SEC{uuid.uuid4().hex[:10].upper()}")

    # Event details
    event_type: SecurityEventType = SecurityEventType.LOGIN_FAILURE
    risk_level: RiskLevel = RiskLevel.LOW
    status: EventStatus = EventStatus.NEW

    # Description
    title: str = ""
    description: str = ""
    recommendation: str = ""

    # Who is affected
    customer_id: Optional[str] = None
    account_iban: Optional[str] = None
    card_id: Optional[str] = None
    employee_id: Optional[str] = None

    # Context
    ip_address: str = ""
    user_agent: str = ""
    device_id: str = ""
    location: str = ""
    country: str = ""

    # Transaction related
    transaction_id: Optional[str] = None
    amount: Optional[Decimal] = None

    # Timing
    detected_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    # Investigation
    assigned_to: str = ""
    notes: str = ""
    resolution: str = ""

    # Related events
    related_events: list = field(default_factory=list)

    # Metadata
    raw_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def escalate(self, new_level: RiskLevel, reason: str):
        """Escalate event to higher risk level"""
        self.risk_level = new_level
        self.notes += f"\n[Escalated] {datetime.now().isoformat()}: {reason}"

    def resolve(self, resolution: str, resolved_by: str):
        """Mark event as resolved"""
        self.status = EventStatus.RESOLVED
        self.resolution = resolution
        self.resolved_at = datetime.now()
        self.notes += f"\n[Resolved] {datetime.now().isoformat()} by {resolved_by}: {resolution}"

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "risk_level": self.risk_level.value,
            "status": self.status.value,
            "title": self.title,
            "description": self.description,
            "recommendation": self.recommendation,
            "customer_id": self.customer_id,
            "account_iban": self.account_iban,
            "card_id": self.card_id,
            "employee_id": self.employee_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "device_id": self.device_id,
            "location": self.location,
            "country": self.country,
            "transaction_id": self.transaction_id,
            "amount": str(self.amount) if self.amount else None,
            "detected_at": self.detected_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "assigned_to": self.assigned_to,
            "notes": self.notes,
            "resolution": self.resolution,
            "related_events": self.related_events,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ComplianceCheck:
    """
    Compliance verification record (KYC, AML, etc.)
    """
    check_id: str = field(default_factory=lambda: f"CHK{uuid.uuid4().hex[:10].upper()}")

    # Check type
    check_type: str = ""  # kyc, aml, sanction, pep, fatca
    customer_id: str = ""

    # Result
    passed: bool = True
    score: int = 0  # Risk score 0-100
    findings: list = field(default_factory=list)

    # Documents
    documents_verified: list = field(default_factory=list)
    documents_missing: list = field(default_factory=list)

    # External checks
    external_provider: str = ""
    external_reference: str = ""
    external_response: Dict[str, Any] = field(default_factory=dict)

    # Status
    status: str = "pending"  # pending, passed, failed, review
    requires_review: bool = False
    reviewed_by: str = ""
    reviewed_at: Optional[datetime] = None
    review_notes: str = ""

    # Validity
    valid_until: Optional[datetime] = None
    next_review: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "check_type": self.check_type,
            "customer_id": self.customer_id,
            "passed": self.passed,
            "score": self.score,
            "findings": self.findings,
            "documents_verified": self.documents_verified,
            "documents_missing": self.documents_missing,
            "external_provider": self.external_provider,
            "external_reference": self.external_reference,
            "status": self.status,
            "requires_review": self.requires_review,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "review_notes": self.review_notes,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "next_review": self.next_review.isoformat() if self.next_review else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AuditLogger:
    """
    Helper class to create audit logs easily
    """

    def __init__(self):
        self.logs: list[AuditLog] = []

    def log(
        self,
        action: AuditAction,
        actor_id: str,
        entity_type: str,
        entity_id: str,
        description: str = "",
        old_values: dict = None,
        new_values: dict = None,
        **kwargs
    ) -> AuditLog:
        """Create and store an audit log entry"""
        log = AuditLog(
            action=action,
            description=description or f"{action.value} on {entity_type} {entity_id}",
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values or {},
            new_values=new_values or {},
            **kwargs
        )
        self.logs.append(log)
        return log

    def get_logs(
        self,
        entity_id: str = None,
        actor_id: str = None,
        action: AuditAction = None,
        from_date: datetime = None,
        to_date: datetime = None
    ) -> list[AuditLog]:
        """Query audit logs with filters"""
        results = self.logs

        if entity_id:
            results = [l for l in results if l.entity_id == entity_id]
        if actor_id:
            results = [l for l in results if l.actor_id == actor_id]
        if action:
            results = [l for l in results if l.action == action]
        if from_date:
            results = [l for l in results if l.timestamp >= from_date]
        if to_date:
            results = [l for l in results if l.timestamp <= to_date]

        return sorted(results, key=lambda x: x.timestamp, reverse=True)
