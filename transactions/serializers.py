from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "merchant",
            "merchant_normalized",
            "amount",
            "category",
            "date",
            "account",
            "needs_review",
        ]