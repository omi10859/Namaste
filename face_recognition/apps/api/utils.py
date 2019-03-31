import boto3
import base64
import spotipy
import spotipy.util as util
from django.urls import reverse
from apps.user_data.models import Mood

class NoFaceDetectedError(Exception):
    pass

def detect_mood(img):

    client = boto3.client('rekognition', region_name='ap-south-1')

    response = client.detect_faces(
            Image = {
                'Bytes': base64.b64decode(img)
            },
            Attributes = ["ALL"]
        )
    
    if len(response['FaceDetails']) < 1:
        raise NoFaceDetectedError()

    face_main = response['FaceDetails'][0]
    face_main_width = face_main['BoundingBox']['Width']

    for r in response['FaceDetails']:
        curr_face_width = r['BoundingBox']['Width']
        if curr_face_width > face_main_width:
            face_main = r

    main_emotion = face_main['Emotions'][0]

    for e in face_main['Emotions']:
        if e['Confidence'] > main_emotion['Confidence']:
            main_emotion = e
    
    return main_emotion['Type']
    
def get_spotify_feed(user):

    credentials = spotipy.oauth2.SpotifyClientCredentials(
        client_id='2f210d19fa5e44759003f86b131c3442',
        client_secret='1d889ec80a81405390d157b1365b6579',
    )
    token = credentials.get_access_token()

    # scope = 'user_library_read'
    # url = "http://localhost:8000%s" % reverse('api:spotify-callback')
    # print(url)
    # token = util.prompt_for_user_token('thisisayush', scope,
    #     client_id='2f210d19fa5e44759003f86b131c3442',
    #     client_secret='1d889ec80a81405390d157b1365b6579',
    # )

    moods = Mood.objects.filter(user=user).order_by('-created_on')
    if len(moods) > 0:
        mood = moods[0]

    sp = spotipy.Spotify(auth=token)

    # print(sp.recommendation_genre_seeds())

    if mood.mood.lower() == "calm":
        genre = ['chill', 'road-trip', 'pop', 'summer', 'romance']
    elif mood.mood.lower() == 'happy':
        genre = ['club', 'pop', 'summer', 'road-trip', 'romance']
    elif mood.mood.lower() == 'surprised':
        genre = ['deep-house', 'hip-hop']
    elif mood.mood.lower() == 'angry':
        genre = ['metal', 'metalcore', 'rock', 'techno', 'club']
    elif mood.mood.lower() == 'confused':
        genre = ['work-out', 'chill', 'tango', 'electro']
    elif mood.mood.lower() == 'sad':
        genre = ['sad', 'sleep', 'road-trip', 'romance', 'pop']
    elif mood.mood.lower() == 'disgusted':
        genre = ['metal', 'hip-hop', 'rock', 'club']
    sp.user('ax8owefx8r3x5qa37jb85hutj')
    tracks = sp.recommendations(seed_genres=genre)

    return tracks