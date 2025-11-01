class Word:
    """ Simple word class to hold text and POS tag """
    def __init__(self, text, tag):
        self.text = text
        self.tag = tag
        
    def __str__(self):
        return self.text
        
    def __repr__(self):
        return f"Word('{self.text}', '{self.tag}')"

def capitalize(text):
    """ Capitalize first letter of text """
    if not text:
        return text
    return text[0].upper() + text[1:] if len(text) > 1 else text.upper()