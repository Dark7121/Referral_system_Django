from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000

def check_referral_code(referral_id):
    user_with_referral = CustomUser.objects.filter(referral_code=referral_id).first()
    if user_with_referral:
        return user_with_referral
    else:
        return Response({"Error": "Invalid Referral ID"}, status=status.HTTP_400_BAD_REQUEST)

def get_users_referred_by_referral_code(request, user_id):
    try:
        current_user = CustomUser.objects.get(user_id=user_id)
        user_referral_code = current_user.referral_code
        users = CustomUser.objects.filter(referral_id=user_referral_code)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({"Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register_user(request):
    data = request.data.copy()
    data['request_type'] = 'register'
    serializer = UserSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        try:
            user = serializer.save()
            referral_id = data.get('referral_id')
            if referral_id:
                referred_by_user = check_referral_code(referral_id)
                if referred_by_user:
                    referred_by_user.points += 1
                    referred_by_user.save()
            return Response({"user_id": user.user_id, "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    token = request.data.get('token')
    user = CustomUser.objects.get(email=email)
    if password==user.password:
        return Response({"token": user.token, "referral_code": user.referral_code, "user_id": user.user_id, "message": "Login successful"}, status=status.HTTP_200_OK)
    else:
        return Response({"Error": "Inavlid Password"}, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['GET'])
def user_details(request, user_id, token):
    user = get_object_or_404(CustomUser, user_id=user_id)
    token = user.token
    serializer = UserSerializer(user)
    if serializer:
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def referrals(request, user_id, token):
    user = CustomUser.objects.get(user_id=user_id)
    token = user.token
    return get_users_referred_by_referral_code(request, user.user_id)
