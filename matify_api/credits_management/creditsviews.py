from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from matify_api.models import UserCredits
from matify_api.serializers import UserCreditsSerializer

class CreditsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        credits, _ = UserCredits.objects.get_or_create(user=request.user)
        serializer = UserCreditsSerializer(credits)
        return Response(serializer.data)