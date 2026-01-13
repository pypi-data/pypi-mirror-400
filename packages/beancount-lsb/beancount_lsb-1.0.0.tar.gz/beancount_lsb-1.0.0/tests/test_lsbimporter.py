"""Tests for the LSBImporter class."""

import csv
import datetime
import decimal
import tempfile
from pathlib import Path

import pytest
from beancount.core import data
from beancount.core.amount import Amount

from beancount_lsb.lsbimporter import LSBImporter


@pytest.fixture
def sample_csv_data():
    """Sample LSB CSV data with various transaction types."""
    return [
        # Internal transfer (negative amount - sending side)
        [
            "",
            "Til Forbrugskonto",
            "1234 5678901234",
            "1234 9876543210",
            "-1.250,50",
            "Test User",
            "",
            "02-01-2026",
            "02-01-2026",
            "02-01-2026",
            "02-01-2026",
            "1000000001",
            "",
            "",
            "",
            "",
        ],
        # Interest payment (positive amount)
        [
            "",
            "Rente af indestående",
            "",
            "1234 5678901234",
            "12,50",
            "",
            "",
            "30-12-2025",
            "31-12-2025",
            "01-01-2026",
            "31-12-2025",
            "1000000002",
            "",
            "",
            "",
            "",
        ],
        # Salary (positive amount)
        [
            "",
            "LØNOVERFØRSEL",
            "",
            "1234 5678901234",
            "25.000,00",
            "",
            "",
            "29-12-2025",
            "30-12-2025",
            "30-12-2025",
            "30-12-2025",
            "1000000003",
            "",
            "",
            "",
            "",
        ],
        # External payment (positive amount)
        [
            "",
            "External Payment",
            "",
            "1234 5678901234",
            "100,00",
            "",
            "",
            "27-12-2025",
            "29-12-2025",
            "29-12-2025",
            "29-12-2025",
            "1000000004",
            "2000000001",
            "",
            "",
            "Test Receiver",
        ],
    ]


@pytest.fixture
def temp_csv_file(sample_csv_data):
    """Create a temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8-sig",
        suffix="_Posteringsdetaljer.csv",
        delete=False,
        newline="",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        for row in sample_csv_data:
            writer.writerow(row)
        filepath = f.name

    yield filepath

    # Cleanup
    Path(filepath).unlink(missing_ok=True)


@pytest.fixture
def importer():
    """Create a basic LSBImporter instance."""
    return LSBImporter(
        account="Assets:LSB:Savings",
        account_number="1234 5678901234",
        currency="DKK",
        flag="*",
    )


@pytest.fixture
def importer_with_account_map():
    """Create an LSBImporter with account mapping for internal transfers."""
    return LSBImporter(
        account="Assets:LSB:Savings",
        account_number="1234 5678901234",
        currency="DKK",
        flag="*",
        account_map={
            "1234 5678901234": "Assets:LSB:Savings",
            "1234 9876543210": "Assets:LSB:Checking",
        },
    )


class TestLSBImporterInit:
    """Tests for LSBImporter initialization."""

    def test_init_basic(self):
        """Test basic initialization."""
        importer = LSBImporter(
            account="Assets:LSB:Checking", account_number="1234 9876543210"
        )
        assert importer.importer_account == "Assets:LSB:Checking"
        assert importer.account_number == "1234 9876543210"
        assert importer.currency == "DKK"
        assert importer.flag == "*"
        assert importer.account_map == {}

    def test_init_with_custom_currency(self):
        """Test initialization with custom currency."""
        importer = LSBImporter(
            account="Assets:LSB:Checking",
            account_number="1234 9876543210",
            currency="EUR",
        )
        assert importer.currency == "EUR"

    def test_init_with_custom_flag(self):
        """Test initialization with custom flag."""
        importer = LSBImporter(
            account="Assets:LSB:Checking",
            account_number="1234 9876543210",
            flag="!",
        )
        assert importer.flag == "!"

    def test_init_with_account_map(self):
        """Test initialization with account map."""
        account_map = {
            "1234 5678901234": "Assets:LSB:Savings",
            "1234 9876543210": "Assets:LSB:Checking",
        }
        importer = LSBImporter(
            account="Assets:LSB:Savings",
            account_number="1234 5678901234",
            account_map=account_map,
        )
        assert importer.account_map == account_map


class TestLSBImporterIdentify:
    """Tests for file identification."""

    def test_identify_correct_file(self, importer, temp_csv_file):
        """Test that the importer correctly identifies LSB CSV files for its account."""
        assert importer.identify(temp_csv_file) is True

    def test_identify_wrong_account(self, temp_csv_file):
        """Test that the importer rejects files for different accounts."""
        importer = LSBImporter(
            account="Assets:LSB:Other", account_number="9999 9999999999"
        )
        assert importer.identify(temp_csv_file) is False

    def test_identify_wrong_filename(self, importer):
        """Test that the importer rejects files with wrong filename."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".csv", delete=False
        ) as f:
            f.write("some,data\n")
            filepath = f.name

        try:
            assert importer.identify(filepath) is False
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_identify_non_csv_file(self, importer):
        """Test that the importer rejects non-CSV files."""
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".txt", delete=False
        ) as f:
            f.write("some text\n")
            filepath = f.name

        try:
            assert importer.identify(filepath) is False
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_identify_empty_file(self, importer):
        """Test that the importer handles empty files gracefully."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
        ) as f:
            filepath = f.name

        try:
            assert importer.identify(filepath) is False
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_identify_malformed_csv(self, importer):
        """Test that the importer handles malformed CSV files gracefully."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # Write row with insufficient columns
            writer.writerow(["col1", "col2"])
            filepath = f.name

        try:
            assert importer.identify(filepath) is False
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestLSBImporterFilename:
    """Tests for filename generation."""

    def test_filename_generation(self, importer):
        """Test that the importer generates correct standardized filenames."""
        filepath = "/path/to/Posteringsdetaljer(3).csv"
        assert importer.filename(filepath) == "lsb.Posteringsdetaljer(3).csv"

    def test_filename_with_different_path(self, importer):
        """Test filename generation with different path."""
        filepath = "/tmp/Downloads/Posteringsdetaljer_2026.csv"
        assert importer.filename(filepath) == "lsb.Posteringsdetaljer_2026.csv"


