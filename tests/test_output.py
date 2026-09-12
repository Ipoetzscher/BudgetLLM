import csv
from io import StringIO

import pytest

from budget_logic import create_left_output, create_right_output, handle_split_rules


def make_output_transaction(transaction_id, merchant, category, amount):
    return {
        "id": transaction_id,
        "month": "07",
        "account": "CC",
        "date": "07/31/2026",
        "merchant": merchant,
        "description": "",
        "total": amount,
        "allocations": [{"category": category, "amount": amount}],
    }


def test_split_rule_does_not_modify_original_and_preserves_total():
    allocations = [
        {"category": "F&B", "amount": -10.00},
        {"category": "Uber", "amount": -20.00},
    ]
    original = [allocation.copy() for allocation in allocations]

    result = handle_split_rules(allocations)

    assert allocations == original
    assert sum(item["amount"] for item in result) == pytest.approx(-30.0)
    assert result == [
        {"category": "F&B", "amount": -10.00},
        {"category": "Uber", "amount": -5.00},
        {"category": "Parent T&E", "amount": -15.00},
    ]


def test_left_and_right_outputs_have_matching_rows_in_input_order():
    transactions = [
        make_output_transaction(1, "FIRST", "F&B", -5.0),
        make_output_transaction(2, "SECOND", "Goods", -10.0),
    ]

    left_rows = list(csv.reader(StringIO(create_left_output(transactions)), delimiter="\t"))
    right_rows = list(csv.reader(StringIO(create_right_output(transactions)), delimiter="\t"))

    assert len(left_rows) == len(right_rows) == 2
    assert left_rows[0][3] == "FIRST"
    assert left_rows[1][3] == "SECOND"
    assert right_rows[0][0] == "-5.0"
    assert right_rows[1][3] == "-10.0"
