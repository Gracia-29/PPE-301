from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from .models import *

class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=email, password=password)

        if user is None:
            return Response({"error": "Email ou mot de passe incorrect"}, status=400)

        refresh = RefreshToken.for_user(user)

        return Response({
            "token": str(refresh.access_token),
            "user": {
                "id": user.id,
                "nom": user.get_full_name(),
                "email": user.email,
                "role": user.role,
                "a_hopital": DemandeInscription.objects.filter(
                    patient=user,
                    statut__in=['approuve', 'valide']
                ).exists()
            }
        })
    


class RegisterAPI(APIView):
    def post(self, request):
        data = request.data

        user = CustomUser.objects.create(
            username=data['email'],
            email=data['email'],
            password=make_password(data['password']),
            first_name=data.get('nom', ''),
            role='patient'
        )

        return Response({
            "message": "Compte créé avec succès"
        })
