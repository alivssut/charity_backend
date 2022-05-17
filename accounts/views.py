from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from .serializers import UserSerializer


class LogoutAPIView(APIView):
    pass


class UserRegistration(APIView):
    def post(self , request):
        form = UserSerializer(data = request.POST)
        
        if form.is_valid():
            form.save()
            return HttpResponse(form, status=201)
        return HttpResponse(form, status=400)