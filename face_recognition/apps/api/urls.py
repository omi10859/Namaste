from django.urls import path

from .views import GetUserByEmailView, LoginView, GetLoggedInUser, GetUserMoodFromImageView

app_name = "api"

urlpatterns = [
    path('login/', LoginView, name="login"),
    path('get/user/by/email', GetUserByEmailView, name="get-user-by-email"),
    path('get/user/', GetLoggedInUser, name="get-logged-in-user"),
    path('get/user/mood', GetUserMoodFromImageView, name="detect-mood"),
]