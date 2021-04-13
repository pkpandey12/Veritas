from django.dispatch import receiver
from django.db.models.signals import post_save
from .tasks import compare_images
from .models import Image


@receiver(post_save, sender=Image)
def comparison_handler(sender, instance, **kwargs):
  print(instance._id)
  compare_images.delay(instance.ipfsHash)
  