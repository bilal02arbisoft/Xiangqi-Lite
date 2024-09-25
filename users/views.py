
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.error_handling import handle_exceptions
from users.models import CustomUser, Profile
from users.serializers import CustomUserSerializer, PasswordChangeSerializer, RequestOtpSerializer, VerifyOtpSerializer


class BaseAPIView(APIView):
    """
    Base API view that includes default permission classes and error handling.
    All views inheriting from this class will automatically apply the error handling decorator.
    """
    permission_classes = [IsAuthenticated,]

class UsersListView(BaseAPIView):
    """
    View to retrieve a list of all users. Requires authentication.
    """
    TTL = 60 * 15
    @method_decorator(cache_page(TTL))
    @handle_exceptions
    def get(self, request):
        """
        Handle GET requests to list all users.
        """
        users = CustomUserSerializer(CustomUser.objects.all(), many=True)

        return Response(users.data, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView, BaseAPIView):
    """
    Custom view to handle user login and return JWT tokens.
    """
    permission_classes = []

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data
        access_token = data.get('access')
        refresh_token = data.get('refresh')

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView, BaseAPIView):
    """
    Custom view to handle refreshing JWT tokens using refresh token.
    """
    permission_classes = []

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:

          return Response({'error': 'Refresh token not provided'}, status=status.HTTP_400_BAD_REQUEST)
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

        return Response(response, status=status.HTTP_200_OK)

class SignupView(BaseAPIView):
    """
    View to handle user signup. No authentication required.
    """
    permission_classes = []
    @handle_exceptions
    def post(self, request):
        """
        Handle POST requests to create a new user.
        """
        serializer = CustomUserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                'message': 'User created successfully',
                'user': serializer.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(BaseAPIView):
    """
    View to handle user logout by blacklisting the refresh token.
    """

    @handle_exceptions
    def post(self, request):
        refresh_token = request.data['refresh']
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({'message':'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)

class UserProfileEditView(BaseAPIView):
    """
    View to handle retrieving and updating user profile. Requires authentication.
    """
    parser_classes = [MultiPartParser, FormParser]

    @handle_exceptions
    def get(self, request):
        """
        Handle GET requests to retrieve user profile.
        """
        user = request.user
        serializer = CustomUserSerializer(user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @handle_exceptions
    def put(self, request):
        """
        Handle PUT requests to update user profile.
        """
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            response_data = {
                'message': 'Successfully Updated the Profile',
                'Profile': serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(BaseAPIView):
    """
    View to handle user deletion. Requires authentication.
    """
    @handle_exceptions
    def delete(self, request):
        user = request.user
        Profile.objects.filter(user=user).delete()
        user.delete()

        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

class PasswordChangeView(BaseAPIView):
    """
    View to handle password change for authenticated users.
    """
    @handle_exceptions
    def post(self, request):
        """
        Handle POST requests to change the user's password.
        """
        user = self.request.user
        serializer = PasswordChangeSerializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response({'message': 'Password has been changed successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RequestOtpView(BaseAPIView):
    """
    View to handle sending an OTP to the user's email. Requires authentication.
    """
    @handle_exceptions
    def post(self, request, *args, **kwargs):
        user_email = {'email': request.user.email}
        serializer = RequestOtpSerializer(data=user_email)

        if serializer.is_valid():
            serializer.save()

            return Response({'message': 'OTP sent to your email successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOtpView(BaseAPIView):
    """
    View to handle OTP verification. Requires authentication.
    """
    @handle_exceptions
    def post(self, request, *args, **kwargs):
        user_email = request.user.email
        request_data = {
            'email': user_email,
            'otp': request.data.get('otp')
        }
        serializer = VerifyOtpSerializer(data=request_data)

        if serializer.is_valid():
            serializer.save()
            request.user.send_verify_email()

            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotFoundAPIView(BaseAPIView):
    """
    View to handle not found (404) errors for unsupported routes.
    """
    permission_classes = []

    @handle_exceptions
    def handle_not_found(self, request, *args, **kwargs):
        response_data = {'message': 'URL Not found'}

        return Response(response_data, status=status.HTTP_404_NOT_FOUND)

    get = handle_not_found
    post = handle_not_found
    put = handle_not_found
    delete = handle_not_found
