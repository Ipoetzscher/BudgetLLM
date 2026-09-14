import os
import requests
from datetime import datetime

BASE_URL = os.getenv("BUDGET_API_URL", "http://127.0.0.1:8000/api")
REQUEST_TIMEOUT = 5

# GET, POST, PATCH, DELETE
def get_active_session():
    response = requests.get(f"{BASE_URL}/session/", timeout=REQUEST_TIMEOUT)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def create_active_session():
    response = requests.post(f"{BASE_URL}/session/", json={}, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()

def delete_active_session():
    response = requests.delete(f"{BASE_URL}/session/",timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

def create_transaction(transaction_data):
    response = requests.post(f"{BASE_URL}/transactions/", json=transaction_data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()

def update_transaction(transaction_id, changes):
    response = requests.patch(f"{BASE_URL}/transactions/{transaction_id}/", json=changes, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


# TRANSLATION
def transaction_to_api_data(transaction, session_id):
    return {
        "session": session_id,
        "merchant": transaction["merchant"],
        "merchant_normalized": transaction["merchant_normalized"],
        "amount": transaction["total"],
        "category": transaction["allocations"][0]["category"],
        "date": datetime.strptime(
            transaction["date"],
            "%m/%d/%Y",
        ).date().isoformat(),
        "account": transaction["account"],
        "needs_review": transaction["needs_review"],
        "merchant_ambiguous": transaction["merchant_ambiguous"],
    }

def save_processed_transactions(transactions):
    session = create_active_session()
    session_id = session["id"]
    saved_transactions = []

    try:
        for transaction in transactions:
            transaction_data = transaction_to_api_data(transaction, session_id)
            saved_transaction = create_transaction(transaction_data)
            saved_transactions.append(saved_transaction)

    except Exception:
        delete_active_session()
        raise

    # Update IDs only after every transaction was saved successfully.
    for index in range(len(transactions)):
        transactions[index]["id"] = saved_transactions[index]["id"]

    return transactions


def active_session_to_transactions(session):
    transactions = []

    saved_transactions = sorted(session["transactions"], key=lambda transaction: transaction["id"])

    for saved_transaction in saved_transactions:
        saved_date = datetime.strptime(saved_transaction["date"],"%Y-%m-%d")
        amount = float(saved_transaction["amount"])
        transaction = {
            "id": saved_transaction["id"],
            "month": saved_date.strftime("%m"),
            "account": saved_transaction["account"],
            "date": saved_date.strftime("%m/%d/%Y"),
            "merchant": saved_transaction["merchant"],
            "merchant_normalized": saved_transaction["merchant_normalized"],
            "total": amount,
            "pre_categorization": "",
            "allocations": [
                {
                    "category": saved_transaction["category"],
                    "amount": amount,
                }
            ],
            "prefix": None,
            "description": "",
            "allocator": "Database",
            "needs_review": saved_transaction["needs_review"],
            "merchant_ambiguous": saved_transaction["merchant_ambiguous"],
        }

        transactions.append(transaction)

    return transactions


def save_review_progress(edited_transactions):
    for transaction in edited_transactions:
        changes = {
            "category": transaction["category"],
            "merchant_ambiguous": transaction["merchant_ambiguous"],
        }

        update_transaction(transaction["id"], changes)


def save_completed_transactions(transactions):
    for transaction in transactions:
        changes = {
            "category": transaction["allocations"][0]["category"],
            "merchant_ambiguous": transaction["merchant_ambiguous"],
            "needs_review": False,
        }

        update_transaction(transaction["id"], changes)