import firebase_admin
from firebase_admin import credentials, firestore

# Initialize
cred = credentials.Certificate("your-service-account-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

paragraphs = {
    1: "This is the intro paragraph...",
    2: "This is the second section...",
    3: "Here is the conclusion...",
}

# Get the current paragraph ID from Firebase
ref = db.reference("current/paragraphId")
current_id = ref.get()  # e.g. returns 2

# Use it to get the matching text
current_text = paragraphs.get(current_id, "No paragraph found")
print(current_text)


