from rules import apply_yodish_grammar
from word import Word, capitalize

punctuation = [u',', u'.', u';', u'?', u'!', u':']
stop_punctuation = [ u'.', u'!', u'?' ]

def translate_sents(text):
    """ Applies translation rules to some spacy-processed text """
    result = [
        [ apply_yodish_grammar(clause_chunk)
          for clause_chunk in split_clauses(clause)
        ]
        for clause in text
    ]
    return serialize(flatten(result))

def flatten(text):
    """Turns text (which contains clauses which contain clause chunks which contain
words) into a flattened list of words
    """
    return [
        word
        for clause in text
        for clause_chunk in clause
        for word in clause_chunk
    ]

def split_clauses(clause):
    """ Attempt to roughly split spacy-interpreted clauses into a "clause chunk"
(targets for our yodish-translation rules """
    output = []
    curr = []
    def save_to_output(chunk):
        if chunk != []:
            output.append(chunk)
        
    for token in clause:
        if token.dep_ == u'cc' or (token.dep_ == u'punct' and token.text in punctuation):
            save_to_output(curr)
            save_to_output([ Word(token.text, token.tag_)])
            curr = []
        else:
            curr.append(Word(token.text, token.tag_))

    save_to_output(curr)
    return output


def serialize(words):
    """ Turn a list of words into a string sentence with "standard" formatting and capitalization conventions
    """
    string = []
    for (i, word) in enumerate(words):
        if (i > 0 and word.text in punctuation) or word.tag == "POS":
            string[-1] = string[-1] + word.text
        elif (i > 0 and words[i - 1].text in stop_punctuation):
            string.append(capitalize(word.text))
        else:
            string.append(word.text)
            
    return capitalize(" ".join(string))
