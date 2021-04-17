from djongo import models
from django.utils.timezone import now
import json

# Create your models here.

# Images model to access data from backend and IPFS endpoint

class Image(models.Model):
  _id = models.ObjectIdField(primary_key=True, unique=True)
  label = models.TextField(default="THIS IS A LABEL FOR AN IMAGE")
  imgipfsHash = models.CharField(max_length=128, null=True)
  imgipfsAddress = models.CharField(max_length=128, null=True)
  textipfsHash = models.CharField(max_length=128, null=True)
  textipfsAddress = models.CharField(max_length=128, null=True)
  transactionHash = models.CharField(max_length=128, null=True)
  blockHash = models.CharField(max_length=128, null=True)
  timestamp = models.DateTimeField(default=now, editable=False)
  photo = models.ImageField(upload_to='images')
  tags = models.TextField(default=json.dumps(["image"]))
  article = models.TextField()

  def __str__(self):
    return self.label

  def get_tags(self):
    if self.tags:
      return json.loads(self.tags)
    else:
      return json.loads(json.dumps(["image"]))

class Similar(models.Model):
  parent_image = models.ForeignKey(Image, on_delete=models.CASCADE)
  image_id = models.ObjectIdField(primary_key=True, unique=True)
  ipfsHash = models.CharField(max_length=128, null=True)
  percentage = models.FloatField(null=True)

  def __str__(self):
    return self.image_id