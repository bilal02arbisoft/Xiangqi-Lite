from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.serializers import CustomUserSerializer, PasswordChangeSerializer
from django.utils import timezone
from django.contrib.sessions.models import Session
from users.models import CustomUser, Profile
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.http import JsonResponse
from rest_framework_simplejwt.views import TokenRefreshView


class UsersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUserSerializer(CustomUser.objects.all(), many=True)

        return Response(users.data)


import logging


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            data = response.data
            access_token = data.get('access')
            refresh_token = data.get('refresh')
            response = JsonResponse({'message': 'Login successful'})
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                samesite='None',
                secure=True,
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                samesite='None',
                secure=True,
            )

            return response
        except AuthenticationFailed as e:

            return Response({'error': str(e)}, status=401)


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token
            response = super().post(request, *args, **kwargs)
            new_access_token = response.data.get('access')
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                samesite='None',
                secure=True,
            )

            return response

        except Exception as e:

            return Response({'error': str(e)}, status=400)

class SignupView(APIView):
    @staticmethod
    def post(request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():

            serializer.save()
            response_data = {
                "message": "User created successfully",
                "user": serializer.data
                }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response("Logged out successfully", status=status.HTTP_205_RESET_CONTENT)
        except Exception:

            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        user = request.user
        serializer = CustomUserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def put(request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            response_data = {
                "message": "Successfully Updated the Profile",
                "Profile:": serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        profile.delete()
        user.delete()
        response_data = {"message": "User deleted successfully"}

        return Response(response_data, status=status.HTTP_204_NO_CONTENT)
class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):

        return self.request.user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            self._invalidate_user_sessions(user)

            return Response({"message": "Password has been changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _invalidate_user_sessions(user):
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        for session in sessions:
            session_data = session.get_decoded()
            if user.pk == session_data.get('_auth_user_id'):

                session.delete()


class NotFoundAPIView(APIView):
    response_data = {"message": " URL Not found"}

    def get(self, request):
        return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        return Response(self.response_data, status=status.HTTP_404_NOT_FOUND)

