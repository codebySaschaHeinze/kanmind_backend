from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model using email as login identifier."""
    
    
    username = None
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    def __str__(self):
        return f"{self.fullname} <{self.email}>"