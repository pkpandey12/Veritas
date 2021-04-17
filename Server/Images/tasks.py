from celery import shared_task
from celery.utils.log import get_task_logger
import glob
import os
import io
from .models import Image, Similar
from PIL import Image as pillow_image
import ipfshttpclient
from pixelmatch.contrib.PIL import pixelmatch
import multiprocessing as mp
import numpy as np
from functools import reduce
import operator


def prod(iterable):
    return reduce(operator.mul, iterable, 1)

logger = get_task_logger(__name__)

# TODO: potentially make use of the skimage library
# TODO: add error handling

SIMILARITY_THRESHOLD = 50
NUMBER_OF_PROCESSES = 4
IMAGE_REDUCTION_FACTOR = 8

@shared_task
def compare_images(id):
  ipfs = ipfshttpclient.connect("/dns/ipfs.infura.io/tcp/5001/https")
  instance = Image.objects.get(imgipfsHash = id)
  logger.info(instance.imgipfsHash)
  cat_resp = ipfs.cat(instance.imgipfsHash)
  i1 = pillow_image.open(io.BytesIO(cat_resp))
  i1 = i1.resize(tuple(int(x/IMAGE_REDUCTION_FACTOR) for x in i1.size), pillow_image.ANTIALIAS)
  images = np.array(Image.objects.exclude(imgipfsHash=id))
  chunks = np.array_split(images,NUMBER_OF_PROCESSES)

  with mp.Manager() as manager:
    jobs = []
    comp_list = manager.list()
    for (i,s) in enumerate(chunks):
      j = mp.Process(target=comparison_thread, args=(comp_list, i, ipfs, s, i1))
      j.start()
      jobs.append(j)    
    
    for j in jobs:
      j.join()
    
    logger.info(comp_list)
    sim_flag = create_similar(comp_list, instance)

    if not sim_flag:
      Image.objects.filter(imgipfsHash = id).update(verified=True)

  logger.info("Comparison process finished")

  # TODO: add post comparison signal perhaps?
  

def create_similar(comp_list, instance):
  if not comp_list:
    return False
  for sim in comp_list:
    Similar.objects.create(
      parent_image = instance,
      ipfsHash = sim["ipfs"],
      percentage = sim["percentage"]
    )
  return True

def comparison_thread(comp_list, i,ipfs, images, i1):
  for im in images:
    i2 = pillow_image.open(io.BytesIO(ipfs.cat(im.imgipfsHash)))
    i2 = i2.resize(i1.size)
    logger.info(i1.size)
    logger.info(i2.size)
    mismatch = pixelmatch(i1, i2, None, includeAA=True)
    logger.info(mismatch)
    percentage = (prod(i1.size) - mismatch) * 100 / prod(i1.size)
    logger.info("percentage:\t"+str(percentage))
    if percentage>SIMILARITY_THRESHOLD:
      comp_list.append({
        "ipfs": im.imgipfsHash,
        "percentage": percentage
      })
