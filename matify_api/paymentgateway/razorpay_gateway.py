
import razorpay
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

class CreateRazorpayOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = 10000  # ₹100 * 100 (paise)

        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"receipt_user_{user.id}",
            "notes": {
                "user_id": str(user.id),
                "credits": 100
            }
        }

        order = razorpay_client.order.create(data=order_data)

        return Response({
            "order_id": order["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount,
            "currency": "INR"
        })
