import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate('serviceAccountKey.json')
app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lostinhistory-default-rtdb.firebaseio.com'
})

