from djongo import models
from django.utils.timezone import now

# Create your models here.

class Text(models.Model):
  _id = models.ObjectIdField(primary_key=True, unique=True)
  title = models.CharField(max_length=280, default="Title")
  ipfsHash = models.CharField(max_length=128, null=True)
  ipfsAddress = models.CharField(max_length=128, null=True)
  transactionHash = models.CharField(max_length=128, null=True)
  blockHash = models.CharField(max_length=128, null=True)
  timestamp = models.DateTimeField(default=now, editable=False)
  body = models.TextField()

  def __str__(self):
    return self.title