from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import LoginForm
from .views import *

app_name = "accounts"

urlpatterns = [
    path('login/', LoginView, name="login"),
    path('register/', UserSignupView, name="register"),
    path('logout/', LogoutView, name="logout"),
    path('checkLogin/', isUserLoggedIn, name="check-login"),
    path("forgot-password/", PasswordResetView, name="password_reset"),
    path("forgot-password/validate/<uidb64>/<token>/", PasswordResetTokenValidateView, name="password_reset_confirm"),
    path("register/activate/<uidb64>/<token>/", ActivateAccountTokenValidateView, name="activate-account"),
    path("register/resend-activation/", ResendAccountActivationView, name="resend-account-activation"),
]
