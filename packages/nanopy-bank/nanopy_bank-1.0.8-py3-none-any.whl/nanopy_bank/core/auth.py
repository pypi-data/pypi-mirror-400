"""
Authentication and User Management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
import uuid
import hashlib


class UserRole(Enum):
    """User roles with different access levels"""
    CLIENT = "client"           # Voir ses comptes uniquement
    ADVISOR = "advisor"         # Voir son portefeuille clients
    DIRECTOR = "director"       # Voir son agence + equipe
    ADMIN = "admin"             # Acces admin banque
    HOLDING = "holding"         # Acces groupe/holding


class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    LOCKED = "locked"
    PENDING = "pending"
    DISABLED = "disabled"


@dataclass
class User:
    """
    User account for authentication
    """
    user_id: str = field(default_factory=lambda: f"USR{uuid.uuid4().hex[:8].upper()}")

    # Credentials
    client_id: str = ""  # 8-digit bank identifier (identifiant bancaire)
    email: str = ""
    password_hash: str = ""

    # Role
    role: UserRole = UserRole.CLIENT

    # Links to entities
    customer_id: Optional[str] = None      # If role=CLIENT
    employee_id: Optional[str] = None      # If role=ADVISOR/DIRECTOR/ADMIN
    holding_id: Optional[str] = None       # If role=HOLDING

    # Profile
    display_name: str = ""
    avatar_url: str = ""
    language: str = "fr"
    timezone: str = "Europe/Paris"

    # Security
    status: UserStatus = UserStatus.ACTIVE
    mfa_enabled: bool = False
    mfa_secret: str = ""

    # Session
    last_login: Optional[datetime] = None
    last_ip: str = ""
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def set_password(self, password: str):
        """Hash and set password"""
        salt = uuid.uuid4().hex[:16]
        self.password_hash = f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"

    def check_password(self, password: str) -> bool:
        """Verify password"""
        if not self.password_hash or ":" not in self.password_hash:
            return False
        salt, hash_value = self.password_hash.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value

    def can_access(self, required_role: UserRole) -> bool:
        """Check if user has required access level"""
        hierarchy = {
            UserRole.CLIENT: 1,
            UserRole.ADVISOR: 2,
            UserRole.DIRECTOR: 3,
            UserRole.ADMIN: 4,
            UserRole.HOLDING: 5,
        }
        return hierarchy.get(self.role, 0) >= hierarchy.get(required_role, 0)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "client_id": self.client_id,
            "email": self.email,
            "role": self.role.value,
            "customer_id": self.customer_id,
            "employee_id": self.employee_id,
            "holding_id": self.holding_id,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "language": self.language,
            "timezone": self.timezone,
            "status": self.status.value,
            "mfa_enabled": self.mfa_enabled,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_ip": self.last_ip,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class Session:
    """
    User session
    """
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    user_id: str = ""

    # Session info
    ip_address: str = ""
    user_agent: str = ""
    device_type: str = ""  # web, mobile, api

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    last_activity: datetime = field(default_factory=datetime.now)

    # Status
    is_active: bool = True

    def is_expired(self) -> bool:
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return not self.is_active


class AuthService:
    """
    Authentication service
    """

    def __init__(self):
        self.users: dict[str, User] = {}
        self.sessions: dict[str, Session] = {}
        self._create_demo_users()

    def _create_demo_users(self):
        """Create demo users for testing"""
        # Client - 1xxxxxxx
        client = User(
            user_id="USR_CLIENT",
            client_id="10000001",
            email="client@nanopybank.fr",
            role=UserRole.CLIENT,
            customer_id="CUST001",
            display_name="Jean Dupont"
        )
        client.set_password("demo123")
        self.users[client.client_id] = client

        # Advisor - 2xxxxxxx
        advisor = User(
            user_id="USR_ADVISOR",
            client_id="20000001",
            email="advisor@nanopybank.fr",
            role=UserRole.ADVISOR,
            employee_id="EMP003",
            display_name="Thomas Moreau"
        )
        advisor.set_password("demo123")
        self.users[advisor.client_id] = advisor

        # Director - 3xxxxxxx
        director = User(
            user_id="USR_DIRECTOR",
            client_id="30000001",
            email="director@nanopybank.fr",
            role=UserRole.DIRECTOR,
            employee_id="EMP002",
            display_name="Camille Leroy"
        )
        director.set_password("demo123")
        self.users[director.client_id] = director

        # Admin - 4xxxxxxx
        admin = User(
            user_id="USR_ADMIN",
            client_id="40000001",
            email="admin@nanopybank.fr",
            role=UserRole.ADMIN,
            employee_id="EMP001",
            display_name="Laurent Dubois"
        )
        admin.set_password("demo123")
        self.users[admin.client_id] = admin

        # Holding - 5xxxxxxx
        holding = User(
            user_id="USR_HOLDING",
            client_id="50000001",
            email="holding@novaxgenesis.fr",
            role=UserRole.HOLDING,
            holding_id="HOLD001",
            display_name="Nova x Genesis"
        )
        holding.set_password("demo123")
        self.users[holding.client_id] = holding

    def login(self, email: str, password: str, ip: str = "") -> Optional[Session]:
        """Authenticate user by email and create session (legacy)"""
        # Find user by email
        user = None
        for u in self.users.values():
            if u.email == email:
                user = u
                break

        if not user:
            return None

        return self._authenticate(user, password, ip)

    def login_by_client_id(self, client_id: str, password: str, ip: str = "") -> Optional[Session]:
        """Authenticate user by bank client ID and create session"""
        user = self.users.get(client_id)

        if not user:
            return None

        return self._authenticate(user, password, ip)

    def _authenticate(self, user: User, password: str, ip: str = "") -> Optional[Session]:
        """Internal authentication logic"""
        if user.status != UserStatus.ACTIVE:
            return None

        if user.locked_until and datetime.now() < user.locked_until:
            return None

        if not user.check_password(password):
            user.failed_attempts += 1
            if user.failed_attempts >= 5:
                from datetime import timedelta
                user.locked_until = datetime.now() + timedelta(minutes=15)
            return None

        # Success
        user.failed_attempts = 0
        user.last_login = datetime.now()
        user.last_ip = ip

        # Create session
        session = Session(
            user_id=user.user_id,
            ip_address=ip,
        )
        self.sessions[session.session_id] = session

        return session

    def logout(self, session_id: str):
        """End session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False

    def get_user(self, email: str) -> Optional[User]:
        """Get user by email"""
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    def get_user_by_client_id(self, client_id: str) -> Optional[User]:
        """Get user by bank client ID"""
        return self.users.get(client_id)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for user in self.users.values():
            if user.user_id == user_id:
                return user
        return None

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get active session"""
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            session.last_activity = datetime.now()
            return session
        return None


# Global auth service
_auth_service: Optional[AuthService] = None

def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
