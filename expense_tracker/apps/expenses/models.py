from django.db import models
from django.contrib.auth.models import User


class Expenses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags (e.g., work,family,emergency)")
    date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.description} - ${self.amount}"
