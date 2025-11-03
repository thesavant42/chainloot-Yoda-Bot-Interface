import spacy

try:
    spacy.require_gpu()
    print("+ spaCy is using the GPU!")
except:
    print("X spaCy is using the CPU.")
