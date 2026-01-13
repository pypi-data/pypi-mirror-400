"""
SEPA XML Generator and Parser - ISO 20022 pain.001 (Credit Transfer) and pain.008 (Direct Debit)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from lxml import etree
import uuid

from ..core.models import Transaction, TransactionType


class SEPAGenerator:
    """
    Generate SEPA XML files (ISO 20022)

    Supported formats:
    - pain.001.001.03: Credit Transfer Initiation (SCT)
    - pain.008.001.02: Direct Debit Initiation (SDD)
    - camt.053.001.02: Bank to Customer Statement
    """

    # Namespaces
    NS_PAIN001 = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
    NS_PAIN008 = "urn:iso:std:iso:20022:tech:xsd:pain.008.001.02"
    NS_CAMT053 = "urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"

    def __init__(
        self,
        initiator_name: str = "NanoPy Bank",
        initiator_iban: str = "",
        initiator_bic: str = "NANPFRPP"
    ):
        self.initiator_name = initiator_name
        self.initiator_iban = initiator_iban
        self.initiator_bic = initiator_bic

    def generate_credit_transfer(
        self,
        transactions: List[dict],
        execution_date: Optional[datetime] = None
    ) -> str:
        """
        Generate SEPA Credit Transfer XML (pain.001.001.03)

        Each transaction dict should contain:
        - amount: Decimal
        - currency: str (default EUR)
        - creditor_name: str
        - creditor_iban: str
        - creditor_bic: str (optional)
        - remittance_info: str (label/description)
        - end_to_end_id: str (optional)
        """
        if not execution_date:
            execution_date = datetime.now()

        # Create root element
        nsmap = {None: self.NS_PAIN001}
        root = etree.Element("Document", nsmap=nsmap)
        cstmr_cdt_trf_initn = etree.SubElement(root, "CstmrCdtTrfInitn")

        # Group Header
        grp_hdr = etree.SubElement(cstmr_cdt_trf_initn, "GrpHdr")
        msg_id = f"NANOPY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        etree.SubElement(grp_hdr, "MsgId").text = msg_id
        etree.SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()
        etree.SubElement(grp_hdr, "NbOfTxs").text = str(len(transactions))

        # Calculate total
        total = sum(Decimal(str(tx.get("amount", 0))) for tx in transactions)
        etree.SubElement(grp_hdr, "CtrlSum").text = f"{total:.2f}"

        # Initiating Party
        initg_pty = etree.SubElement(grp_hdr, "InitgPty")
        etree.SubElement(initg_pty, "Nm").text = self.initiator_name

        # Payment Information
        pmt_inf = etree.SubElement(cstmr_cdt_trf_initn, "PmtInf")
        etree.SubElement(pmt_inf, "PmtInfId").text = f"PMT-{msg_id}"
        etree.SubElement(pmt_inf, "PmtMtd").text = "TRF"  # Transfer
        etree.SubElement(pmt_inf, "NbOfTxs").text = str(len(transactions))
        etree.SubElement(pmt_inf, "CtrlSum").text = f"{total:.2f}"

        # Payment Type Information
        pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
        etree.SubElement(svc_lvl, "Cd").text = "SEPA"

        # Requested Execution Date
        etree.SubElement(pmt_inf, "ReqdExctnDt").text = execution_date.strftime("%Y-%m-%d")

        # Debtor (payer)
        dbtr = etree.SubElement(pmt_inf, "Dbtr")
        etree.SubElement(dbtr, "Nm").text = self.initiator_name

        dbtr_acct = etree.SubElement(pmt_inf, "DbtrAcct")
        dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
        etree.SubElement(dbtr_acct_id, "IBAN").text = self.initiator_iban.replace(" ", "")

        dbtr_agt = etree.SubElement(pmt_inf, "DbtrAgt")
        dbtr_agt_fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
        etree.SubElement(dbtr_agt_fin_instn_id, "BIC").text = self.initiator_bic

        # Credit Transfer Transaction Information (for each transaction)
        for tx in transactions:
            cdt_trf_tx_inf = etree.SubElement(pmt_inf, "CdtTrfTxInf")

            # Payment ID
            pmt_id = etree.SubElement(cdt_trf_tx_inf, "PmtId")
            end_to_end_id = tx.get("end_to_end_id", f"E2E-{uuid.uuid4().hex[:12].upper()}")
            etree.SubElement(pmt_id, "EndToEndId").text = end_to_end_id

            # Amount
            amt = etree.SubElement(cdt_trf_tx_inf, "Amt")
            instd_amt = etree.SubElement(amt, "InstdAmt", Ccy=tx.get("currency", "EUR"))
            instd_amt.text = f"{Decimal(str(tx['amount'])):.2f}"

            # Creditor Agent (beneficiary bank)
            if tx.get("creditor_bic"):
                cdtr_agt = etree.SubElement(cdt_trf_tx_inf, "CdtrAgt")
                cdtr_agt_fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
                etree.SubElement(cdtr_agt_fin_instn_id, "BIC").text = tx["creditor_bic"]

            # Creditor (beneficiary)
            cdtr = etree.SubElement(cdt_trf_tx_inf, "Cdtr")
            etree.SubElement(cdtr, "Nm").text = tx["creditor_name"]

            cdtr_acct = etree.SubElement(cdt_trf_tx_inf, "CdtrAcct")
            cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
            etree.SubElement(cdtr_acct_id, "IBAN").text = tx["creditor_iban"].replace(" ", "")

            # Remittance Information
            rmt_inf = etree.SubElement(cdt_trf_tx_inf, "RmtInf")
            etree.SubElement(rmt_inf, "Ustrd").text = tx.get("remittance_info", "")[:140]

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

    def generate_direct_debit(
        self,
        transactions: List[dict],
        collection_date: Optional[datetime] = None,
        sequence_type: str = "OOFF"  # OOFF=One-off, FRST=First, RCUR=Recurring, FNAL=Final
    ) -> str:
        """
        Generate SEPA Direct Debit XML (pain.008.001.02)

        Each transaction dict should contain:
        - amount: Decimal
        - debtor_name: str
        - debtor_iban: str
        - debtor_bic: str (optional)
        - mandate_id: str
        - mandate_date: str (YYYY-MM-DD)
        - remittance_info: str
        - end_to_end_id: str (optional)
        """
        if not collection_date:
            collection_date = datetime.now()

        nsmap = {None: self.NS_PAIN008}
        root = etree.Element("Document", nsmap=nsmap)
        cstmr_drct_dbt_initn = etree.SubElement(root, "CstmrDrctDbtInitn")

        # Group Header
        grp_hdr = etree.SubElement(cstmr_drct_dbt_initn, "GrpHdr")
        msg_id = f"NANOPY-DD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        etree.SubElement(grp_hdr, "MsgId").text = msg_id
        etree.SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()
        etree.SubElement(grp_hdr, "NbOfTxs").text = str(len(transactions))

        total = sum(Decimal(str(tx.get("amount", 0))) for tx in transactions)
        etree.SubElement(grp_hdr, "CtrlSum").text = f"{total:.2f}"

        initg_pty = etree.SubElement(grp_hdr, "InitgPty")
        etree.SubElement(initg_pty, "Nm").text = self.initiator_name

        # Payment Information
        pmt_inf = etree.SubElement(cstmr_drct_dbt_initn, "PmtInf")
        etree.SubElement(pmt_inf, "PmtInfId").text = f"PMT-{msg_id}"
        etree.SubElement(pmt_inf, "PmtMtd").text = "DD"  # Direct Debit
        etree.SubElement(pmt_inf, "NbOfTxs").text = str(len(transactions))
        etree.SubElement(pmt_inf, "CtrlSum").text = f"{total:.2f}"

        # Payment Type Information
        pmt_tp_inf = etree.SubElement(pmt_inf, "PmtTpInf")
        svc_lvl = etree.SubElement(pmt_tp_inf, "SvcLvl")
        etree.SubElement(svc_lvl, "Cd").text = "SEPA"
        lcl_instrm = etree.SubElement(pmt_tp_inf, "LclInstrm")
        etree.SubElement(lcl_instrm, "Cd").text = "CORE"  # CORE or B2B
        etree.SubElement(pmt_tp_inf, "SeqTp").text = sequence_type

        # Requested Collection Date
        etree.SubElement(pmt_inf, "ReqdColltnDt").text = collection_date.strftime("%Y-%m-%d")

        # Creditor (collector)
        cdtr = etree.SubElement(pmt_inf, "Cdtr")
        etree.SubElement(cdtr, "Nm").text = self.initiator_name

        cdtr_acct = etree.SubElement(pmt_inf, "CdtrAcct")
        cdtr_acct_id = etree.SubElement(cdtr_acct, "Id")
        etree.SubElement(cdtr_acct_id, "IBAN").text = self.initiator_iban.replace(" ", "")

        cdtr_agt = etree.SubElement(pmt_inf, "CdtrAgt")
        cdtr_agt_fin_instn_id = etree.SubElement(cdtr_agt, "FinInstnId")
        etree.SubElement(cdtr_agt_fin_instn_id, "BIC").text = self.initiator_bic

        # Creditor Scheme Identification (SEPA Creditor ID)
        cdtr_schme_id = etree.SubElement(pmt_inf, "CdtrSchmeId")
        cdtr_schme_id_id = etree.SubElement(cdtr_schme_id, "Id")
        prvt_id = etree.SubElement(cdtr_schme_id_id, "PrvtId")
        othr = etree.SubElement(prvt_id, "Othr")
        etree.SubElement(othr, "Id").text = f"FR{uuid.uuid4().hex[:18].upper()}"  # Creditor ID
        schme_nm = etree.SubElement(othr, "SchmeNm")
        etree.SubElement(schme_nm, "Prtry").text = "SEPA"

        # Direct Debit Transaction Information
        for tx in transactions:
            drct_dbt_tx_inf = etree.SubElement(pmt_inf, "DrctDbtTxInf")

            # Payment ID
            pmt_id = etree.SubElement(drct_dbt_tx_inf, "PmtId")
            end_to_end_id = tx.get("end_to_end_id", f"E2E-{uuid.uuid4().hex[:12].upper()}")
            etree.SubElement(pmt_id, "EndToEndId").text = end_to_end_id

            # Amount
            instd_amt = etree.SubElement(drct_dbt_tx_inf, "InstdAmt", Ccy="EUR")
            instd_amt.text = f"{Decimal(str(tx['amount'])):.2f}"

            # Mandate Related Information
            drct_dbt_tx = etree.SubElement(drct_dbt_tx_inf, "DrctDbtTx")
            mndt_rltd_inf = etree.SubElement(drct_dbt_tx, "MndtRltdInf")
            etree.SubElement(mndt_rltd_inf, "MndtId").text = tx["mandate_id"]
            etree.SubElement(mndt_rltd_inf, "DtOfSgntr").text = tx.get("mandate_date", datetime.now().strftime("%Y-%m-%d"))

            # Debtor Agent
            if tx.get("debtor_bic"):
                dbtr_agt = etree.SubElement(drct_dbt_tx_inf, "DbtrAgt")
                dbtr_agt_fin_instn_id = etree.SubElement(dbtr_agt, "FinInstnId")
                etree.SubElement(dbtr_agt_fin_instn_id, "BIC").text = tx["debtor_bic"]

            # Debtor
            dbtr = etree.SubElement(drct_dbt_tx_inf, "Dbtr")
            etree.SubElement(dbtr, "Nm").text = tx["debtor_name"]

            dbtr_acct = etree.SubElement(drct_dbt_tx_inf, "DbtrAcct")
            dbtr_acct_id = etree.SubElement(dbtr_acct, "Id")
            etree.SubElement(dbtr_acct_id, "IBAN").text = tx["debtor_iban"].replace(" ", "")

            # Remittance Information
            rmt_inf = etree.SubElement(drct_dbt_tx_inf, "RmtInf")
            etree.SubElement(rmt_inf, "Ustrd").text = tx.get("remittance_info", "")[:140]

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()

    def generate_statement(
        self,
        iban: str,
        transactions: List[Transaction],
        opening_balance: Decimal,
        closing_balance: Decimal,
        from_date: datetime,
        to_date: datetime
    ) -> str:
        """
        Generate Bank Statement XML (camt.053.001.02)
        """
        nsmap = {None: self.NS_CAMT053}
        root = etree.Element("Document", nsmap=nsmap)
        bk_to_cstmr_stmt = etree.SubElement(root, "BkToCstmrStmt")

        # Group Header
        grp_hdr = etree.SubElement(bk_to_cstmr_stmt, "GrpHdr")
        msg_id = f"STMT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        etree.SubElement(grp_hdr, "MsgId").text = msg_id
        etree.SubElement(grp_hdr, "CreDtTm").text = datetime.now().isoformat()

        # Statement
        stmt = etree.SubElement(bk_to_cstmr_stmt, "Stmt")
        etree.SubElement(stmt, "Id").text = msg_id
        etree.SubElement(stmt, "CreDtTm").text = datetime.now().isoformat()

        # Account
        acct = etree.SubElement(stmt, "Acct")
        acct_id = etree.SubElement(acct, "Id")
        etree.SubElement(acct_id, "IBAN").text = iban.replace(" ", "")

        # Balance - Opening
        bal_opng = etree.SubElement(stmt, "Bal")
        tp_opng = etree.SubElement(bal_opng, "Tp")
        cd_or_prtry_opng = etree.SubElement(tp_opng, "CdOrPrtry")
        etree.SubElement(cd_or_prtry_opng, "Cd").text = "OPBD"  # Opening Booked
        amt_opng = etree.SubElement(bal_opng, "Amt", Ccy="EUR")
        amt_opng.text = f"{opening_balance:.2f}"
        etree.SubElement(bal_opng, "CdtDbtInd").text = "CRDT" if opening_balance >= 0 else "DBIT"
        etree.SubElement(bal_opng, "Dt").text = from_date.strftime("%Y-%m-%d")

        # Balance - Closing
        bal_clsg = etree.SubElement(stmt, "Bal")
        tp_clsg = etree.SubElement(bal_clsg, "Tp")
        cd_or_prtry_clsg = etree.SubElement(tp_clsg, "CdOrPrtry")
        etree.SubElement(cd_or_prtry_clsg, "Cd").text = "CLBD"  # Closing Booked
        amt_clsg = etree.SubElement(bal_clsg, "Amt", Ccy="EUR")
        amt_clsg.text = f"{closing_balance:.2f}"
        etree.SubElement(bal_clsg, "CdtDbtInd").text = "CRDT" if closing_balance >= 0 else "DBIT"
        etree.SubElement(bal_clsg, "Dt").text = to_date.strftime("%Y-%m-%d")

        # Entries (transactions)
        for tx in transactions:
            ntry = etree.SubElement(stmt, "Ntry")
            amt_ntry = etree.SubElement(ntry, "Amt", Ccy=tx.currency.value)
            amt_ntry.text = f"{tx.amount:.2f}"
            etree.SubElement(ntry, "CdtDbtInd").text = "CRDT" if tx.is_credit else "DBIT"
            etree.SubElement(ntry, "Sts").text = "BOOK"
            etree.SubElement(ntry, "BookgDt").text = tx.created_at.strftime("%Y-%m-%d")
            etree.SubElement(ntry, "ValDt").text = tx.value_date.strftime("%Y-%m-%d") if tx.value_date else tx.created_at.strftime("%Y-%m-%d")

            # Entry Details
            ntry_dtls = etree.SubElement(ntry, "NtryDtls")
            tx_dtls = etree.SubElement(ntry_dtls, "TxDtls")

            refs = etree.SubElement(tx_dtls, "Refs")
            etree.SubElement(refs, "EndToEndId").text = tx.end_to_end_id or tx.reference

            # Related Parties
            if tx.counterparty_name:
                rltd_pties = etree.SubElement(tx_dtls, "RltdPties")
                if tx.is_credit:
                    dbtr = etree.SubElement(rltd_pties, "Dbtr")
                    etree.SubElement(dbtr, "Nm").text = tx.counterparty_name
                else:
                    cdtr = etree.SubElement(rltd_pties, "Cdtr")
                    etree.SubElement(cdtr, "Nm").text = tx.counterparty_name

            # Remittance Information
            rmt_inf = etree.SubElement(tx_dtls, "RmtInf")
            etree.SubElement(rmt_inf, "Ustrd").text = tx.label[:140]

        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8").decode()


class SEPAParser:
    """
    Parse SEPA XML files
    """

    @staticmethod
    def parse_credit_transfer(xml_content: str) -> List[dict]:
        """Parse pain.001 Credit Transfer file"""
        root = etree.fromstring(xml_content.encode())

        # Remove namespace for easier parsing
        for elem in root.iter():
            if elem.tag.startswith('{'):
                elem.tag = elem.tag.split('}')[1]

        transactions = []
        for cdt_trf_tx_inf in root.findall(".//CdtTrfTxInf"):
            tx = {}

            # Amount
            instd_amt = cdt_trf_tx_inf.find(".//InstdAmt")
            if instd_amt is not None:
                tx["amount"] = Decimal(instd_amt.text)
                tx["currency"] = instd_amt.get("Ccy", "EUR")

            # End to End ID
            end_to_end = cdt_trf_tx_inf.find(".//EndToEndId")
            if end_to_end is not None:
                tx["end_to_end_id"] = end_to_end.text

            # Creditor Name
            cdtr_nm = cdt_trf_tx_inf.find(".//Cdtr/Nm")
            if cdtr_nm is not None:
                tx["creditor_name"] = cdtr_nm.text

            # Creditor IBAN
            cdtr_iban = cdt_trf_tx_inf.find(".//CdtrAcct/Id/IBAN")
            if cdtr_iban is not None:
                tx["creditor_iban"] = cdtr_iban.text

            # Creditor BIC
            cdtr_bic = cdt_trf_tx_inf.find(".//CdtrAgt/FinInstnId/BIC")
            if cdtr_bic is not None:
                tx["creditor_bic"] = cdtr_bic.text

            # Remittance Info
            ustrd = cdt_trf_tx_inf.find(".//RmtInf/Ustrd")
            if ustrd is not None:
                tx["remittance_info"] = ustrd.text

            transactions.append(tx)

        return transactions

    @staticmethod
    def parse_statement(xml_content: str) -> dict:
        """Parse camt.053 Bank Statement file"""
        root = etree.fromstring(xml_content.encode())

        # Remove namespace
        for elem in root.iter():
            if elem.tag.startswith('{'):
                elem.tag = elem.tag.split('}')[1]

        result = {
            "iban": "",
            "opening_balance": Decimal("0"),
            "closing_balance": Decimal("0"),
            "transactions": []
        }

        # IBAN
        iban = root.find(".//Acct/Id/IBAN")
        if iban is not None:
            result["iban"] = iban.text

        # Balances
        for bal in root.findall(".//Bal"):
            cd = bal.find(".//Cd")
            amt = bal.find(".//Amt")
            if cd is not None and amt is not None:
                value = Decimal(amt.text)
                if cd.text == "OPBD":
                    result["opening_balance"] = value
                elif cd.text == "CLBD":
                    result["closing_balance"] = value

        # Transactions
        for ntry in root.findall(".//Ntry"):
            tx = {}
            amt = ntry.find("Amt")
            if amt is not None:
                tx["amount"] = Decimal(amt.text)
                tx["currency"] = amt.get("Ccy", "EUR")

            cdt_dbt = ntry.find("CdtDbtInd")
            if cdt_dbt is not None:
                tx["is_credit"] = cdt_dbt.text == "CRDT"

            bookg_dt = ntry.find("BookgDt")
            if bookg_dt is not None:
                tx["booking_date"] = bookg_dt.text

            ustrd = ntry.find(".//Ustrd")
            if ustrd is not None:
                tx["label"] = ustrd.text

            result["transactions"].append(tx)

        return result