class TestLSBImporterExtract:
    """Tests for transaction extraction."""

    def test_extract_basic_transactions(self, importer, temp_csv_file):
        """Test extracting transactions from a CSV file."""
        entries = list(importer.extract(temp_csv_file, []))

        # Should extract all transactions
        assert len(entries) > 0

        # Check that entries are Transaction objects
        for entry in entries:
            assert isinstance(entry, data.Transaction)

    def test_extract_transaction_fields(self, importer, temp_csv_file):
        """Test that extracted transactions have correct fields."""
        entries = list(importer.extract(temp_csv_file, []))

        # Entries are sorted by date. Check interest payment transaction (31-12-2025)
        interest_txn = next(
            (e for e in entries if "Rente af indestående" in e.narration), None
        )
        assert interest_txn is not None
        assert isinstance(interest_txn, data.Transaction)
        assert interest_txn.date == datetime.date(2025, 12, 31)
        assert interest_txn.flag == "*"
        assert "Rente af indestående" in interest_txn.narration
        assert len(interest_txn.postings) == 1
        assert interest_txn.postings[0].account == "Assets:LSB:Savings"

    def test_extract_amount_parsing(self, importer, temp_csv_file):
        """Test that amounts are correctly parsed from Danish format."""
        entries = list(importer.extract(temp_csv_file, []))

        # Find the salary transaction
        salary_txn = next((e for e in entries if "LØNOVERFØRSEL" in e.narration), None)
        assert salary_txn is not None

        # Check amount parsing (25.000,00 -> 25000.00)
        posting = salary_txn.postings[0]
        assert posting.units.number == decimal.Decimal("25000.00")
        assert posting.units.currency == "DKK"

    def test_extract_narration_format(self, importer, temp_csv_file):
        """Test that narration is properly formatted."""
        entries = list(importer.extract(temp_csv_file, []))

        # Check narration format (combines columns 0 and 1 with separator)
        for txn in entries:
            assert isinstance(txn.narration, str)
            # Should contain the posteringstekst
            assert len(txn.narration) > 0


