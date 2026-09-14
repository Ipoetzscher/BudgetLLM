from rest_framework import serializers
from .models import Transaction, ActiveSession

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "session",
            "merchant",
            "merchant_normalized",
            "amount",
            "category",
            "date",
            "account",
            "needs_review",
            "merchant_ambiguous",
        ]

class ActiveSessionSerializer(serializers.ModelSerializer):

    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = ActiveSession
        fields = [
            "id",
            "created_at",
            "updated_at",
            "transactions"
        ]