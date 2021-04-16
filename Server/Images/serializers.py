from rest_framework import serializers
from .models import Image, Similar

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class SimilarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Similar
        fields = ('image_id', 'ipfsHash', 'percentage')