from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import GeneratedImage, ProcessedImage
from .serializers import GeneratedImageSerializer, ProcessedImageSerializer


class GeneratedImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        images = GeneratedImage.objects.filter(user=request.user).order_by('-created_at')
        serializer = GeneratedImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GeneratedImageSerializer(data={
            'user': request.user.id,
            'image_url': request.data.get('image_url')
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProcessedImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        images = ProcessedImage.objects.filter(user=request.user).order_by('-created_at')
        serializer = ProcessedImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProcessedImageSerializer(data={
            'user': request.user.id,
            'image_url': request.data.get('image_url'),
            'source': request.data.get('source'),
            'description': request.data.get('description', '')
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
