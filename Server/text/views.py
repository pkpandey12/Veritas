from django.shortcuts import render

from django.shortcuts import render, redirect
from django.urls import reverse
import json
from web3 import Web3, HTTPProvider
from .models import Text
from .serializers import TextSerializer
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
from io import BytesIO, StringIO
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

# View to upload new text post to IPFS and server storage

# Request format: 
#     title: text title
#     datetime: the timestamp of the image
#     body: text body
class TextListView(APIView):
  parser_classes = (MultiPartParser, )

  # Upload text to IPFS and server's local storage
  def post(self, request, format=None):
    title = request.data['title']
    body = request.data['body']

    # IPFS upload
    if (not title or not body) :
      return Response("No text provided")

    if len(title + body) > MAX_SIZE:
      return Response("File provided must be less than "+str(MAX_SIZE)+" bytes")
    
    timestamp = request.data["datetime"]

    text_data = {
        'title': title,
        'timestamp': timestamp
    }
    text_to_upload = BytesIO((str(text_data) + "\n ENDMETA \n" + body).encode(encoding='UTF-8'))
    # upload to IPFS finally
    ipfsResponse = ipfs.add(text_to_upload)
    text_to_upload.close()
    if not ipfsResponse:
      return Response("IPFS processing error")
    else:
      print("IPFS upload successful, hash = " + str(ipfsResponse['Hash']))

    # Blockchain upload
    # TODO: Add error handling
    
    ethResp = contract.functions.saveHash(ipfsResponse['Hash']).call()
    print("ETHEREUM RESPONSE", ethResp)
    # Saving the model locally

    newText = Text(
      title = title,
      timestamp = dateutil.parser.parse(timestamp),
      ipfsHash = ipfsResponse["Hash"],
      ipfsAddress = "https://gateway.ipfs.io/ipfs/"+str(ipfsResponse['Hash']),
      transactionHash = ipfsResponse["Hash"],
      # TODO: Change below to actual value
      blockHash = ipfsResponse["Hash"],
      body = body
    )
    newText.save()
    newText.delete()
    serializer = TextSerializer(newText)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

  # Get image from server DB
  def get(self, request, format=None):
    print("IN GET")
    texts = Text.objects.all()
    serializer = TextSerializer(texts, many=True)
    return Response(serializer.data)



# Retrieve specific image by IPFS hash, or delete existing image
class TextDetailView(APIView):

  def get_object(self, ipfsHash):
    try: 
      return Text.objects.get(ipfsHash=ipfsHash)
    except Text.DoesNotExist:

        text = ipfs.cat(ipfsHash).decode('utf-8')
        # This next bit assumes the IPFS hash led to text
        string_segments = text.split('\n ENDMETA \n')
        text_data = ast.literal_eval(string_segments[0])
        body = string_segments[1]

        newText = Text(
          title = text_data['title'],
          timestamp = dateutil.parser.parse(text_data['timestamp']),
          ipfsHash = ipfsHash,
          ipfsAddress = "https://gateway.ipfs.io/ipfs/"+ipfsHash,
          transactionHash = ipfsHash,
          # TODO: Change below to actual value
          blockHash = ipfsHash,
          body = body
        )
        newText.save()
        return newText
        
        #raise Http404
      
  # Return image in response
  def get(self, request, ipfsHash, format=None):
    text = self.get_object(ipfsHash)
    serializer = TextSerializer(text)
    return Response(serializer.data)

  def delete(self, request, ipfsHash, format=None):
    text = self.get_object(ipfsHash)
    text.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)