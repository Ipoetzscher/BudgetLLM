import pytest

from memory import normalize_merchant


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("SQ *ROOSTER &amp; RICE", ("ROOSTER & RICE", "SQ")),
        ("STARBUCKS STORE 17211", ("STARBUCKS", None)),
        ("TARGET 00014076", ("TARGET", None)),
        ("TST*LETS ROLL ICE CREAME", ("LETS ROLL ICE CREAME", "TST")),
        ("Amazon.com*PA2BZ6883", ("AMAZON MKTPL", None)),
        ("Amazon Prime*ZP4HV1A", ("AMAZON PRIME", None)),
        ("UBER *EATS", ("UBER EATS", None)),
    ],
)
def test_normalize_credit_card_merchants(description, expected):
    assert normalize_merchant(description, "CC") == expected


def test_normalize_wells_fargo_purchase_uses_credit_card_cleanup():
    description = (
        "PURCHASE AUTHORIZED ON 01/01 SP INTELLIGENT CHA INTELLIGENTCH CA "
        "S123456789 CARD 1234"
    )

    assert normalize_merchant(description, "WF") == (
        "INTELLIGENT CHA INTELLIGENTCH CA",
        None,
    )


def test_family_markers_come_from_environment(monkeypatch):
    monkeypatch.setenv("BUDGET_FAMILY_MARKERS", "EXAMPLEFAMILY,EXAMPLEFIRST")

    assert normalize_merchant(
        "ZELLE FROM THE EXAMPLEFAMILY TRUST ON 01/11 REF # ABC123",
        "WF",
    ) == ("ZELLE FROM DAD", None)
