from rest_framework import serializers
from .models import TrainedModel ,Gallery ,UserCredits
from rest_framework import serializers
from .models import GeneratedImage, ProcessedImage

class GeneratedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedImage
        fields = ['id', 'user', 'image_url', 'created_at']

class ProcessedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedImage
        fields = ['id', 'user', 'image_url', 'source', 'description', 'created_at']


class TrainedModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainedModel
        fields = '__all__'

class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ['id', 'image_url', 'created_at']
        
        


class UserCreditsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCredits
        fields = ['credits_remaining', 'credits_used']