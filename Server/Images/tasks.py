from celery import shared_task
from celery.utils.log import get_task_logger
import glob
import os
import io
from .models import Image, Similar
from PIL import Image as pillow_image
import ipfshttpclient
from pixelmatch.contrib.PIL import pixelmatch
import multiprocessing
import numpy as np
from functools import reduce
import operator


def prod(iterable):
    return reduce(operator.mul, iterable, 1)

logger = get_task_logger(__name__)

# TODO: potentially make use of the skimage library
# TODO: add error handling

SIMILARITY_THRESHOLD = 40
NUMBER_OF_PROCESSES = 4
IMAGE_REDUCTION_FACTOR = 4

@shared_task
def compare_images(id):
  ipfs = ipfshttpclient.connect("/dns/ipfs.infura.io/tcp/5001/https")
  instance = Image.objects.get(ipfsHash = id)
  logger.info(instance.ipfsHash)
  cat_resp = ipfs.cat(instance.ipfsHash)
  i1 = pillow_image.open(io.BytesIO(cat_resp))
  i1 = i1.resize(tuple(int(x/IMAGE_REDUCTION_FACTOR) for x in i1.size), pillow_image.ANTIALIAS)
  images = np.array(Image.objects.all())
  chunks = np.array_split(images,NUMBER_OF_PROCESSES)
  jobs = []
  for (i,s) in enumerate(chunks):
    j = multiprocessing.Process(target=comparison_thread, args=(i, ipfs, instance, s, i1))
    jobs.append(j)
  
  for j in jobs:
    j.start()
  
  for j in jobs:
    j.join()

  logger.info("Comparison process finished")

  # TODO: add post comparison signal perhaps?
  

def create_similar(instance, percentage):
  newSimilar = Similar(
    parent_image = instance,
    percentage = percentage
  )
  newSimilar.save()
  return True

def comparison_thread(i,ipfs, instance, images, i1):
  for i in images:
    i2 = pillow_image.open(io.BytesIO(ipfs.cat(i.ipfsHash)))
    i2 = i2.resize(i1.size)
    logger.info(i1.size)
    logger.info(i2.size)
    mismatch = pixelmatch(i1, i2, None, includeAA=True)
    logger.info(mismatch)
    percentage = (prod(i1.size) - mismatch) * 100 / prod(i1.size)
    logger.info("percentage:\t"+str(percentage))
    if percentage>SIMILARITY_THRESHOLD:
      created_flag = create_similar(instance, percentage)


# from celery import shared_task
# from celery.utils.log import get_task_logger
# import glob
# import os
# import io
# from .models import Image, Similar
# from PIL import Image as pillow_image
# import ipfshttpclient
# from math import prod
# from pixelmatch.contrib.PIL import pixelmatch

# logger = get_task_logger(__name__)

# @shared_task
# def compare_images(id):
#   ipfs = ipfshttpclient.connect("/dns/ipfs.infura.io/tcp/5001/https")
#   instance = Image.objects.get(ipfsHash = id)
#   logger.info(instance.ipfsHash)
#   cat_resp = ipfs.cat(instance.ipfsHash)
#   i1 = pillow_image.open(io.BytesIO(cat_resp))
#   i1 = i1.resize(tuple(int(x/4) for x in i1.size), pillow_image.ANTIALIAS)
#   images = Image.objects.all()
#   for i in images:
#     i2 = pillow_image.open(io.BytesIO(ipfs.cat(i.ipfsHash)))
#     i2 = i2.resize(i1.size)
#     logger.info(i1.size)
#     logger.info(i2.size)
#     mismatch = pixelmatch(i1, i2, None, includeAA=True)
#     logger.info(mismatch)
#     percentage = (prod(i1.size) - mismatch) * 100 / prod(i1.size)
#     logger.info("percentage:\t"+str(percentage))
#     if percentage>40:
#       created_flag = createSimilar(instance, percentage)

# def createSimilar(instance, percentage):
#   newSimilar = Similar(
#     parent_image = instance,
#     percentage = percentage
#   )
#   newSimilar.save()
#   return True