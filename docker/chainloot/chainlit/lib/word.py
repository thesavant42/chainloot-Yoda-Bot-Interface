class Word:
    def __init__(self, text, tag):
        self.text = text.lower()
        self.tag = tag
        self.expand_contractions()
        self.apply_capitalization()
        
    def __str__(self):
        return self.text

    def __repr__(self):
        return self.text

    def apply_capitalization(self):
        if self.text == 'i' or self.tag == 'NNP':
            self.text = capitalize(self.text)

    def expand_contractions(self):
        """ Like contractions, Yoda does not. """
        if self.text in contractions and self.tag != "POS":
            self.text = contractions[self.text]

def capitalize(s):
    return s[0].upper() + s[1:]

contractions = {
    '\'ll' : 'will',
    '\'d' : 'would',
    '\'ve': 'have',
    '\'re': 'are',
    'n\'t' : 'not',
    '\'s' : 'is',
    '\'m' : 'am',
};


