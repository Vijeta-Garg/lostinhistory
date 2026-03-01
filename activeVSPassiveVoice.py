import firebase_admin
from firebase_admin import credentials, firestore

# Initialize
# cred = credentials.Certificate("your-service-account-key.json")
# firebase_admin.initialize_app(cred)

# db = firestore.client()

#make sure to match these id indexings later!!! 
paragraphs = {
        1: "In 1953, James Watson and Francis Crick published their landmark paper in <i>Nature</i>, proposing that DNA takes the form of a double helix. Their model elegantly explained how genetic information could be stored and copied — the two strands of the helix could separate, each serving as a template for a new complementary strand. Watson and Crick's insight built upon earlier work establishing that DNA, not protein, was the carrier of genetic information. Maurice Wilkins, working at King's College London, had been studying DNA fibers using X-ray diffraction techniques, and his crystallographic data provided critical physical evidence for the helical structure. The famous Photo 51 an X-ray diffraction image of extraordinary clarity, revealed the unmistakable signature of a helix and allowed Watson and Crick to refine the dimensions of their model. For their discovery, Watson, Crick, and Wilkins shared the 1962 Nobel Prize in Physiology or Medicine..",
        2: "This is the second section...",
        3: "Here is the conclusion...",
    }

    # # Get the current paragraph ID from Firebase --> choose ids after!!!
    # ref = db.reference("current/paragraphId")
    # current_id = ref.get()  # e.g. returns 2

    # # Use it to get the matching text
current_text_id = paragraphs.get(1, "No paragraph found")





