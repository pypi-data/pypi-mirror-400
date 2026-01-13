"""Importer for Lån & Spar Bank (LSB) CSV files."""

from os import path
from beancount.core import data
from beangulp.importers import csvbase


class LSBImporter(csvbase.Importer):
    """Importer for LSB (Lån & Spar Bank) CSV exports.

    CSV Format:
    - No header row
    - UTF-8 with BOM encoding
    - Semicolon (;) separated
    - Danish number format (. for thousands, , for decimals)

    Fields (by index):
    0: Text from sender (often blank)
    1: Posteringstekst (transaction description)
    2: From Account (XXXX YYYYYYYYYY format)
    3: Destination Account (XXXX YYYYYYYYYY format)
    4: Amount (Danish format)
    5: Approved by
    6: Unknown field
    7: Created Date
    8: Posting Date
    9: Interest Date
    10: Dispositionsdato
    11: Bank reference (numerical)
    12: External reference (numerical)
    13-15: Unknown fields
    16: Receiver
    """

    # CSV file settings
    encoding = "utf-8-sig"  # UTF-8 with BOM
    names = False  # No header row
    header = 0  # No header lines to skip
    footer = 0  # No footer lines to skip

    class LSBDialect(csvbase.csv.Dialect):
        """CSV dialect for LSB files."""

        delimiter = ";"
        quotechar = '"'
        doublequote = True
        skipinitialspace = False
        lineterminator = "\r\n"
        quoting = csvbase.csv.QUOTE_MINIMAL

    dialect = LSBDialect

    # Column definitions (using indices since there's no header)
    text_from_sender = csvbase.Column(0, default="")
    posteringstekst = csvbase.Column(1)  # Transaction description
    from_account = csvbase.Column(2, default="")
    to_account = csvbase.Column(3, default="")
    amount = csvbase.Amount(4, subs={r"\.": "", r",": "."})  # Danish format conversion
    approved_by = csvbase.Column(5, default="")
    created_date = csvbase.Date(7, "%d-%m-%Y")
    date = csvbase.Date(8, "%d-%m-%Y")  # Posting Date
    interest_date = csvbase.Date(9, "%d-%m-%Y")
    dispositionsdato = csvbase.Date(10, "%d-%m-%Y")
    bank_reference = csvbase.Column(11, default="")
    external_reference = csvbase.Column(12, default="")
    receiver = csvbase.Column(15, default="")  # Last field in 16-field CSV

    # Narration uses columns 0 and 1 combined
    narration = csvbase.Columns(0, 1, sep=" | ")

    def __init__(
        self, account, account_number, currency="DKK", flag="*", account_map=None
    ):
        """Initialize the LSB importer.

        Args:
            account: The main account to use for transactions (e.g., "Assets:LSB:Checking")
            account_number: The LSB account number to match (e.g., "0400 4024493887")
            currency: The currency to use (default: DKK)
            flag: The default flag for transactions (default: *)
            account_map: Optional dict mapping LSB account numbers to Beancount accounts
                        for handling internal transfers (e.g., {"0400 4024493887": "Assets:LSB:Checking"})
        """
        super().__init__(account, currency, flag)
        self.account_number = account_number
        self.account_map = account_map or {}

    def identify(self, filepath):
        """Identify if a file is an LSB CSV export for this account.

        Determines the file's account by checking the sign of amounts:
        - Negative amounts: from_account is the file's account
        - Positive amounts: to_account is the file's account

        Args:
            filepath: Path to the file to identify

        Returns:
            True if the file is an LSB CSV export for this specific account
        """
        import csv
        import decimal

        # Check if filename matches expected pattern
        filename = path.basename(filepath).lower()
        if "posteringsdetaljer" not in filename or not filename.endswith(".csv"):
            return False

        # Determine the file's account by checking the first transaction
        try:
            with open(filepath, encoding="utf-8-sig") as fd:
                reader = csv.reader(fd, delimiter=";")

                for row in reader:
                    if len(row) < 5:  # Need columns 2, 3, and 4
                        continue

                    from_account = row[2].strip()
                    to_account = row[3].strip()
                    amount_str = row[4].strip()

                    if not amount_str:
                        continue

                    # Parse amount (Danish format: . for thousands, , for decimal)
                    amount_str = amount_str.replace(".", "").replace(",", ".")
                    try:
                        amount = decimal.Decimal(amount_str)
                    except decimal.InvalidOperation:
                        continue

                    # Check if this account matches based on amount sign
                    if amount < 0 and from_account == self.account_number:
                        return True
                    elif amount > 0 and to_account == self.account_number:
                        return True
                    # Continue checking other rows if not a match

        except (UnicodeDecodeError, IOError, csv.Error):
            return False

        return False

    def filename(self, filepath):
        """Generate a standardized filename for the imported file.

        Args:
            filepath: Original file path

        Returns:
            Standardized filename
        """
        return "lsb." + path.basename(filepath)

    def finalize(self, txn, row):
        """Post-process the transaction to handle LSB-specific logic.

        This method determines the payee and handles internal transfers.
        For internal transfers between known accounts, adds a second posting.

        Args:
            txn: The transaction object
            row: The CSV row data

        Returns:
            Modified transaction or None to skip
        """
        if txn is None:
            return None

        # Determine payee and handle internal transfers
        payee = None
        postings = list(txn.postings)

        if row.from_account and row.to_account:
            # Determine which account is the other side of the transfer
            other_account_number = None
            if row.from_account == self.account_number:
                other_account_number = row.to_account
            elif row.to_account == self.account_number:
                other_account_number = row.from_account

            # Check if it's an internal transfer (other account is in our account map)
            if other_account_number and other_account_number in self.account_map:
                # Internal transfer between known accounts
                # Only import the "sending" side (negative amount) to avoid duplicates
                if row.to_account == self.account_number:
                    # This is the receiving side (positive amount), skip it
                    return None

                other_account = self.account_map[other_account_number]
                # Add the balancing posting (amount will be automatically negated by Beancount)
                postings.append(
                    data.Posting(other_account, None, None, None, None, None)
                )

        # Reconstruct transaction with updated payee and postings
        txn = txn._replace(payee=payee, postings=postings)

        return txn
