from django.urls import path

from .views import GetUserByEmailView, LoginView, GetLoggedInUser, GetUserMoodFromImageView,NewsByNameView,YoutubesearchView, GetUserPreferenceView, SaveUserPreferenceView, GetSpotifyMusicView, AuthSpotifyMusicView

app_name = "api"

urlpatterns = [
    path('login/', LoginView, name="login"),
    path('get/user/by/email', GetUserByEmailView, name="get-user-by-email"),
    path('get/user/', GetLoggedInUser, name="get-logged-in-user"),
    path('get/user/mood/', GetUserMoodFromImageView, name="detect-mood"),
    path('get/user/preference/', GetUserPreferenceView, name="get-user-preference"),
    path('save/user/preference/', SaveUserPreferenceView, name="save-user-preference"),
    path('get/videos/youtube/', YoutubesearchView, name="get-from-youtube"),
    path('get/news/', NewsByNameView, name="get-news"),
    path('get/music/spotify/', GetSpotifyMusicView, name="get-spotify"),
    path('auth/spotify/', AuthSpotifyMusicView, name="spotify-callback"),
]