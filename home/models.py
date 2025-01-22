from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Add(models.Model):
    title = models.CharField(max_length=122)
    amount = models.CharField(max_length=122)
    category = models.CharField(max_length=12)
    notes = models.TextField()
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username if self.user else 'No User'