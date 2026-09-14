from django.db import models

# Create your models here.
class ActiveSession(models.Model): 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    session = models.ForeignKey(ActiveSession, on_delete=models.CASCADE, related_name="transactions", null=True, blank=True)
    merchant = models.CharField(max_length=255)
    merchant_normalized = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, blank=True, default="")
    date = models.DateField()
    account = models.CharField(max_length=10)
    needs_review = models.BooleanField(default=True)
    merchant_ambiguous = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.merchant} — {self.amount}"

