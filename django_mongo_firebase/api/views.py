from django.http import HttpResponse
from .utils import generate_unique_username, validate_credentials
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer
from .models import user_collection
import jwt
from django.views.decorators.csrf import csrf_exempt

import os
import datetime
import dotenv
dotenv.load_dotenv()


secret = os.getenv('JWT_SECRET')

def home(request):
    return HttpResponse("API is running")

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')

            # Checking if a user with the given email already exists
            existing_user = user_collection.find_one({"email": email})
            if existing_user:
                return Response({"detail": "A user with that email already exists."}, status=status.HTTP_400_BAD_REQUEST)
                        
             # Checking if a user with the given email already exists
            existing_username = user_collection.find_one({"username": username})
            if existing_username:
                return Response({"detail": "A user with that username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generating a unique username based on the email
            new_username = generate_unique_username(email)

            # Creating a new user document
            new_user = {
                "username": new_username,
                "email": email,
                "password": serializer.validated_data.get('password'),
                "first_name": serializer.validated_data.get('first_name', ''),
                "last_name": serializer.validated_data.get('last_name', ''),
            }

            # Inserting the user document into the collection
            user_collection.insert_one(new_user)

            response_data = {
                "username": new_username,
                "email": email
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Validating the username and password against MongoDB
        if validate_credentials(username, password):
            existing_user = user_collection.find_one({"username": username})
            payload = {
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expiration time
            }

            # Generating the JWT token
            custom_token = jwt.encode(payload, secret, algorithm="HS256")

            email = existing_user.get("email")

            # Returning the custom token in the response
            response_data = {
                "username": username,   
                "email": email,
                "custom_token": custom_token 
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"detail": "Username or password is invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    def get(self, request):
        try:
            id_token = request.META.get('HTTP_AUTHORIZATION').split("Bearer ")[1]
            decoded_token = jwt.decode(id_token, secret, algorithms=["HS256"])
            username = decoded_token['username']
            existing_user = user_collection.find_one({"username": username})
            profile_data = {
                    "username": username,
                    "email": existing_user.get('email'),
                    "full_name": existing_user.get("first_name")+"-"+existing_user.get("last_name")
                }
            return Response(profile_data, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired.'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileEditView(APIView):
    @csrf_exempt
    def post(self, request):
        try:
            id_token = request.META.get('HTTP_AUTHORIZATION').split("Bearer ")[1]
            decoded_token = jwt.decode(id_token, secret, algorithms=["HS256"])
            username = decoded_token['username']
            user = user_collection.find_one({"username": username})

            if user:
                first_name = request.data.get('first_name', user.get('first_name'))
                last_name = request.data.get('last_name', user.get('last_name'))
                updated_username = request.data.get('username')
                profile_data = {
                    "username": user.get('username'),
                    "email": user.get('email'),
                    "full_name": first_name+"-"+last_name
                }
                updated_data = {
                        'username': updated_username,
                        'first_name':first_name,
                        'last_name':last_name
                }
                if updated_username and updated_username != '': 

                    if user_collection.find_one({'username': updated_username}):
                        return Response({'error': 'Username already exists.'}, status=400)

                    updated_data = {
                        'username': updated_username,
                        'first_name':first_name,
                        'last_name':last_name
                    }
                else:
                    updated_data = {
                        'first_name':first_name,
                        'last_name':last_name
                    }
                user_collection.update_one({'_id': user.get('_id')}, {'$set': updated_data})
            return Response(profile_data, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Token has expired.'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_401_UNAUTHORIZED)