from unicodedata import name
from django.urls import path
from .views import (
        RegisterView, 
        VerifyUserEmail,
        LoginUserView, 
        TestingAuthenticatedReq, 
        PasswordResetConfirm, 
        BusinessUserActivation,
        BusinessDetailsListCreateView,
        BusinessDetailsRetrieveUpdateDestroyView,
        PasswordResetRequestView,SetNewPasswordView, LogoutApiView)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-email/', VerifyUserEmail.as_view(), name='verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginUserView.as_view(), name='login-user'),
    path('business-users/', BusinessUserActivation.as_view(), name='business-user-list'),
    path('business-details/<int:business_id>/', BusinessDetailsRetrieveUpdateDestroyView.as_view(), name='business-details-retrieve-update-destroy'),
    path('business-details/', BusinessDetailsListCreateView.as_view(), name='business-details-list-create'),
    path('get-something/', TestingAuthenticatedReq.as_view(), name='just-for-testing'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),
    path('set-new-password/', SetNewPasswordView.as_view(), name='set-new-password'),
    path('logout/', LogoutApiView.as_view(), name='logout')
    ]