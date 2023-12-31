from django.db import models
from django.contrib.auth.models import User


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Reset Code for {self.user}"