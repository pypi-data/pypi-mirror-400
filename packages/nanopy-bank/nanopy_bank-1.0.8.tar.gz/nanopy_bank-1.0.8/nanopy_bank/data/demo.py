"""
Demo/Test Data for NanoPy Bank

This file contains all fake data for testing and demonstration purposes.
Nothing is hardcoded in the main model files.
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# Import models
from ..core.models import (
    Customer, Account, Transaction, Card,
    AccountType, AccountStatus, Currency,
    TransactionType,
    CardType, CardStatus
)
from ..core.beneficiary import (
    Beneficiary, StandingOrder, SEPAMandate,
    OrderFrequency, OrderStatus, MandateType, MandateStatus
)
from ..core.products import (
    Loan, Insurance, SavingsProduct,
    LoanType, LoanStatus, InsuranceType, SavingsType
)
from ..core.fees import Fee, InterestRate, FeeType, RateType
from ..core.branch import Branch, Employee, ATM, BranchType, EmployeeRole


# =============================================================================
# DEMO CUSTOMERS
# =============================================================================

DEMO_CUSTOMERS = [
    {
        "customer_id": "CUST001",
        "first_name": "Jean",
        "last_name": "Dupont",
        "email": "jean.dupont@email.fr",
        "phone": "+33612345678",
        "address": "15 Rue de la Paix",
        "city": "Paris",
        "postal_code": "75001",
        "country": "FR",
        "birth_date": date(1985, 3, 15),
        "nationality": "FR",
        "occupation": "Ingenieur",
        "income_range": "50000-75000",
    },
    {
        "customer_id": "CUST002",
        "first_name": "Marie",
        "last_name": "Martin",
        "email": "marie.martin@email.fr",
        "phone": "+33623456789",
        "address": "42 Avenue des Champs",
        "city": "Lyon",
        "postal_code": "69001",
        "country": "FR",
        "birth_date": date(1990, 7, 22),
        "nationality": "FR",
        "occupation": "Medecin",
        "income_range": "75000-100000",
    },
    {
        "customer_id": "CUST003",
        "first_name": "Pierre",
        "last_name": "Bernard",
        "email": "pierre.bernard@email.fr",
        "phone": "+33634567890",
        "address": "8 Boulevard Victor Hugo",
        "city": "Marseille",
        "postal_code": "13001",
        "country": "FR",
        "birth_date": date(1978, 11, 8),
        "nationality": "FR",
        "occupation": "Commercant",
        "income_range": "35000-50000",
    },
    {
        "customer_id": "CUST004",
        "first_name": "Sophie",
        "last_name": "Petit",
        "email": "sophie.petit@email.fr",
        "phone": "+33645678901",
        "address": "25 Rue du Commerce",
        "city": "Bordeaux",
        "postal_code": "33000",
        "country": "FR",
        "birth_date": date(1995, 1, 30),
        "nationality": "FR",
        "occupation": "Etudiante",
        "income_range": "0-15000",
    },
]


# =============================================================================
# DEMO ACCOUNTS
# =============================================================================

DEMO_ACCOUNTS = [
    # Jean Dupont - Compte courant
    {
        "iban": "FR7630001007941234567890185",
        "bic": "NANPFRPP",
        "customer_id": "CUST001",
        "account_type": AccountType.CHECKING,
        "account_name": "Compte Courant",
        "currency": Currency.EUR,
        "balance": Decimal("3542.87"),
        "overdraft_limit": Decimal("500.00"),
    },
    # Jean Dupont - Livret A
    {
        "iban": "FR7630001007941234567890186",
        "bic": "NANPFRPP",
        "customer_id": "CUST001",
        "account_type": AccountType.SAVINGS,
        "account_name": "Livret A",
        "currency": Currency.EUR,
        "balance": Decimal("15000.00"),
    },
    # Marie Martin - Compte courant
    {
        "iban": "FR7630001007942345678901234",
        "bic": "NANPFRPP",
        "customer_id": "CUST002",
        "account_type": AccountType.CHECKING,
        "account_name": "Compte Courant",
        "currency": Currency.EUR,
        "balance": Decimal("8234.56"),
        "overdraft_limit": Decimal("1000.00"),
    },
    # Pierre Bernard - Compte courant
    {
        "iban": "FR7630001007943456789012345",
        "bic": "NANPFRPP",
        "customer_id": "CUST003",
        "account_type": AccountType.CHECKING,
        "account_name": "Compte Pro",
        "currency": Currency.EUR,
        "balance": Decimal("12456.00"),
        "overdraft_limit": Decimal("2000.00"),
    },
    # Sophie Petit - Compte courant
    {
        "iban": "FR7630001007944567890123456",
        "bic": "NANPFRPP",
        "customer_id": "CUST004",
        "account_type": AccountType.CHECKING,
        "account_name": "Compte Courant",
        "currency": Currency.EUR,
        "balance": Decimal("456.23"),
        "overdraft_limit": Decimal("200.00"),
    },
]


# =============================================================================
# DEMO TRANSACTIONS
# =============================================================================

def generate_demo_transactions():
    """Generate realistic demo transactions"""
    transactions = []
    base_date = datetime.now() - timedelta(days=90)

    # Transaction templates
    templates = [
        # Credits
        {"label": "VIREMENT SALAIRE", "amount": Decimal("2850.00"), "type": TransactionType.CREDIT_TRANSFER, "is_salary": True},
        {"label": "REMBOURSEMENT SECU", "amount": Decimal("45.60"), "type": TransactionType.CREDIT_TRANSFER},
        {"label": "VIREMENT DE M. DUPONT", "amount": Decimal("150.00"), "type": TransactionType.CREDIT_TRANSFER},

        # Debits
        {"label": "LOYER JANVIER", "amount": Decimal("850.00"), "type": TransactionType.DIRECT_DEBIT},
        {"label": "EDF ELECTRICITE", "amount": Decimal("78.45"), "type": TransactionType.DIRECT_DEBIT},
        {"label": "ORANGE MOBILE", "amount": Decimal("29.99"), "type": TransactionType.DIRECT_DEBIT},
        {"label": "CARREFOUR PARIS", "amount": Decimal("156.78"), "type": TransactionType.CARD_PAYMENT},
        {"label": "AMAZON EU", "amount": Decimal("45.99"), "type": TransactionType.CARD_PAYMENT},
        {"label": "SNCF CONNECT", "amount": Decimal("89.00"), "type": TransactionType.CARD_PAYMENT},
        {"label": "RETRAIT DAB 75001", "amount": Decimal("60.00"), "type": TransactionType.ATM_WITHDRAWAL},
        {"label": "BOULANGERIE PAUL", "amount": Decimal("8.50"), "type": TransactionType.CARD_PAYMENT},
        {"label": "UBER EATS", "amount": Decimal("22.40"), "type": TransactionType.CARD_PAYMENT},
    ]

    # Generate transactions for each account
    for account in DEMO_ACCOUNTS:
        if account["account_type"] != AccountType.CHECKING:
            continue

        iban = account["iban"]
        current_date = base_date

        for i in range(30):
            # Pick random templates
            num_tx = random.randint(1, 4)
            for _ in range(num_tx):
                template = random.choice(templates)

                is_credit = template["type"] == TransactionType.CREDIT_TRANSFER

                tx = {
                    "account_iban": iban,
                    "transaction_type": template["type"],
                    "amount": template["amount"] + Decimal(str(random.randint(-10, 10))),
                    "currency": "EUR",
                    "label": template["label"],
                    "description": f"Transaction du {current_date.strftime('%d/%m/%Y')}",
                    "created_at": current_date + timedelta(hours=random.randint(8, 20)),
                    "is_credit": is_credit,
                }

                if not is_credit:
                    tx["counterparty_name"] = template["label"].split()[0]

                transactions.append(tx)

            current_date += timedelta(days=random.randint(1, 5))
            if current_date > datetime.now():
                break

    return transactions

DEMO_TRANSACTIONS = generate_demo_transactions()


# =============================================================================
# DEMO CARDS
# =============================================================================

DEMO_CARDS = [
    {
        "card_number": "4970XXXXXXXX1234",
        "customer_id": "CUST001",
        "account_iban": "FR7630001007941234567890185",
        "card_type": CardType.DEBIT,
        "cardholder_name": "JEAN DUPONT",
        "expiry_date": "12/27",
        "daily_limit": Decimal("1000.00"),
        "monthly_limit": Decimal("5000.00"),
        "contactless_enabled": True,
        "online_enabled": True,
    },
    {
        "card_number": "4970XXXXXXXX2345",
        "customer_id": "CUST002",
        "account_iban": "FR7630001007942345678901234",
        "card_type": CardType.CREDIT,
        "cardholder_name": "MARIE MARTIN",
        "expiry_date": "06/28",
        "daily_limit": Decimal("2000.00"),
        "monthly_limit": Decimal("10000.00"),
        "contactless_enabled": True,
        "online_enabled": True,
    },
    {
        "card_number": "4970XXXXXXXX3456",
        "customer_id": "CUST003",
        "account_iban": "FR7630001007943456789012345",
        "card_type": CardType.BUSINESS,
        "cardholder_name": "PIERRE BERNARD",
        "expiry_date": "09/26",
        "daily_limit": Decimal("3000.00"),
        "monthly_limit": Decimal("15000.00"),
        "contactless_enabled": True,
        "online_enabled": True,
    },
]


# =============================================================================
# DEMO BENEFICIARIES
# =============================================================================

DEMO_BENEFICIARIES = [
    {
        "customer_id": "CUST001",
        "name": "Marie Dupont",
        "iban": "FR7614410000011234567890123",
        "bic": "AGRIFRPP",
        "alias": "Maman",
        "category": "family",
        "is_favorite": True,
    },
    {
        "customer_id": "CUST001",
        "name": "SCI Les Lilas",
        "iban": "FR7630004000031234567890143",
        "bic": "BNPAFRPP",
        "alias": "Proprietaire",
        "category": "bills",
        "is_favorite": True,
    },
    {
        "customer_id": "CUST002",
        "name": "Auto-Ecole Victor",
        "iban": "FR7610278060000002038650128",
        "bic": "CMCIFR2A",
        "alias": "Permis",
        "category": "services",
    },
]


# =============================================================================
# DEMO STANDING ORDERS
# =============================================================================

DEMO_STANDING_ORDERS = [
    {
        "from_iban": "FR7630001007941234567890185",
        "customer_id": "CUST001",
        "to_iban": "FR7630004000031234567890143",
        "to_name": "SCI Les Lilas",
        "amount": Decimal("850.00"),
        "frequency": OrderFrequency.MONTHLY,
        "execution_day": 5,
        "label": "Loyer mensuel",
        "category": "housing",
    },
    {
        "from_iban": "FR7630001007941234567890185",
        "customer_id": "CUST001",
        "to_iban": "FR7630001007941234567890186",
        "to_name": "Mon Livret A",
        "amount": Decimal("200.00"),
        "frequency": OrderFrequency.MONTHLY,
        "execution_day": 1,
        "label": "Epargne mensuelle",
        "category": "savings",
    },
]


# =============================================================================
# DEMO FEES (French banking fees)
# =============================================================================

DEMO_FEES = [
    Fee(
        fee_type=FeeType.ACCOUNT_MAINTENANCE,
        name="Frais de tenue de compte",
        description="Frais mensuels de gestion du compte",
        amount=Decimal("2.00"),
        frequency="monthly"
    ),
    Fee(
        fee_type=FeeType.CARD_ANNUAL,
        name="Cotisation carte Visa",
        description="Cotisation annuelle carte bancaire",
        amount=Decimal("45.00"),
        frequency="yearly"
    ),
    Fee(
        fee_type=FeeType.TRANSFER_SEPA,
        name="Virement SEPA",
        description="Virement SEPA occasionnel",
        amount=Decimal("0.00"),
        frequency="per_transaction"
    ),
    Fee(
        fee_type=FeeType.TRANSFER_INTERNATIONAL,
        name="Virement international",
        description="Virement hors zone SEPA",
        amount=Decimal("15.00"),
        frequency="per_transaction"
    ),
    Fee(
        fee_type=FeeType.OVERDRAFT_FEE,
        name="Commission d'intervention",
        description="Par operation en decouvert non autorise",
        amount=Decimal("8.00"),
        frequency="per_transaction"
    ),
    Fee(
        fee_type=FeeType.REJECTED_PAYMENT,
        name="Rejet de prelevement",
        description="Frais pour prelevement rejete",
        amount=Decimal("20.00"),
        frequency="per_transaction"
    ),
    Fee(
        fee_type=FeeType.ATM_WITHDRAWAL_OTHER,
        name="Retrait autre banque",
        description="Au-dela de 3 retraits/mois",
        amount=Decimal("1.00"),
        frequency="per_transaction"
    ),
    Fee(
        fee_type=FeeType.CURRENCY_CONVERSION,
        name="Conversion de devise",
        description="Commission sur operations en devise",
        amount=Decimal("2.00"),
        is_percentage=True,
        frequency="per_transaction"
    ),
]


# =============================================================================
# DEMO INTEREST RATES (French rates 2024)
# =============================================================================

DEMO_RATES = [
    InterestRate(
        rate_type=RateType.SAVINGS,
        name="Livret A",
        rate=Decimal("3.00"),
        product_types=["livret_a"]
    ),
    InterestRate(
        rate_type=RateType.SAVINGS,
        name="LDDS",
        rate=Decimal("3.00"),
        product_types=["ldds"]
    ),
    InterestRate(
        rate_type=RateType.SAVINGS,
        name="LEP",
        rate=Decimal("5.00"),
        product_types=["lep"]
    ),
    InterestRate(
        rate_type=RateType.OVERDRAFT,
        name="Taux decouvert autorise",
        rate=Decimal("7.00"),
        description="Taux annuel pour decouvert autorise"
    ),
    InterestRate(
        rate_type=RateType.OVERDRAFT,
        name="Taux decouvert non autorise",
        rate=Decimal("16.00"),
        description="Taux annuel pour decouvert non autorise"
    ),
    InterestRate(
        rate_type=RateType.LOAN,
        name="Pret personnel",
        rate=Decimal("5.50"),
        product_types=["personal"],
        min_duration_months=12,
        max_duration_months=84
    ),
    InterestRate(
        rate_type=RateType.MORTGAGE,
        name="Pret immobilier 20 ans",
        rate=Decimal("3.80"),
        product_types=["mortgage"],
        min_duration_months=180,
        max_duration_months=300
    ),
]


# =============================================================================
# DEMO BRANCHES
# =============================================================================

DEMO_BRANCHES = [
    Branch(
        branch_id="BR001",
        branch_code="00794",
        name="Agence Paris Opera",
        branch_type=BranchType.BRANCH,
        address="1 Place de l'Opera",
        city="Paris",
        postal_code="75009",
        phone="+33 1 42 68 00 00",
        email="paris.opera@nanopybank.fr",
        has_atm=True,
        has_safe_deposit=True,
    ),
    Branch(
        branch_id="BR002",
        branch_code="00795",
        name="Agence Lyon Part-Dieu",
        branch_type=BranchType.BRANCH,
        address="17 Rue de la Part-Dieu",
        city="Lyon",
        postal_code="69003",
        phone="+33 4 72 00 00 00",
        email="lyon.partdieu@nanopybank.fr",
        has_atm=True,
    ),
    Branch(
        branch_id="BRHQ",
        branch_code="00001",
        name="Siege Social",
        branch_type=BranchType.HEADQUARTERS,
        address="1 Rue de la Banque",
        city="Paris",
        postal_code="75001",
        phone="+33 1 23 45 67 89",
        email="siege@nanopybank.fr",
    ),
]


# =============================================================================
# DEMO EMPLOYEES
# =============================================================================

DEMO_EMPLOYEES = [
    Employee(
        employee_id="EMP001",
        employee_number="M001234",
        first_name="Laurent",
        last_name="Dubois",
        email="laurent.dubois@nanopybank.fr",
        role=EmployeeRole.DIRECTOR,
        title="Directeur General",
        branch_id="BRHQ",
        can_approve_loans=True,
        max_approval_amount=Decimal("1000000.00"),
        can_view_all_customers=True,
    ),
    Employee(
        employee_id="EMP002",
        employee_number="M001235",
        first_name="Camille",
        last_name="Leroy",
        email="camille.leroy@nanopybank.fr",
        role=EmployeeRole.MANAGER,
        title="Directrice d'Agence",
        branch_id="BR001",
        can_approve_loans=True,
        max_approval_amount=Decimal("50000.00"),
    ),
    Employee(
        employee_id="EMP003",
        employee_number="M001236",
        first_name="Thomas",
        last_name="Moreau",
        email="thomas.moreau@nanopybank.fr",
        role=EmployeeRole.ADVISOR,
        title="Conseiller Clientele",
        branch_id="BR001",
        manager_id="EMP002",
    ),
    Employee(
        employee_id="EMP004",
        employee_number="M001237",
        first_name="Emma",
        last_name="Simon",
        email="emma.simon@nanopybank.fr",
        role=EmployeeRole.TELLER,
        title="Guichetiere",
        branch_id="BR002",
    ),
]


# =============================================================================
# DEMO LOANS
# =============================================================================

DEMO_LOANS = [
    Loan(
        loan_id="LN0001",
        customer_id="CUST001",
        account_iban="FR7630001007941234567890185",
        loan_type=LoanType.PERSONAL,
        purpose="Travaux maison",
        principal=Decimal("15000.00"),
        interest_rate=Decimal("5.50"),
        duration_months=48,
        status=LoanStatus.ACTIVE,
        has_insurance=True,
        insurance_premium=Decimal("25.00"),
    ),
    Loan(
        loan_id="LN0002",
        customer_id="CUST002",
        account_iban="FR7630001007942345678901234",
        loan_type=LoanType.AUTO,
        purpose="Achat vehicule",
        principal=Decimal("25000.00"),
        interest_rate=Decimal("4.90"),
        duration_months=60,
        status=LoanStatus.ACTIVE,
    ),
]


# =============================================================================
# DEMO INSURANCE
# =============================================================================

DEMO_INSURANCE = [
    Insurance(
        customer_id="CUST001",
        insurance_type=InsuranceType.HOME,
        product_name="Assurance Habitation Complete",
        coverage_amount=Decimal("200000.00"),
        deductible=Decimal("150.00"),
        premium_amount=Decimal("35.00"),
        premium_frequency="monthly",
        account_iban="FR7630001007941234567890185",
    ),
    Insurance(
        customer_id="CUST002",
        insurance_type=InsuranceType.AUTO,
        product_name="Assurance Auto Tous Risques",
        coverage_amount=Decimal("50000.00"),
        deductible=Decimal("300.00"),
        premium_amount=Decimal("85.00"),
        premium_frequency="monthly",
        account_iban="FR7630001007942345678901234",
    ),
]


# =============================================================================
# DEMO SAVINGS PRODUCTS
# =============================================================================

DEMO_SAVINGS = [
    SavingsProduct(
        customer_id="CUST001",
        account_iban="FR7630001007941234567890186",
        savings_type=SavingsType.LIVRET_A,
        product_name="Livret A",
        interest_rate=Decimal("3.00"),
        max_balance=Decimal("22950.00"),
        is_tax_exempt=True,
    ),
]


# =============================================================================
# HELPER FUNCTION TO CREATE DEMO BANK
# =============================================================================

# =============================================================================
# DEMO HOLDING DATA (Nova x Genesis SASU)
# Holding specialisee dans l'investissement en dette souveraine
# Activite principale: Dette d'Etat / Obligations de guerre
# Filiales: activite secondaire
# =============================================================================

DEMO_HOLDING = {
    "holding": {
        "name": "Nova x Genesis",
        "legal_name": "Nova x Genesis Financial Services SASU",
        "siren": "912 345 678",
        "lei": "969500XXXXXXXXXXXXXX",
        "address": "42 Avenue des Champs-Elysees",
        "city": "Paris",
        "postal_code": "75008",
        "country": "France",
        "capital": Decimal("500000000.00"),  # 500M EUR capital
        "activity": "Investissement en dette souveraine",
    },
    "accounts": {
        "principal": {
            "name": "Compte Principal",
            "iban": "FR76 3000 6000 0112 3456 7890 189",
            "balance": Decimal("85000000.00"),  # 85M EUR
            "currency": "EUR",
        },
        "tresorerie": {
            "name": "Compte Tresorerie",
            "iban": "FR76 3000 6000 0198 7654 3210 012",
            "balance": Decimal("45000000.00"),  # 45M EUR
            "currency": "EUR",
        },
        "titres": {
            "name": "Compte Titres (Dette Souveraine)",
            "iban": "FR76 3000 6000 0199 8765 4321 098",
            "balance": Decimal("120000000.00"),  # 120M EUR cash pour achats
            "currency": "EUR",
        },
    },
    # Filiales
    "subsidiaries": [
        {"id": "SUB001", "name": "NanoPy Bank France", "type": "Banque de detail", "ownership": Decimal("100.00"), "assets": Decimal("2400000000"), "employees": 1250, "status": "active", "pool_balance": Decimal("8500000"), "pool_limit": Decimal("10000000")},
        {"id": "SUB002", "name": "Nova Asset Management", "type": "Gestion d'actifs", "ownership": Decimal("100.00"), "assets": Decimal("850000000"), "employees": 85, "status": "active", "pool_balance": Decimal("-1200000"), "pool_limit": Decimal("5000000")},
        {"id": "SUB003", "name": "Nova Insurance", "type": "Assurance", "ownership": Decimal("85.00"), "assets": Decimal("450000000"), "employees": 320, "status": "active", "pool_balance": Decimal("3800000"), "pool_limit": Decimal("8000000")},
        {"id": "SUB004", "name": "Nova Leasing", "type": "Credit-bail", "ownership": Decimal("100.00"), "assets": Decimal("180000000"), "employees": 45, "status": "active", "pool_balance": Decimal("-450000"), "pool_limit": Decimal("2000000")},
        {"id": "SUB005", "name": "Nova Digital", "type": "Fintech", "ownership": Decimal("70.00"), "assets": Decimal("25000000"), "employees": 60, "status": "startup", "pool_balance": Decimal("650000"), "pool_limit": Decimal("1000000")},
    ],
    "intra_group_loans": [
        {"id": "IGL001", "borrower": "Nova Leasing", "borrower_id": "SUB004", "principal": Decimal("5000000"), "outstanding": Decimal("4200000"), "rate": Decimal("1.25"), "start_date": date(2024, 1, 15), "maturity": date(2027, 12, 31), "status": "active"},
        {"id": "IGL002", "borrower": "Nova Digital", "borrower_id": "SUB005", "principal": Decimal("2500000"), "outstanding": Decimal("2500000"), "rate": Decimal("1.50"), "start_date": date(2025, 3, 1), "maturity": date(2026, 6, 30), "status": "active"},
        {"id": "IGL003", "borrower": "Nova Insurance", "borrower_id": "SUB003", "principal": Decimal("10000000"), "outstanding": Decimal("8500000"), "rate": Decimal("1.00"), "start_date": date(2023, 6, 1), "maturity": date(2028, 12, 31), "status": "active"},
    ],
    "dividends": [
        {"id": "DIV001", "subsidiary": "NanoPy Bank France", "subsidiary_id": "SUB001", "year": "2025", "gross": Decimal("15000000"), "tax": Decimal("0"), "net": Decimal("15000000"), "status": "paid", "payment_date": date(2025, 4, 15)},
        {"id": "DIV002", "subsidiary": "Nova Asset Management", "subsidiary_id": "SUB002", "year": "2025", "gross": Decimal("3200000"), "tax": Decimal("0"), "net": Decimal("3200000"), "status": "approved", "payment_date": None},
        {"id": "DIV003", "subsidiary": "Nova Insurance", "subsidiary_id": "SUB003", "year": "2025", "gross": Decimal("1800000"), "tax": Decimal("270000"), "net": Decimal("1530000"), "status": "declared", "payment_date": None},
    ],
    "pool_rates": {"credit": Decimal("0.50"), "debit": Decimal("2.00")},
    # Revenus - Dette souveraine = 85% des revenus
    "revenue_breakdown": {
        "sovereign_bonds_coupons": Decimal("98500000"),  # 98.5M EUR - Coupons annuels
        "sovereign_bonds_trading": Decimal("15200000"),  # 15.2M EUR - Plus-values trading
        "subsidiaries_dividends": Decimal("2800000"),    # 2.8M EUR - Dividendes filiales
        "other": Decimal("1500000"),                     # 1.5M EUR - Autres
    },
    # Assurances Groupe
    "insurances": [
        # RC Dirigeants (D&O)
        {"id": "INS001", "type": "D&O", "name": "RC Dirigeants et Mandataires Sociaux", "insurer": "AXA Corporate", "policy_number": "DO-2024-NXG-001", "coverage": Decimal("50000000"), "premium": Decimal("185000"), "frequency": "annual", "start_date": date(2024, 1, 1), "end_date": date(2025, 12, 31), "status": "active"},
        # RC Pro Groupe
        {"id": "INS002", "type": "RC_PRO", "name": "RC Professionnelle Groupe", "insurer": "Allianz", "policy_number": "RCP-2024-NXG-002", "coverage": Decimal("100000000"), "premium": Decimal("320000"), "frequency": "annual", "start_date": date(2024, 1, 1), "end_date": date(2025, 12, 31), "status": "active"},
        # Cyber assurance
        {"id": "INS003", "type": "CYBER", "name": "Cyber Assurance Groupe", "insurer": "Chubb", "policy_number": "CYB-2024-NXG-003", "coverage": Decimal("25000000"), "premium": Decimal("95000"), "frequency": "annual", "start_date": date(2024, 3, 1), "end_date": date(2025, 2, 28), "status": "active"},
        # Assurance Immeubles
        {"id": "INS004", "type": "PROPERTY", "name": "Multirisque Siege Social", "insurer": "Generali", "policy_number": "MR-2024-NXG-004", "coverage": Decimal("15000000"), "premium": Decimal("42000"), "frequency": "annual", "start_date": date(2024, 1, 1), "end_date": date(2025, 12, 31), "status": "active"},
        # Key Man
        {"id": "INS005", "type": "KEY_MAN", "name": "Assurance Homme-Cle (PDG)", "insurer": "Swiss Life", "policy_number": "KM-2024-NXG-005", "coverage": Decimal("10000000"), "premium": Decimal("28000"), "frequency": "annual", "start_date": date(2024, 6, 1), "end_date": date(2025, 5, 31), "status": "active"},
        # CDS Ukraine (couverture risque souverain)
        {"id": "INS006", "type": "CDS", "name": "CDS Ukraine Sovereign 5Y", "insurer": "JP Morgan (contrepartie)", "policy_number": "CDS-UA-2024-001", "coverage": Decimal("150000000"), "premium": Decimal("4500000"), "frequency": "annual", "start_date": date(2024, 1, 15), "end_date": date(2029, 1, 15), "status": "active", "spread_bps": 3000},
    ],
    # Sinistres
    "claims": [
        {"id": "CLM001", "insurance_id": "INS003", "date": date(2024, 8, 15), "type": "Tentative intrusion", "amount_claimed": Decimal("150000"), "amount_paid": Decimal("125000"), "status": "paid"},
        {"id": "CLM002", "insurance_id": "INS004", "date": date(2024, 11, 20), "type": "Degat des eaux", "amount_claimed": Decimal("35000"), "amount_paid": Decimal("0"), "status": "pending"},
    ],
}


# =============================================================================
# DEMO SOVEREIGN BONDS PORTFOLIO - PORTEFEUILLE MASSIF (2.8 Milliards EUR)
# Dette de guerre / Obligations d'Etat - Activite principale
# =============================================================================

DEMO_SOVEREIGN_BONDS = [
    # ============ FRANCE - OAT (850M EUR) ============
    {"isin": "FR0014007L00", "name": "OAT 2.50% 25/05/2030 (Defense)", "country": "FR", "country_name": "France", "coupon": Decimal("2.50"), "maturity": date(2030, 5, 25), "nominal": Decimal("250000000"), "purchase_price": Decimal("99.50"), "current_price": Decimal("98.75"), "purchase_date": date(2023, 6, 15), "quantity": 2500},
    {"isin": "FR0013508470", "name": "OAT 1.50% 25/05/2031", "country": "FR", "country_name": "France", "coupon": Decimal("1.50"), "maturity": date(2031, 5, 25), "nominal": Decimal("200000000"), "purchase_price": Decimal("96.25"), "current_price": Decimal("95.80"), "purchase_date": date(2023, 9, 1), "quantity": 2000},
    {"isin": "FR0014003513", "name": "OAT 0.75% 25/11/2028", "country": "FR", "country_name": "France", "coupon": Decimal("0.75"), "maturity": date(2028, 11, 25), "nominal": Decimal("150000000"), "purchase_price": Decimal("97.00"), "current_price": Decimal("96.50"), "purchase_date": date(2024, 1, 10), "quantity": 1500},
    {"isin": "FR0013154028", "name": "OAT 1.25% 25/05/2036", "country": "FR", "country_name": "France", "coupon": Decimal("1.25"), "maturity": date(2036, 5, 25), "nominal": Decimal("250000000"), "purchase_price": Decimal("92.00"), "current_price": Decimal("91.25"), "purchase_date": date(2024, 3, 20), "quantity": 2500},

    # ============ ALLEMAGNE - Bund (600M EUR) ============
    {"isin": "DE0001102580", "name": "Bund 2.30% 15/02/2033", "country": "DE", "country_name": "Allemagne", "coupon": Decimal("2.30"), "maturity": date(2033, 2, 15), "nominal": Decimal("300000000"), "purchase_price": Decimal("102.00"), "current_price": Decimal("101.50"), "purchase_date": date(2023, 4, 1), "quantity": 3000},
    {"isin": "DE0001102614", "name": "Bund 1.70% 15/08/2032", "country": "DE", "country_name": "Allemagne", "coupon": Decimal("1.70"), "maturity": date(2032, 8, 15), "nominal": Decimal("200000000"), "purchase_price": Decimal("98.75"), "current_price": Decimal("98.25"), "purchase_date": date(2023, 7, 15), "quantity": 2000},
    {"isin": "DE0001141836", "name": "Bund 0.00% 15/08/2031", "country": "DE", "country_name": "Allemagne", "coupon": Decimal("0.00"), "maturity": date(2031, 8, 15), "nominal": Decimal("100000000"), "purchase_price": Decimal("88.50"), "current_price": Decimal("87.75"), "purchase_date": date(2024, 2, 1), "quantity": 1000},

    # ============ ITALIE - BTP (400M EUR) ============
    {"isin": "IT0005436693", "name": "BTP 3.85% 01/09/2049", "country": "IT", "country_name": "Italie", "coupon": Decimal("3.85"), "maturity": date(2049, 9, 1), "nominal": Decimal("200000000"), "purchase_price": Decimal("95.50"), "current_price": Decimal("94.25"), "purchase_date": date(2023, 5, 10), "quantity": 2000},
    {"isin": "IT0005494239", "name": "BTP 2.80% 01/06/2029", "country": "IT", "country_name": "Italie", "coupon": Decimal("2.80"), "maturity": date(2029, 6, 1), "nominal": Decimal("200000000"), "purchase_price": Decimal("99.00"), "current_price": Decimal("98.50"), "purchase_date": date(2024, 1, 5), "quantity": 2000},

    # ============ ESPAGNE - Bonos (300M EUR) ============
    {"isin": "ES0000012L29", "name": "Bonos 2.55% 31/10/2032", "country": "ES", "country_name": "Espagne", "coupon": Decimal("2.55"), "maturity": date(2032, 10, 31), "nominal": Decimal("150000000"), "purchase_price": Decimal("98.00"), "current_price": Decimal("97.50"), "purchase_date": date(2023, 8, 1), "quantity": 1500},
    {"isin": "ES00000128Q6", "name": "Bonos 1.85% 30/07/2035", "country": "ES", "country_name": "Espagne", "coupon": Decimal("1.85"), "maturity": date(2035, 7, 30), "nominal": Decimal("150000000"), "purchase_price": Decimal("94.25"), "current_price": Decimal("93.75"), "purchase_date": date(2024, 2, 15), "quantity": 1500},

    # ============ UKRAINE - War Bonds (250M EUR) ============
    {"isin": "XS2010028699", "name": "Ukraine 7.75% 01/09/2026 (War Bond)", "country": "UA", "country_name": "Ukraine", "coupon": Decimal("7.75"), "maturity": date(2026, 9, 1), "nominal": Decimal("100000000"), "purchase_price": Decimal("45.00"), "current_price": Decimal("52.50"), "purchase_date": date(2023, 3, 1), "quantity": 1000},
    {"isin": "XS2010028772", "name": "Ukraine 6.876% 21/05/2029 (War Bond)", "country": "UA", "country_name": "Ukraine", "coupon": Decimal("6.876"), "maturity": date(2029, 5, 21), "nominal": Decimal("150000000"), "purchase_price": Decimal("38.00"), "current_price": Decimal("48.25"), "purchase_date": date(2023, 6, 15), "quantity": 1500},

    # ============ POLOGNE (200M EUR) - Soutien OTAN ============
    {"isin": "PL0000112736", "name": "Poland 3.25% 25/07/2033", "country": "PL", "country_name": "Pologne", "coupon": Decimal("3.25"), "maturity": date(2033, 7, 25), "nominal": Decimal("200000000"), "purchase_price": Decimal("96.50"), "current_price": Decimal("95.75"), "purchase_date": date(2024, 1, 20), "quantity": 2000},

    # ============ USA - Treasury (300M EUR) ============
    {"isin": "US912810TM09", "name": "US Treasury 4.125% 15/08/2053", "country": "US", "country_name": "Etats-Unis", "coupon": Decimal("4.125"), "maturity": date(2053, 8, 15), "nominal": Decimal("200000000"), "purchase_price": Decimal("97.00"), "current_price": Decimal("96.25"), "purchase_date": date(2023, 10, 1), "quantity": 2000},
    {"isin": "US91282CJL54", "name": "US Treasury 4.50% 15/11/2033", "country": "US", "country_name": "Etats-Unis", "coupon": Decimal("4.50"), "maturity": date(2033, 11, 15), "nominal": Decimal("100000000"), "purchase_price": Decimal("101.50"), "current_price": Decimal("100.75"), "purchase_date": date(2024, 3, 1), "quantity": 1000},

    # ============ UK - Gilt (150M EUR) ============
    {"isin": "GB00BDRHNP05", "name": "UK Gilt 3.75% 22/10/2053", "country": "GB", "country_name": "Royaume-Uni", "coupon": Decimal("3.75"), "maturity": date(2053, 10, 22), "nominal": Decimal("150000000"), "purchase_price": Decimal("92.00"), "current_price": Decimal("91.25"), "purchase_date": date(2023, 11, 15), "quantity": 1500},
]


# =============================================================================
# DEMO AVAILABLE BONDS (for purchase) - Focus dette souveraine / guerre
# =============================================================================

DEMO_AVAILABLE_BONDS = [
    # Eurozone - Core
    {"isin": "FR0014006XJ5", "name": "OAT 1.25% 25/05/2034", "country": "FR", "country_name": "France", "coupon": Decimal("1.25"), "maturity": date(2034, 5, 25), "current_price": Decimal("94.50"), "yield": Decimal("1.85")},
    {"isin": "FR0014007TY1", "name": "OAT 3.00% 25/05/2033 (Defense)", "country": "FR", "country_name": "France", "coupon": Decimal("3.00"), "maturity": date(2033, 5, 25), "current_price": Decimal("102.75"), "yield": Decimal("2.65")},
    {"isin": "DE0001102648", "name": "Bund 2.60% 15/08/2033", "country": "DE", "country_name": "Allemagne", "coupon": Decimal("2.60"), "maturity": date(2033, 8, 15), "current_price": Decimal("103.50"), "yield": Decimal("2.25")},
    {"isin": "IT0005519787", "name": "BTP 4.00% 30/04/2035", "country": "IT", "country_name": "Italie", "coupon": Decimal("4.00"), "maturity": date(2035, 4, 30), "current_price": Decimal("100.25"), "yield": Decimal("3.95")},
    {"isin": "ES00001015F8", "name": "Bonos 3.15% 30/04/2033", "country": "ES", "country_name": "Espagne", "coupon": Decimal("3.15"), "maturity": date(2033, 4, 30), "current_price": Decimal("101.00"), "yield": Decimal("3.00")},

    # Europe de l'Est - Soutien OTAN / Ukraine
    {"isin": "XS2010029077", "name": "Ukraine 8.994% 01/02/2030 (War Bond)", "country": "UA", "country_name": "Ukraine", "coupon": Decimal("8.994"), "maturity": date(2030, 2, 1), "current_price": Decimal("42.50"), "yield": Decimal("28.50")},
    {"isin": "PL0000113783", "name": "Poland 5.75% 25/04/2032", "country": "PL", "country_name": "Pologne", "coupon": Decimal("5.75"), "maturity": date(2032, 4, 25), "current_price": Decimal("108.25"), "yield": Decimal("4.50")},
    {"isin": "ROVRZSDI2CZ7", "name": "Romania 4.625% 03/04/2049", "country": "RO", "country_name": "Roumanie", "coupon": Decimal("4.625"), "maturity": date(2049, 4, 3), "current_price": Decimal("78.50"), "yield": Decimal("6.25")},

    # USA & UK
    {"isin": "US91282CKR31", "name": "US Treasury 4.625% 15/05/2034", "country": "US", "country_name": "Etats-Unis", "coupon": Decimal("4.625"), "maturity": date(2034, 5, 15), "current_price": Decimal("102.50"), "yield": Decimal("4.35")},
    {"isin": "GB00BM8Z2V59", "name": "UK Gilt 4.25% 07/12/2040", "country": "GB", "country_name": "Royaume-Uni", "coupon": Decimal("4.25"), "maturity": date(2040, 12, 7), "current_price": Decimal("98.75"), "yield": Decimal("4.35")},

    # Autres
    {"isin": "JP1201551M12", "name": "JGB 0.50% 20/03/2033", "country": "JP", "country_name": "Japon", "coupon": Decimal("0.50"), "maturity": date(2033, 3, 20), "current_price": Decimal("98.00"), "yield": Decimal("0.72")},
    {"isin": "CH0224397130", "name": "Swiss Conf 1.50% 24/07/2042", "country": "CH", "country_name": "Suisse", "coupon": Decimal("1.50"), "maturity": date(2042, 7, 24), "current_price": Decimal("105.00"), "yield": Decimal("1.15")},
]


# =============================================================================
# HELPER FUNCTION TO GET DEMO HOLDING DATA
# =============================================================================

def get_demo_holding_data():
    """
    Get a copy of demo holding data.
    Returns a deep copy to avoid mutations.
    """
    import copy
    data = copy.deepcopy(DEMO_HOLDING)
    data["sovereign_bonds"] = copy.deepcopy(DEMO_SOVEREIGN_BONDS)
    data["available_bonds"] = copy.deepcopy(DEMO_AVAILABLE_BONDS)
    data["bond_transactions"] = []
    data["transactions"] = []
    return data


# =============================================================================
# HELPER FUNCTION TO CREATE DEMO BANK
# =============================================================================

def create_demo_bank():
    """
    Create a bank instance populated with demo data.

    Returns:
        Bank: A bank instance with demo customers, accounts, transactions, etc.
    """
    from ..core.bank import Bank

    bank = Bank()

    # Add customers
    for cust_data in DEMO_CUSTOMERS:
        customer = Customer(**cust_data)
        bank.customers[customer.customer_id] = customer

    # Add accounts
    for acc_data in DEMO_ACCOUNTS:
        account = Account(**acc_data)
        bank.accounts[account.iban] = account

    # Add transactions
    for tx_data in DEMO_TRANSACTIONS:
        tx = Transaction(**tx_data)
        bank.transactions[tx.transaction_id] = tx

    # Add cards
    for card_data in DEMO_CARDS:
        card = Card(**card_data)
        bank.cards[card.card_id] = card

    return bank
