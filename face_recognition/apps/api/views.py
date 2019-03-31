import random
import pafy

from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout

from apps.accounts.models import User
from apps.user_data.models import Mood, UserMeta
from .utils import detect_mood, get_spotify_feed


from PyouPlay import get as get_videos
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
    score = Mood.guess_health(request.user)

    return JsonResponse({
        'status': True,
        'mood': {
            'mood': mood,
            'health_score': score
        }
    })


@check_ajax
def YoutubesearchView(request):
    # search = request.GET.get('search', None)
    search = 'general'
    categories = UserMeta.get_key(request.user, 'categories')
    videos = []
    if categories:
        categories = categories.value.split(',')
        videos_l = []
        if len(categories) > 0: 
            for x in categories:
                yt = get_videos.toplinks(x)
                if len(yt) > 2:
                    yt = yt[1:]
                for y in yt:
                    if "/channel/" in y:
                        continue
                    videos_l.append(y)
        random.shuffle(videos_l)
        videos_l = videos_l[:5]
        for url in videos_l:
            print(url)
            v = pafy.new(url)
            videos.append({
                'url': url,
                'title': v.title,
                'description': v.description
            })
    else:
        yt = get_videos.toplinks(search)
        for url in yt:
            v = pafy.new(url)
            videos.append({
                'url': url,
                'title': v.title,
                'description': v.description
            })

    return JsonResponse({
        'status': True,
        'data': videos
    })

# @check_ajax
def NewsByNameView(request):
    country = 'in'
    search = ''
    category = 'general' 

    categories = UserMeta.get_key(request.user, 'categories')
    newsapi = NewsApiClient(api_key='1e8aa2017af046b08f8db306b7c7ad70')
    news = []
    if categories:
        categories = categories.value.split(',')
        if len(categories) > 0: 
            for x in categories:
                if x == 'music':
                    x = 'entertainment'
                n = newsapi.get_top_headlines(
                    q=search,
                    category=x,
                    language='en',
                    country=country
                )
                if n['status'] == 'ok' and 'articles' in n:
                    for n2 in n['articles']:
                        news.append(n2)
        random.shuffle(news)
        news = news[:10]
    else:
        n = newsapi.get_top_headlines(
            q=search, category=category, 
            language='en', country=country
        )
        if n['status'] == 'ok' and 'articles' in n:
            for n2 in n['articles']:
                news.append(n2)
    
    return JsonResponse({
        'status': True,
        'data': news
    })

@check_ajax
def SaveUserPreferenceView(request):

    key = request.GET.get('key')
    value = request.GET.get('value')

    status = False
    key_obj = UserMeta.get_key(request.user, key)
    if key_obj:
        key_obj.value = value
        key_obj.save()
        status = True
    else:
        if UserMeta.save_key(request.user, key, value):
            status = True

    return JsonResponse({
        'status': status
    })

@check_ajax
def GetUserPreferenceView(request):

    keys = UserMeta.get_keys_for_user(request.user)
    data = {}
    for x in keys:
        data[x.key] = x.value
    
    return JsonResponse({
        'status': True,
        'data': data
    })

def GetSpotifyMusicView(request):

    return JsonResponse({'status': True, 'data': get_spotify_feed(request.user)})

def AuthSpotifyMusicView(request):

    return JsonResponse({
        'headers': dict(request.headers),
        'get': dict(request.GET),
        'post': dic(request.POST)
    })