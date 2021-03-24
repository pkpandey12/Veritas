"""
Imports and Libraries
"""

from django.shortcuts import render, redirect
from django.urls import reverse
import json
from web3 import Web3, HTTPProvider
from .models import Image
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
from django.http import HttpResponse
import magic
import ipfsApi
# Create your views here.

blockchain_address = 'http://localhost:7545'
web3 = Web3(HTTPProvider(blockchain_address))

ipfs = ipfsApi.Client(host="https://ipfs.infura.io", port=5001)

web3.eth.defaultAccount = web3.eth.accounts[0]

# TODO: REMEMBER TO CHANGE THESE TO GANACHE SETTINGS AFTER BASIC SERVER TESTS ARE FINISHED

compiled_contract_path = '/Users/praneetkumarpandey/FYP/RevPro-FYP/veritas/Blockchain/build/contracts/ImageHash.json'

deployed_contract_address = '0x5e080Ceda0e9f365ef1405BF43C17DdE34F8e0A1'

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

class ImageView(APIView):
  parser_classes = (MultiPartParser, )

  def post(self, request, format=None):
    print(request.data)
    file = request.FILES['file']

    # IPFS upload

    if not file:
      return Response("No file provided")
    
    if "image" not in magic.from_file(file, mime=True):
      return Response("File provided must be an image")

    if req.file.size > MAX_SIZE:
      return Response("File provided must be less than "+str(MAX_SIZE)+" bytes")

    ipfsResponse = ipfs.add(file)
    if not ipfsResponse:
      return Response("IPFS processing error")
    else:
      print("IPFS upload successful, hash = " + str(ipfsResponse['Hash']))

    # Blockchain upload
    # TODO: Add error handling
    
    ethResp = contract.functions.saveHash(ipfsResponse['Hash'])).call()

    # Saving the model locally

    newImage = Image(
      label = request.data["label"],
      datetime = request.data["datetime"],
      ipfsHash = ipfsResponse["Hash"],
      ipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(req.data.ipfsHash),
      transactionHash = ipfsResponse["Hash"],
      # TODO: Change below to actual value
      blockHash = ipfsResponse["Hash"],
    )

    Image.save()
    
      