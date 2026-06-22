from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login

User = get_user_model()


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({'detail':'id_token is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            #verifying google token
            plyload = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            #verifying email
            if not plyload.get('email_verified'):
                return Response({'detail':'Google Email Is Not VERIFIED!'}, status=status.HTTP_400_BAD_REQUEST)
            
            email = plyload.get('email')
            first_name = plyload.get('given_name', '')
            last_name = plyload.get('family_name', '')

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username':email,
                    'first_name':first_name,
                    'last_name':last_name,
                }
            )

            if created:
                user.set_unusable_password()
                user.save()

            update_last_login(None, user)

            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    'access':str(refresh.access_token),
                    'refresh':str(refresh),
                    'user':{
                        'id':user.id,
                        'email':user.email,
                        'first_name':user.first_name,
                        'last_name':user.last_name,
                    }
                },
                status= status.HTTP_201_CREATED
            )
        
        except Exception as e:
            return Response({
                'detail':f"Invalied Google token: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            