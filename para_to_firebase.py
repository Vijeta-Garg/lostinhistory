import os
import firebase_admin
from firebase_admin import credentials, db
# This builds the path relative to firebase_config.py's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cred = credentials.Certificate(os.path.join(BASE_DIR, 'serviceAccountKey.json'))

app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://lostinhistory-default-rtdb.firebaseio.com'
})
from llm_extraction import extract_nouns, extract_names

sample_dictionary = {
    1: "In 1953, James Watson and Francis Crick published their landmark paper in Nature, proposing that DNA takes the form of a double helix. Their model elegantly explained how genetic information could be stored and copied — the two strands of the helix could separate, each serving as a template for a new complementary strand. Watson and Crick's insight built upon earlier work establishing that DNA, not protein, was the carrier of genetic information. Maurice Wilkins, working at King's College London, had been studying DNA fibers using X-ray diffraction techniques, and his crystallographic data provided critical physical evidence for the helical structure. The famous \"Photo 51,\" an X-ray diffraction image of extraordinary clarity, revealed the unmistakable signature of a helix and allowed Watson and Crick to refine the dimensions of their model. For their discovery, Watson, Crick, and Wilkins shared the 1962 Nobel Prize in Physiology or Medicine.",
    2: "The discovery of nuclear fission in 1938 fundamentally transformed both physics and world history. Otto Hahn, working at the Kaiser Wilhelm Institute in Berlin, bombarded uranium atoms with neutrons and observed that the uranium nucleus had split into lighter elements — barium among them. This was a stunning result that defied existing models of nuclear physics, which had assumed that bombarding heavy nuclei with neutrons would produce only slightly lighter elements. Hahn published his radiochemical findings, and the theoretical explanation soon followed: the uranium nucleus, when struck by a neutron, could divide into two roughly equal fragments, releasing an enormous amount of energy predicted by Einstein's mass-energy equivalence. For this discovery, Otto Hahn was awarded the 1944 Nobel Prize in Chemistry. The implications were immediate and far-reaching — within seven years, nuclear fission had been harnessed for both devastating weaponry and, eventually, civilian energy production.",
    3: "For much of the early twentieth century, astronomers assumed that the Sun and other stars were composed of roughly the same mixture of elements found on Earth — primarily iron and other heavy elements. This seemed reasonable: spectroscopic analysis had revealed the presence of familiar elements in stellar atmospheres, and the prevailing view held that the cosmos was chemically homogeneous. Henry Norris Russell, one of the most influential astrophysicists of the era, championed this position throughout the 1920s. It was not until later analyses of stellar spectra and advances in quantum mechanics that the scientific community came to accept a radically different picture: stars are composed overwhelmingly of hydrogen and helium, with heavier elements present only in trace amounts. This insight was foundational — it reshaped models of stellar evolution, nucleosynthesis, and ultimately our understanding of the Big Bang and the chemical history of the universe.",
    4: "The mechanism by which biological sex is determined was a major puzzle in early genetics. By the turn of the twentieth century, advances in microscopy had revealed that cells contained distinct structures called chromosomes, and several researchers suspected that these structures played a role in heredity. Edmund Beecher Wilson and Clarence Erwin McClung were among the key figures investigating the relationship between chromosomes and sex. Working with insects, researchers observed that certain chromosome pairs differed between males and females. The identification of the X and Y chromosomes — and the demonstration that the presence or absence of a specific chromosome determined sex — was a breakthrough that connected cytology to Mendelian genetics. Thomas Hunt Morgan later expanded on this chromosomal theory of inheritance through his famous experiments with Drosophila fruit flies, establishing that genes are carried on chromosomes and founding the field of modern genetics.",
    5: "Modern wireless communication rests on a foundation of innovations stretching back over a century. Guglielmo Marconi's successful transatlantic radio transmission in 1901 proved that electromagnetic waves could carry information across vast distances without wires. In the decades that followed, engineers steadily improved radio technology, developing amplitude and frequency modulation to encode audio signals. During World War II, the challenge of secure military communication spurred new thinking about how radio signals could be made resistant to jamming and interception. The concept of spread-spectrum communication — in which a signal is broadcast across a rapidly changing sequence of frequencies rather than a single fixed frequency — emerged as a powerful solution. This technique made signals both harder to detect and more resistant to interference. Spread-spectrum principles would prove foundational to the digital wireless revolution. By the late twentieth century, these ideas had been adapted and refined into the protocols underlying modern technologies including Wi-Fi, Bluetooth, and GPS navigation systems."
}
proper_nouns = []
names = []
def get_nouns(key):
    global proper_nouns
    proper_nouns = extract_nouns(sample_dictionary[key])
def get_names(key):
    global names
    names = extract_names(sample_dictionary[key])   
def upload_to_database(key):
    get_nouns(key)
    ref = db.reference('nouns')
    ref.set(proper_nouns)
    ref = db.reference('current_paragraph')
    ref.set(key)
    print('uploaded successfully!')
def upload_names_to_database(key):
    get_names(key)
    ref = db.reference('names')
    ref.set(names)
    ref = db.reference('current_paragraph')
    ref.set(key)
    print('uploaded successfully!')
upload_to_database(2)
upload_names_to_database(2)

