from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer


@api_view(["GET", "POST"])
def transaction_list(request):
    if request.method == "GET":
        transactions = Transaction.objects.all().order_by("id")
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    if request.method == "POST":
        
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

