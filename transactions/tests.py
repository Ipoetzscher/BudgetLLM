from django.test import TestCase

# Create your tests here.
from datetime import date
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APIClient

from .models import Transaction


class TransactionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/transactions/"

    def test_post_creates_transaction(self):
        transaction_data = {
            "merchant": "EXAMPLE CAFE",
            "merchant_normalized": "EXAMPLE CAFE",
            "amount": "-12.50",
            "category": "F&B",
            "date": "2026-09-11",
            "account": "CC",
            "needs_review": False,
        }

        response = self.client.post(
            self.url,
            transaction_data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Transaction.objects.count(), 1)

        transaction = Transaction.objects.get()
        self.assertEqual(transaction.merchant, "EXAMPLE CAFE")
        self.assertEqual(transaction.amount, Decimal("-12.50"))

    def test_get_returns_stored_transactions(self):
        Transaction.objects.create(
            merchant="EXAMPLE STORE",
            merchant_normalized="EXAMPLE STORE",
            amount=Decimal("-20.00"),
            category="Goods",
            date=date(2026, 9, 12),
            account="WF",
            needs_review=False,
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["merchant"], "EXAMPLE STORE")
        self.assertEqual(response.data[0]["category"], "Goods")