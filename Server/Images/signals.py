from django.dispatch import receiver
from django.db.models.signals import post_save
from .tasks import compare_images
from .models import Image, Similar


@receiver(post_save, sender=Image)
def comparison_handler(sender, instance, **kwargs):
  print(instance._id)
  compare_images.delay(instance.imgipfsHash)
  
@receiver(post_save, sender=Similar)
def similar_save(sender, instance, **kwargs):
  print("SIMILAR MODEL SAVED")