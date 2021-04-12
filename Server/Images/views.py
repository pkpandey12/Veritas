"""
Imports and Libraries
"""

from django.shortcuts import render, redirect
from django.urls import reverse
import json
from web3 import Web3, HTTPProvider
from .models import Image
from .serializers import ImageSerializer
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
from django.core.files.images import ImageFile
import ipfshttpclient
import base64
import ast
import dateutil.parser
# Create your views here.

blockchain_address = 'http://localhost:8545'
web3 = Web3(HTTPProvider(blockchain_address))
# /dns/ipfs-api.example.com/tcp/443/https
ipfs = ipfshttpclient.connect("/dns/ipfs.infura.io/tcp/5001/https")

web3.eth.defaultAccount = web3.eth.accounts[0]

# TODO: REMEMBER TO CHANGE THESE TO GANACHE SETTINGS AFTER BASIC SERVER TESTS ARE FINISHED

# This depends on your PC's path gotta change it
compiled_contract_path = '/home/sthavir/fyp/Veritas/Server/Blockchain/build/contracts/ImageHash.json'

# Change this every time you to deploy to Ganache
deployed_contract_address = '0xfB67301732FB944b3e1f006cFe6450E420307F25'

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
#     datetime: the datetime of the image

# View to get list of all saved images or upload new image
class ImageListView(APIView):
  parser_classes = (MultiPartParser, )

  # Upload image to IPFS and server's local storage
  def post(self, request, format=None):
    print("IN POST")
    print(request.data)
    file = request.data['file']
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
    
    # this package lets you add stuff to the EXIF, so we can have some
    # useful data stored there
    image_exif = exImage(image_from_request)

    image_data = {
      "label": request.data['label'],
      "timestamp": request.data['datetime']
    }
    # image description seemed a good tag to use
    image_exif.image_description = str(image_data)

    # upload to IPFS finally
    file_to_upload = BytesIO(image_exif.get_file())
    ipfsResponse = ipfs.add(file_to_upload)
    file_to_upload.close()
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
      ipfsHash = ipfsResponse["Hash"],
      ipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(ipfsResponse['Hash']),
      transactionHash = ipfsResponse["Hash"],
      # TODO: Change below to actual value
      blockHash = ipfsResponse["Hash"],
      photo = request.data["file"]
    )
    newImage.save()
    newImage.delete()
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
      return Image.objects.get(ipfsHash=ipfsHash)
    except Image.DoesNotExist:

        image = ipfs.cat(ipfsHash)

        # This next bit assumes the IPFS hash led to an image
        image_exif = exImage(image)
        image_details_dict = ast.literal_eval(image_exif.image_description)

        newImage = Image(
          label = image_details_dict['label'],
          timestamp = image_details_dict['timestamp'],
          ipfsHash = ipfsHash,
          ipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(ipfsHash),
          transactionHash = ipfsHash,
          blockHash = ipfsHash,
          photo = ImageFile(BytesIO(image), name=image_details_dict['label'])
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
