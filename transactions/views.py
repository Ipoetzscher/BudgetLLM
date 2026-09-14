from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Transaction, ActiveSession
from .serializers import TransactionSerializer, ActiveSessionSerializer


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

@api_view(["PATCH"])
def transaction_detail(request, transaction_id):
    if request.method == "PATCH":
        try: 
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({"detail": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TransactionSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


@api_view(["GET", "POST", "DELETE"])
def active_session(request):
    if request.method == "GET":
        session = ActiveSession.objects.first()
        if session is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ActiveSessionSerializer(session)
        return Response(serializer.data)

    if request.method == "POST":
        if ActiveSession.objects.exists():
            return Response({"detail": "An active session already exists."}, status=status.HTTP_409_CONFLICT)
        serializer = ActiveSessionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        session = ActiveSession.objects.first()
        if session is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

