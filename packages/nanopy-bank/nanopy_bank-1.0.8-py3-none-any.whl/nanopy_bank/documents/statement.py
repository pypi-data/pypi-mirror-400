"""
Bank Statement PDF Generator
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from io import BytesIO
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


class StatementGenerator:
    """
    Generate PDF bank statements
    """

    def __init__(
        self,
        bank_name: str = "NanoPy Bank",
        bank_address: str = "1 Rue de la Banque, 75001 Paris",
        bank_phone: str = "+33 1 23 45 67 89",
        bank_bic: str = "NANPFRPP"
    ):
        self.bank_name = bank_name
        self.bank_address = bank_address
        self.bank_phone = bank_phone
        self.bank_bic = bank_bic

        # Colors
        self.primary_color = colors.HexColor("#1a1a2e")
        self.accent_color = colors.HexColor("#00d4ff")
        self.text_color = colors.HexColor("#333333")
        self.light_gray = colors.HexColor("#f5f5f5")

    def generate(
        self,
        account_iban: str,
        account_name: str,
        customer_name: str,
        customer_address: str,
        transactions: List[dict],
        from_date: date,
        to_date: date,
        opening_balance: Decimal,
        closing_balance: Decimal,
        currency: str = "EUR"
    ) -> bytes:
        """
        Generate a PDF bank statement

        Returns: PDF content as bytes
        """
        buffer = BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )

        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='BankTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            spaceBefore=15,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='Normal2',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color
        ))
        styles.add(ParagraphStyle(
            name='Small',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.gray
        ))

        # Build content
        elements = []

        # Header
        elements.append(Paragraph(self.bank_name, styles['BankTitle']))
        elements.append(Paragraph(self.bank_address, styles['Small']))
        elements.append(Paragraph(f"Tel: {self.bank_phone} | BIC: {self.bank_bic}", styles['Small']))
        elements.append(Spacer(1, 15*mm))

        # Statement title
        elements.append(Paragraph("RELEVE DE COMPTE", styles['SectionTitle']))
        elements.append(Paragraph(
            f"Periode du {from_date.strftime('%d/%m/%Y')} au {to_date.strftime('%d/%m/%Y')}",
            styles['Normal2']
        ))
        elements.append(Spacer(1, 10*mm))

        # Account and customer info
        info_data = [
            ["Titulaire:", customer_name],
            ["Adresse:", customer_address],
            ["IBAN:", self._format_iban(account_iban)],
            ["Compte:", account_name],
        ]
        info_table = Table(info_data, colWidths=[40*mm, 120*mm])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 10*mm))

        # Balance summary
        elements.append(Paragraph("SYNTHESE", styles['SectionTitle']))

        # Calculate totals
        total_credit = sum(
            Decimal(str(tx.get("amount", 0)))
            for tx in transactions
            if tx.get("is_credit", False)
        )
        total_debit = sum(
            Decimal(str(tx.get("amount", 0)))
            for tx in transactions
            if not tx.get("is_credit", True)
        )

        balance_data = [
            ["Solde initial:", f"{opening_balance:,.2f} {currency}"],
            ["Total credits:", f"+{total_credit:,.2f} {currency}"],
            ["Total debits:", f"-{total_debit:,.2f} {currency}"],
            ["Solde final:", f"{closing_balance:,.2f} {currency}"],
        ]
        balance_table = Table(balance_data, colWidths=[60*mm, 60*mm])
        balance_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica', 10),
            ('FONT', (1, 0), (1, -1), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.text_color),
            ('TEXTCOLOR', (1, 1), (1, 1), colors.green),  # Credits in green
            ('TEXTCOLOR', (1, 2), (1, 2), colors.red),    # Debits in red
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, -1), (-1, -1), self.light_gray),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(balance_table)
        elements.append(Spacer(1, 10*mm))

        # Transactions
        elements.append(Paragraph("OPERATIONS", styles['SectionTitle']))

        if transactions:
            # Table header
            tx_data = [["Date", "Libelle", "Debit", "Credit", "Solde"]]

            # Running balance
            running_balance = opening_balance

            for tx in sorted(transactions, key=lambda x: x.get("created_at", "")):
                tx_date = tx.get("created_at", "")
                if isinstance(tx_date, str) and tx_date:
                    try:
                        tx_date = datetime.fromisoformat(tx_date.replace("Z", "")).strftime("%d/%m/%Y")
                    except:
                        tx_date = tx_date[:10]

                amount = Decimal(str(tx.get("amount", 0)))
                is_credit = tx.get("is_credit", False)

                if is_credit:
                    running_balance += amount
                    debit_str = ""
                    credit_str = f"+{amount:,.2f}"
                else:
                    running_balance -= amount
                    debit_str = f"-{amount:,.2f}"
                    credit_str = ""

                label = tx.get("label", tx.get("description", ""))[:40]

                tx_data.append([
                    tx_date,
                    label,
                    debit_str,
                    credit_str,
                    f"{running_balance:,.2f}"
                ])

            tx_table = Table(tx_data, colWidths=[25*mm, 70*mm, 30*mm, 30*mm, 30*mm])
            tx_table.setStyle(TableStyle([
                # Header
                ('BACKGROUND', (0, 0), (-1, 0), self.primary_color),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

                # Body
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.text_color),
                ('ALIGN', (2, 1), (4, -1), 'RIGHT'),

                # Debit column in red
                ('TEXTCOLOR', (2, 1), (2, -1), colors.red),
                # Credit column in green
                ('TEXTCOLOR', (3, 1), (3, -1), colors.green),

                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.light_gray]),

                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(tx_table)
        else:
            elements.append(Paragraph("Aucune operation sur cette periode.", styles['Normal2']))

        elements.append(Spacer(1, 15*mm))

        # Footer
        elements.append(Paragraph(
            f"Document genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            styles['Small']
        ))
        elements.append(Paragraph(
            f"{self.bank_name} - Ce document est un releve de compte informatif.",
            styles['Small']
        ))

        # Build PDF
        doc.build(elements)

        return buffer.getvalue()

    def _format_iban(self, iban: str) -> str:
        """Format IBAN with spaces"""
        iban = iban.replace(" ", "")
        return " ".join([iban[i:i+4] for i in range(0, len(iban), 4)])


def generate_statement_pdf(
    account,
    customer,
    transactions: List,
    from_date: date,
    to_date: date,
    opening_balance: Decimal
) -> bytes:
    """
    Helper function to generate statement PDF

    Args:
        account: Account object
        customer: Customer object
        transactions: List of Transaction objects
        from_date: Statement start date
        to_date: Statement end date
        opening_balance: Balance at start of period

    Returns:
        PDF content as bytes
    """
    generator = StatementGenerator()

    # Convert transactions to dicts
    tx_dicts = [tx.to_dict() if hasattr(tx, 'to_dict') else tx for tx in transactions]

    return generator.generate(
        account_iban=account.iban if hasattr(account, 'iban') else account.get('iban', ''),
        account_name=account.account_name if hasattr(account, 'account_name') else account.get('account_name', ''),
        customer_name=customer.full_name if hasattr(customer, 'full_name') else f"{customer.get('first_name', '')} {customer.get('last_name', '')}",
        customer_address=f"{customer.address if hasattr(customer, 'address') else customer.get('address', '')}, {customer.postal_code if hasattr(customer, 'postal_code') else customer.get('postal_code', '')} {customer.city if hasattr(customer, 'city') else customer.get('city', '')}",
        transactions=tx_dicts,
        from_date=from_date,
        to_date=to_date,
        opening_balance=opening_balance,
        closing_balance=account.balance if hasattr(account, 'balance') else Decimal(str(account.get('balance', 0))),
        currency=account.currency.value if hasattr(account, 'currency') else account.get('currency', 'EUR')
    )
