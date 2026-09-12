from budget_logic import (
    process_chase_csv,
    process_uploaded_files,
    process_wells_fargo_csv,
)

from conftest import UploadedCsv


CHASE_CSV = """Transaction Date,Description,Amount,Category
07/30/2026,STARBUCKS STORE 12345,-6.25,Food & Drink
07/31/2026,TARGET 00014076,-20.00,Shopping
"""

WELLS_FARGO_CSV = """DATE,DESCRIPTION,AMOUNT,CHECK #,STATUS
07/31/2026,VENMO PAYMENT 260731 12345 EXAMPLE PERSON,-10.00,,Posted
08/01/2026,MOBILE DEPOSIT : REF NUMBER : 12345,50.00,,Posted
"""


def test_process_chase_csv_builds_transactions():
    transactions = process_chase_csv(UploadedCsv(CHASE_CSV))

    assert [transaction["id"] for transaction in transactions] == [1, 2]
    assert transactions[0]["account"] == "CC"
    assert transactions[0]["merchant_normalized"] == "STARBUCKS"
    assert transactions[0]["total"] == -6.25
    assert transactions[0]["pre_categorization"] == "Food & Drink"


def test_process_wells_fargo_csv_sanitizes_descriptions():
    transactions = process_wells_fargo_csv(UploadedCsv(WELLS_FARGO_CSV))

    assert [transaction["id"] for transaction in transactions] == [1, 2]
    assert transactions[0]["account"] == "WF"
    assert transactions[0]["merchant"] == "VENMO PAYMENT"
    assert "EXAMPLE PERSON" not in transactions[0]["merchant"]
    assert transactions[0]["merchant_normalized"] == "VENMO PAYMENT"
    assert transactions[0]["total"] == -10.0
    assert transactions[0]["pre_categorization"] == ""


def test_combined_transactions_are_chase_first_with_sequential_ids():
    transactions = process_uploaded_files(
        UploadedCsv(CHASE_CSV),
        UploadedCsv(WELLS_FARGO_CSV),
    )

    assert [transaction["account"] for transaction in transactions] == [
        "CC", "CC", "WF", "WF"
    ]
    assert [transaction["id"] for transaction in transactions] == [1, 2, 3, 4]


def test_wells_fargo_only_starts_at_one():
    transactions = process_uploaded_files(wf_file=UploadedCsv(WELLS_FARGO_CSV))

    assert [transaction["id"] for transaction in transactions] == [1, 2]
