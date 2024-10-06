from django.urls import path
from .views import AuthUserAPIView, UserRegistrationAPIView, UserLogoutAPIView, UserLoginAPIView, \
    PasswordResetRequestView, PasswordResetConfirmView, UserProfileView, UpdateUserActiveStatusAPIView, \
    UserListAPIView, StudentListAPIView

urlpatterns = [
    path('', AuthUserAPIView.as_view(), name='auth_user'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('register/', UserRegistrationAPIView.as_view(), name='user_registration'),
    path('update-active-status/', UpdateUserActiveStatusAPIView.as_view(), name='update_user_active_status'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('logout/', UserLogoutAPIView.as_view(), name='user_logout'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('user-list/', UserListAPIView.as_view(), name='user_list'),
    path('student-list/', StudentListAPIView.as_view(), name='student_list'),
]
