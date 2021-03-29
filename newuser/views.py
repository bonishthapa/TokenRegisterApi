from django.shortcuts import render
from .models import NewUser
import jwt
from django.conf import Settings, settings
from django.contrib import auth
from rest_framework import generics, status
from rest_framework.response import Response
from .utils import Util
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .serializers import UserSerializer

# Create your views here.

class RegisterView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self,request):
        user = request.data
        serializer  = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        user = NewUser.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token
        relativeLink = reverse('email-verify')
        current_site = get_current_site(request).domain
        absurl = 'http://'+current_site+relativeLink+"?token="+str(token)
        email_body = 'hi '+user.username+' Use link below\n' +absurl
        data ={
            'email_body': email_body,
            'email_subject':'Verify Your Email',
            'to_email':user.email
        }
        Util.send_email(data)

        return Response(user_data,status=status.HTTP_201_CREATED)

class Verify_Email(generics.GenericAPIView):
    def get(self,request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token,settings.SECRET_KEY,algorithms=['HS256'])
            user = NewUser.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({'email':'Successfully verified email'},status=status.HTTP_201_CREATED)
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'token expired'},status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invalid Token'},status=status.HTTP_400_BAD_REQUEST)




class LoginView(generics.GenericAPIView):

    def post(self,request):
        data = request.data
        username = data.get('username','')
        password = data.get('password','')
        user = auth.authenticate(username=username,password=password)

        if user:
            auth_token = jwt.encode(
                {'username':user.username}, settings.JWT_SECRET_KEY)

            serializer = UserSerializer(user, many=True)

            data={
                'user':serializer.data,
                'token':auth_token
            }

            return Response(data,status=status.HTTP_200_OK)

        return Response({'detail':'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