class TestLSBImporterFinalize:
    """Tests for transaction finalization logic."""

    def test_finalize_internal_transfer_skip_receiving_side(
        self, importer_with_account_map
    ):
        """Test that receiving side of internal transfers is skipped."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # Receiving side (positive amount)
            writer.writerow(
                [
                    "",
                    "Fra Opsparingskonto",
                    "1234 9876543210",
                    "1234 5678901234",
                    "1000,00",
                    "Test User",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000005",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer_with_account_map.extract(filepath, []))
            # Receiving side should be skipped
            assert len(entries) == 0
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_finalize_internal_transfer_sending_side(self, importer_with_account_map):
        """Test that sending side of internal transfers includes balancing posting."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # Sending side (negative amount)
            writer.writerow(
                [
                    "",
                    "Til Forbrugskonto",
                    "1234 5678901234",
                    "1234 9876543210",
                    "-1000,00",
                    "Test User",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000006",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer_with_account_map.extract(filepath, []))
            assert len(entries) == 1

            txn = entries[0]
            # Should have two postings: one for source, one for destination
            assert len(txn.postings) == 2
            assert txn.postings[0].account == "Assets:LSB:Savings"
            assert txn.postings[1].account == "Assets:LSB:Checking"
            # Second posting should have None for units (auto-balanced)
            assert txn.postings[1].units is None
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_finalize_external_transaction(self, importer):
        """Test that external transactions (no account map) are not modified."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # External transaction
            writer.writerow(
                [
                    "",
                    "External Payment",
                    "",
                    "1234 5678901234",
                    "100,00",
                    "",
                    "",
                    "27-12-2025",
                    "29-12-2025",
                    "29-12-2025",
                    "29-12-2025",
                    "1000000007",
                    "2000000002",
                    "",
                    "",
                    "Test Receiver",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer.extract(filepath, []))
            assert len(entries) == 1

            txn = entries[0]
            # External transactions should only have one posting
            assert len(txn.postings) == 1
            assert txn.postings[0].account == "Assets:LSB:Savings"
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_finalize_with_unknown_internal_account(self, importer_with_account_map):
        """Test transfer to account not in account_map."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # Transfer to unknown account
            writer.writerow(
                [
                    "",
                    "Til ukendt konto",
                    "1234 5678901234",
                    "9999 9999999999",
                    "-1000,00",
                    "Test User",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000008",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer_with_account_map.extract(filepath, []))
            assert len(entries) == 1

            txn = entries[0]
            # Should only have one posting (external transaction)
            assert len(txn.postings) == 1
        finally:
            Path(filepath).unlink(missing_ok=True)


class TestLSBImporterCSVDialect:
    """Tests for CSV dialect configuration."""

    def test_csv_dialect_settings(self, importer):
        """Test that CSV dialect is configured correctly."""
        assert importer.dialect.delimiter == ";"
        assert importer.dialect.quotechar == '"'
        assert importer.dialect.lineterminator == "\r\n"

    def test_encoding_setting(self, importer):
        """Test that encoding is set to UTF-8 with BOM."""
        assert importer.encoding == "utf-8-sig"

    def test_no_header_configuration(self, importer):
        """Test that header configuration is correct."""
        assert importer.names is False
        assert importer.header == 0
        assert importer.footer == 0


class TestLSBImporterEdgeCases:
    """Tests for edge cases and error handling."""

    def test_missing_amount_field(self, importer):
        """Test handling of rows with missing amount."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            # Row with empty amount
            writer.writerow(
                [
                    "",
                    "Test Transaction",
                    "",
                    "1234 5678901234",
                    "",  # Empty amount
                    "",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000009",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            # Empty amounts should raise a decimal.InvalidOperation
            with pytest.raises(decimal.InvalidOperation):
                list(importer.extract(filepath, []))
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_very_large_amount(self, importer):
        """Test handling of very large amounts."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                [
                    "",
                    "Large Transfer",
                    "",
                    "1234 5678901234",
                    "1.234.567,89",  # Large amount with Danish formatting
                    "",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000010",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer.extract(filepath, []))
            if entries:
                txn = entries[0]
                # Check that large amount is parsed correctly
                assert txn.postings[0].units.number == decimal.Decimal("1234567.89")
        finally:
            Path(filepath).unlink(missing_ok=True)

    def test_zero_amount(self, importer):
        """Test handling of zero amount transactions."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            suffix="_Posteringsdetaljer.csv",
            delete=False,
            newline="",
        ) as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(
                [
                    "",
                    "Zero Transaction",
                    "",
                    "1234 5678901234",
                    "0,00",
                    "",
                    "",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "02-01-2026",
                    "1000000011",
                    "",
                    "",
                    "",
                    "",
                ]
            )
            filepath = f.name

        try:
            entries = list(importer.extract(filepath, []))
            # Zero amount transactions should be handled
            if entries:
                txn = entries[0]
                assert txn.postings[0].units.number == decimal.Decimal("0")
        finally:
            Path(filepath).unlink(missing_ok=True)
