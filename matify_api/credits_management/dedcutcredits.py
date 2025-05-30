from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings

from matify_api.models import UserCredits
from matify_api.serializers import UserCreditsSerializer


class DeductCreditsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        amount = request.data.get("amount", 1)
        credits = UserCredits.objects.get(user=request.user)
        if credits.credits_remaining >= amount:
            credits.credits_remaining -= amount
            credits.credits_used += amount
            credits.save()
            return Response({"status": "deducted"})
        else:
            return Response({"error": "Not enough credits"}, status=400)