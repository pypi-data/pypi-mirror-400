"""
NanoPy Bank CLI
"""

import click
import sys
import os


@click.group()
@click.version_option(version="1.0.0")
def main():
    """NanoPy Bank - Online Banking System"""
    pass


@main.command()
@click.option("--port", "-p", default=8501, help="Port to run on")
@click.option("--host", "-h", default="localhost", help="Host to bind to")
def serve(port: int, host: str):
    """Start the banking UI (Streamlit)"""
    import subprocess

    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    click.echo(f"Starting NanoPy Bank on http://{host}:{port}")

    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.address", host,
        "--theme.base", "dark"
    ])


@main.command()
@click.option("--iban", "-i", required=True, help="Account IBAN")
@click.option("--output", "-o", default="statement.xml", help="Output file")
def export_statement(iban: str, output: str):
    """Export bank statement as SEPA XML (camt.053)"""
    from .core import get_bank
    from .sepa import SEPAGenerator
    from datetime import datetime, timedelta

    bank = get_bank()
    account = bank.get_account(iban)

    if not account:
        click.echo(f"Account {iban} not found", err=True)
        return

    transactions = bank.get_account_transactions(iban, limit=100)

    generator = SEPAGenerator(
        initiator_name="NanoPy Bank",
        initiator_iban=iban,
        initiator_bic=account.bic
    )

    xml_content = generator.generate_statement(
        iban=iban,
        transactions=transactions,
        opening_balance=account.balance,
        closing_balance=account.balance,
        from_date=datetime.now() - timedelta(days=30),
        to_date=datetime.now()
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write(xml_content)

    click.echo(f"Statement exported to {output}")


@main.command()
@click.option("--iban", "-i", required=True, help="Source Account IBAN")
def export_sepa(iban: str):
    """Export SEPA Credit Transfer XML (pain.001)"""
    click.echo("Use the web UI for SEPA exports: nanopy-bank serve")


@main.command()
def stats():
    """Show bank statistics"""
    from .core import get_bank

    bank = get_bank()
    stats = bank.get_stats()

    click.echo("\n=== NanoPy Bank Statistics ===\n")
    click.echo(f"Customers:    {stats['total_customers']}")
    click.echo(f"Accounts:     {stats['total_accounts']}")
    click.echo(f"Transactions: {stats['total_transactions']}")
    click.echo(f"Total Balance: {stats['total_balance']} EUR")
    click.echo(f"Today's Txs:  {stats['transactions_today']}")
    click.echo()


@main.command()
def demo():
    """Create demo data"""
    from decimal import Decimal
    from .core import get_bank, AccountType, TransactionType

    bank = get_bank()

    click.echo("Creating demo customer and account...")

    # Create customer
    customer = bank.create_customer(
        first_name="Marie",
        last_name="Dupont",
        email="marie.dupont@email.com",
        phone="+33612345678",
        address="45 Avenue des Champs-Élysées",
        city="Paris",
        postal_code="75008",
        country="FR"
    )

    # Create checking account
    account = bank.create_account(
        customer_id=customer.customer_id,
        account_type=AccountType.CHECKING,
        initial_balance=Decimal("2500.00"),
        account_name="Compte Courant"
    )

    # Create savings account
    savings = bank.create_account(
        customer_id=customer.customer_id,
        account_type=AccountType.SAVINGS,
        initial_balance=Decimal("15000.00"),
        account_name="Livret A"
    )

    # Add demo transactions
    bank.credit(account.iban, Decimal("3200.00"), "Salaire Décembre", "ACME SARL", "", TransactionType.SEPA_CREDIT)
    bank.debit(account.iban, Decimal("850.00"), "Loyer Janvier", "IMMO PARIS", "", TransactionType.SEPA_DEBIT)
    bank.debit(account.iban, Decimal("127.50"), "EDF Electricité", "EDF", "", TransactionType.SEPA_DEBIT)
    bank.debit(account.iban, Decimal("45.90"), "Carrefour Market", "CARREFOUR", "", TransactionType.CARD_PAYMENT)
    bank.debit(account.iban, Decimal("12.99"), "Spotify Premium", "SPOTIFY", "", TransactionType.CARD_PAYMENT)
    bank.debit(account.iban, Decimal("60.00"), "Retrait DAB", "", "", TransactionType.ATM_WITHDRAWAL)

    click.echo(f"\nDemo created!")
    click.echo(f"Customer: {customer.full_name} ({customer.customer_id})")
    click.echo(f"Checking: {account.format_iban()}")
    click.echo(f"Savings:  {savings.format_iban()}")
    click.echo(f"\nRun 'nanopy-bank serve' to access the UI")


if __name__ == "__main__":
    main()
