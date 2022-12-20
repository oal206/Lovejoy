from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class EvaluateRequest(models.Model):
    text = models.CharField(max_length=200)
    contact_via = models.CharField(max_length=80)
    image = models.ImageField(upload_to='images/Evaluation_Pics', null=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
