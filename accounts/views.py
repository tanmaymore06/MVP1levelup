from django.shortcuts import render

# Create your views here.

from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer


class RegisterView(APIView):
    '''API view to handle user registration.'''
    permission_classes = [AllowAny] # This allows anyone to access this view, which is necessary for user registration since new users won't have authentication tokens yet.

    def post(self, request):
        '''Handle POST requests to register a new user.'''

        serializer = RegisterSerializer(data=request.data) # serializer stores the data sent in the request and will validate it according to the rules defined in the RegisterSerializer. 
        
        if serializer.is_valid():   # If the data is valid, it will be used to create a new user.
            user = serializer.save()    # The 'save' method of the serializer will call the 'create' method defined in the RegisterSerializer, which creates a new user using the validated data.
            token, _ = Token.objects.get_or_create(user=user)   # After the user is created, we generate an authentication token for that user. The 'get_or_create' method checks if a token already exists for the user and returns it; if not, it creates a new token. This token will be used for authenticating future requests from the frontend.
            return Response({   # Response is sent back to the frontend with the token and user information. The frontend can then store this token (e.g., in local storage) and include it in the headers of future requests to authenticate the user.
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=201) # The 'Response' sents '200 OK' by default, but since we are creating a new resource (a user), it's more appropriate to return '201 Created' to indicate that the user was successfully created.
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    '''API view to handle user login.'''
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username") # 'request.data' is a dictionary-like object that contains the data sent in the POST request. We use the 'get' method to retrieve the value associated with the "username" key. If "username" is not provided in the request, 'get' will return None instead of raising an error.
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=400
            )

        user = authenticate(username=username, password=password) # The 'authenticate' function checks if the provided username and password match a user in the database. If the credentials are valid, it returns the user object; otherwise, it returns None.

        if not user:
            return Response(
                {"detail": "Invalid credentials."},
                status=401
            )

        token, _ = Token.objects.get_or_create(user=user)   # If the user is authenticated successfully, we generate (or retrieve) an authentication token for that user, just like in the registration view. This token will be used by the frontend to authenticate future requests.
        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }   # Here, the status code is not explicitly set, so it will default to '200 OK', which means, "The resource(user) is successfully retrieved and the token is generated."
        })


class LogoutView(APIView):
    '''API view to handle user logout.'''

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"detail": "Logged out successfully."})