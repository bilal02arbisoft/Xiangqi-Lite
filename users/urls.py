from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from users.views import (SignupView, LogoutView,
                         UserProfileEditView, PasswordChangeView,
                         UsersListView, UserDeleteView, CustomTokenObtainPairView)


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password_change/', PasswordChangeView.as_view(), name='password-change'),
    path('users/', UsersListView.as_view(), name='users'),
    path('profile/', UserProfileEditView.as_view(), name='profile'),
    path('delete/', UserDeleteView.as_view(), name='delete'),

]
