from budget_logic import allocate, build_review_queue, process_edits


def make_transaction(merchant="STARBUCKS", transaction_id=1):
    return {
        "id": transaction_id,
        "merchant_normalized": merchant,
        "pre_categorization": "Food & Drink",
        "total": -5.0,
        "prefix": None,
        "allocations": [{"category": "TBD", "amount": 0}],
        "needs_review": True,
        "merchant_ambiguous": True,
    }


def test_unambiguous_memory_is_reused_without_model_call():
    memory = {
        "STARBUCKS": {"categories": ["F&B"], "ambiguous": False}
    }

    def fail_if_called(*args):
        raise AssertionError("Model should not be called for unambiguous memory")

    transaction = allocate(make_transaction(), memory, categorize=fail_if_called)

    assert transaction["allocator"] == "Memory"
    assert transaction["needs_review"] is False
    assert transaction["allocations"] == [{"category": "F&B", "amount": -5.0}]


def test_unseen_merchant_uses_model_and_requires_review():
    transaction = allocate(
        make_transaction("NEW MERCHANT"),
        {},
        categorize=lambda *args: "Goods",
    )

    assert transaction["allocator"] == "LLM"
    assert transaction["needs_review"] is True
    assert build_review_queue([transaction]) == [transaction]
    assert transaction["allocations"] == [{"category": "Goods", "amount": -5.0}]


def test_invalid_model_category_falls_back_to_other_and_requires_review():
    transaction = allocate(
        make_transaction("NEW MERCHANT"),
        {},
        categorize=lambda *args: "Here is my answer: Goods",
    )

    assert transaction["needs_review"] is True
    assert transaction["allocations"][0]["category"] == "Other"


def test_process_edits_matches_transactions_by_id():
    memory = {}
    transactions = [
        make_transaction("FIRST", 1),
        make_transaction("SECOND", 2),
    ]
    edits = [
        {**transactions[0], "category": "F&B", "merchant_ambiguous": False},
        {**transactions[1], "category": "Goods", "merchant_ambiguous": True},
    ]

    process_edits(memory, transactions, edits)

    assert transactions[0]["allocations"][0]["category"] == "F&B"
    assert transactions[1]["allocations"][0]["category"] == "Goods"
    assert memory["FIRST"] == {"categories": ["F&B"], "ambiguous": False}
    assert memory["SECOND"] == {"categories": ["Goods"], "ambiguous": True}
