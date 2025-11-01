import spacy
from text import translate_sents

nlp = spacy.load("en_core_web_sm")

def translate(text):
    """ Translate text into Yodish """
    doc = nlp(text)
    return translate_sents(doc.sents)

if __name__ == "__main__":
    # Example usage - only runs when script is executed directly
    print(translate("I sense much anger in him."))
