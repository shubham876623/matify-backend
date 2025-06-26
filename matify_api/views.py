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
    
    def delete(self, request):
        image_id = request.data.get('id')  # or use `request.query_params.get('id')` for query param
        if not image_id:
            return Response({"detail": "Image ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            image = GeneratedImage.objects.get(id=image_id, user=request.user)
            image.delete()
            return Response({"detail": "Image deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except GeneratedImage.DoesNotExist:
            return Response({"detail": "Image not found."}, status=status.HTTP_404_NOT_FOUND)


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
