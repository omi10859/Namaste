import boto3
import base64

class NoFaceDetectedError(Exception):
    pass

def detect_mood(img):

    client = boto3.client('rekognition')

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
    
