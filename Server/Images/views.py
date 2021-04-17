"""
Imports and Libraries
"""

from django.shortcuts import render, redirect
from django.urls import reverse
import json
from web3 import Web3, HTTPProvider
from .models import Image, Similar
from .serializers import ImageSerializer, SimilarSerializer
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin)
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
import magic
from exif import Image as exImage
from PIL import Image as pilImage
from io import BytesIO
import ipfshttpclient
import base64
import ast
import dateutil.parser
# Create your views here.

blockchain_address = 'http://localhost:7545'
web3 = Web3(HTTPProvider(blockchain_address))
# /dns/ipfs-api.example.com/tcp/443/https
ipfs = ipfshttpclient.connect("/dns/ipfs.infura.io/tcp/5001/https")

web3.eth.defaultAccount = web3.eth.accounts[0]

# TODO: REMEMBER TO CHANGE THESE TO GANACHE SETTINGS AFTER BASIC SERVER TESTS ARE FINISHED

# This depends on your PC's path gotta change it
compiled_contract_path = '/Users/praneetkumarpandey/FYP/RevPro-FYP/veritas/Server/Blockchain/build/contracts/ImageHash.json'

# Change this every time you to deploy to Ganache
deployed_contract_address = '0xC421c64d05562890aA8a6498f89A7AeCc0913D1e'

with open(compiled_contract_path) as file:
  contract_json = json.load(file)
  contract_abi = contract_json['abi']

contract = web3.eth.contract(address = deployed_contract_address, abi=contract_abi)

MAX_SIZE = 52428800

"""
Helper functions
"""


# How to call contract function

# message = contract.functions.sayHello().call()

# Request format: 
#     file: the image to be uploaded
#     label: the image's label
#     datetime: the timestamp of the image
#     article: image's accompanying article
#     tags: tags

# View to get list of all saved images or upload new image
class ImageListView(APIView):
  parser_classes = (MultiPartParser, )

  # Upload image to IPFS and server's local storage
  # As far as handling multiple requests at the same time, that is not a problem we are likely to face. gunicorn,(which we use by default
  # as a worker for django deployments on heroku) is singlethreaded, hence, requests will be automatically queued.
  def post(self, request, format=None):
    print("IN POST")
    print(request.data)
    file = request.data['file']
    article = ""
    print(file.size)
    # IPFS upload
    if not file:
      return Response("No file provided")
    
    # gets raw bytes from the file so the buffer can be read 
    # instead of saving to storage first
    
    image_from_request = file.read()
    if "image" not in magic.from_buffer(image_from_request, mime=True):
      return Response("File provided must be an image")
    
    if file.size > MAX_SIZE:
      return Response("File provided must be less than "+str(MAX_SIZE)+" bytes")
    
    # upload article to IPFS
    article_to_upload = BytesIO(article.encode(encoding='UTF-8'))
    article_ipfs_response = ipfs.add(article_to_upload)
    article_to_upload.close()
    if not article_ipfs_response:
      return Response("IPFS processing error")
    else:
      print("IPFS upload successful, hash = " + str(article_ipfs_response['Hash']))
    
    ethResp = contract.functions.saveHash(article_ipfs_response['Hash']).call()

    # this package lets you add stuff to the EXIF, so we can have some
    # useful data stored there
    image_exif = exImage(image_from_request)

    image_data = {
      "label": request.data['label'],
      "timestamp": request.data['datetime'],
      "tags": "red",
      "article_hash": article_ipfs_response['Hash']
    }
    # image description seemed a good tag to use
    image_exif.image_description = str(image_data)

    # upload to IPFS finally
    file_to_upload = BytesIO(image_exif.get_file())
    ipfsResponse = ipfs.add(file_to_upload)
    if not ipfsResponse:
      return Response("IPFS processing error")
    else:
      print("IPFS upload successful, hash = " + str(ipfsResponse['Hash']))

    # Blockchain upload
    # TODO: Add error handling
    
    ethResp = contract.functions.saveHash(ipfsResponse['Hash']).call()
    print("ETHEREUM RESPONSE", ethResp)
    # Saving the model locally

    newImage = Image(
      label = request.data["label"],
      timestamp = dateutil.parser.parse(request.data["datetime"]),
      imgipfsHash = ipfsResponse["Hash"],
      imgipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(ipfsResponse['Hash']),
      articleipfsHash = article_ipfs_response['Hash'],
      transactionHash = ipfsResponse["Hash"],
      # TODO: Change below to actual value
      blockHash = ipfsResponse["Hash"],
      photo = request.data["file"],
      # tags = json.dumps([x.strip() for x in request.data["tags"].split(',')] if request.data["tags"] else ["red"]),
      tags = json.dumps(["red"]),
      article = article
    )
    newImage.save()
    serializer = ImageSerializer(newImage)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  # Get image from server DB
  def get(self, request, format=None):
    print("IN GET")
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    return Response(serializer.data)



# Retrieve specific image by IPFS hash, or delete existing image
class ImageDetailView(APIView):

  def get_object(self, ipfsHash):
    try: 
      return Image.objects.get(imgipfsHash=ipfsHash)
    except Image.DoesNotExist:
      image = ipfs.cat(ipfsHash)
      image_exif = exImage(image)
      image_details_dict = ast.literal_eval(image_exif.image_description)
      article = ipfs.cat(image_details_dict['article_hash']).decode('utf-8')
      newImage = Image(
        label = image_details_dict['label'],
        timestamp = image_details_dict['timestamp'],
        imgipfsHash = ipfsHash,
        imgipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(ipfsHash),
        articleipfsHash = image_details_dict['article_hash'],
        transactionHash = ipfsHash,
        blockHash = ipfsHash,
        photo = image
      )
      newImage.save()
      return newImage
      #raise Http404
      
  # Return image in response
  def get(self, request, ipfsHash, format=None):
    image = self.get_object(ipfsHash)
    serializer = ImageSerializer(image)
    return Response(serializer.data)

  def delete(self, request, ipfsHash, format=None):
    image = self.get_object(ipfsHash)
    image.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# View for investigating tags
class ImageTagView(APIView):
  def post(self, request, format=None):
    print(request.data)
    images = Image.objects.all()
    ids = []
    for i in images:
      if all(item in i.get_tags() for item in request.data["tags"]):
        ids.append(i.imgipfsHash)
    
    filtered_images = Image.objects.filter(imgipfsHash__in=ids).filter(verified=True)
    serializer = ImageSerializer(filtered_images, many=True)
    return Response(serializer.data)

# View for image similarity
class SimilarityView(APIView):
  def get(self, request, ipfsHash, format=None):
    image = Image.objects.get(imgipfsHash=ipfsHash)
    similar_images = Similar.objects.filter(parent_image=image)
    serializer = SimilarSerializer(similar_images, many=True)
    return Response(serializer.data)