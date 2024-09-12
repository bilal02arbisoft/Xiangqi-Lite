from django.urls import path

from users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    PasswordChangeView,
    ProfileView,
    RequestOtpView,
    SignupView,
    UserDeleteView,
    UserProfileEditView,
    UsersListView,
    VerifyOtpView,
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password_change/', PasswordChangeView.as_view(), name='password-change'),
    path('users/', UsersListView.as_view(), name='users'),
    path('profile/', UserProfileEditView.as_view(), name='profile'),
    path('delete/', UserDeleteView.as_view(), name='delete'),
    path('requestotp/', RequestOtpView.as_view(), name='requestotp'),
    path('verifyotp/', VerifyOtpView.as_view(), name='verifyotp'),
    path('details/<int:user_id>/', ProfileView.as_view(), name='user_profile'),
]
