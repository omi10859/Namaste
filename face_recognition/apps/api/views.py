from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout

from apps.accounts.models import User
from apps.user_data.models import Mood
from .utils import detect_mood


from PyouPlay import get
from newsapi import NewsApiClient

def check_ajax(func):

    def inner(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("Only AJAX Requests are accepted")
        return func(request, *args, **kwargs)
    
    return inner

@check_ajax
def LoginView(request):
    email = request.POST.get('email')
    password = request.POST.get('password')

    error = None
    err_cd = None
    status = False

    if not email or not password:
        err_cd = "REQ_PARAM_MISS"
        error = "Required Parameter Missing"

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        err_cd = "UNKNOWN_USER"
        error = "Unknown User"
    
    if(authenticate(request, email=email, password=password)):
        login(request, user)
        status = True
    else:
        status = False
        err_cd = "INCORRECT_PASS"
        error = "Incorrect Password"

    if status:
        return JsonResponse({'status': True})
    
    return JsonResponse({
        'status': status,
        'error': error,
        'err_cd': err_cd
    })

@check_ajax
def GetLoggedInUser(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': False, 'err_cd': 'NOT_AUTHORIZED', 'error': "User is not authorized!"})

    data = {
        'status': True
    }

    data['data'] = {
        'id': request.user.id,
        'name': request.user.first_name,
        'email': request.user.email,
        'email_confirmed': request.user.email_confirmed,
        'authenticated': request.user.is_authenticated,
        'gender': request.user.gender
    }
    
    return JsonResponse(data)

@check_ajax
def GetUserByEmailView(request):

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'status': False, 'error': 'Parameter email missing'})

    try: 
        user = User.objects.get(email=email)
        status = True
    except User.DoesNotExist:
        user = None
        status = False

    if user:
        id = user.id
        name = user.get_full_name()
        email = user.email
        email_confirmed = user.email_confirmed
        authenticated = False

    if request.user.is_authenticated and request.user == user:
        authenticated = True
        gender = user.gender

    data = {
        'status': status
    }

    if status:
        data['data'] = {
            'id': id,
            'name': name,
            'email': email,
            'email_confirmed': email_confirmed,
            'authenticated': authenticated
        }
        if authenticated:
            data['data']['gender'] = gender
    
    return JsonResponse(data)

@check_ajax
def GetUserMoodFromImageView(request):
    
    if request.method != "POST":
        return JsonResponse({"status": False, "error": "Only POST Requests are accepted"})
    
    img = request.POST.get("image", None)
    if not img:
        return JsonResponse({"status": False, "error": "No Image Data"})
    missing_padding = len(img) % 4
    if missing_padding != 0:
        img += '='* (4 - missing_padding)

    mood = detect_mood(img)

    Mood.record_mood(request.user, mood);

    return JsonResponse({
        'status': True,
        'mood': mood
    })


@check_ajax
def YoutubesearchView(request, search):
    return get.toplinks(search)


@check_ajax
def NewsByNameView(country,search=None, category=None):

    newsapi = NewsApiClient(api_key='1e8aa2017af046b08f8db306b7c7ad70')


    top_headlines = newsapi.get_top_headlines(q=search,
                                            category=category,
                                            language='en',
                                            country=country)

    return top_headlines
