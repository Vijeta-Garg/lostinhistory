import os
import firebase_admin
from firebase_admin import credentials, db
# This builds the path relative to firebase_config.py's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred = credentials.Certificate(os.path.join(BASE_DIR, 'serviceAccountKey.json'))

app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lostinhistory-default-rtdb.firebaseio.com'
})
from llm_extraction import extract_nouns, extract_names, extract_women

proper_nouns = []
names = []
women =[]
def get_nouns(text):
    global proper_nouns
    proper_nouns = extract_nouns(text)
def get_names(text):
    global names
    names = extract_names(text)   
def get_women(text):
    global women
    women = extract_women(text)
    
# def upload_to_database(text):
#     get_nouns(text)
#     ref = db.reference('nouns')
#     ref.set(proper_nouns)
#     print('uploaded successfully!')
    
# def upload_names_to_database(text):
#     get_names(text)
#     ref = db.reference('names')
#     ref.set(names)
#     print('uploaded successfully!')

# def upload_women(text):
#     get_women(text)
#     ref = db.reference('women')
#     ref.set(women)
#     print('uploaded successfully')
    
def listener(event):
    data = event.data
    if data and isinstance(data, str):
        get_names(data)
        get_nouns(data)
        get_women(data)
        db.reference('paragraphs').push({
            'names': names,
            'nouns': proper_nouns,
            'women': women
        })
        print('uploaded successfully!')
ref = db.reference("current_paragraph")
ref.listen(listener)