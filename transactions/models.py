from django.db import models

# Create your models here.
class Transaction(models.Model):
    merchant = models.CharField(max_length=255)
    merchant_normalized = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, blank=True, default="")
    date = models.DateField()
    account = models.CharField(max_length=10)
    needs_review = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.merchant} — {self.amount}"