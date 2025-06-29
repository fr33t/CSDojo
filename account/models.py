from django.db import models


# Create your models here.
class User(models.Model):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=254, unique=True)
    password_hash = models.CharField(max_length=254)
    totp_uri = models.CharField(max_length=254, unique=True)

    # avatar url?
    def __str__(self):
        return f"{self.nickname}"
