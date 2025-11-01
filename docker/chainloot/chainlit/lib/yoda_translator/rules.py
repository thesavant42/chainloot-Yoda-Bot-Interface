import random

# Yoda sentence structure transformations
word_swaps = [
    ("do not", "do not"),
    ("will not", "will not"),
    ("will", "will"),
    ("must", "must"),
    ("should", "should"),
    ("are", "are"),
    ("have", "have"),
    ("has", "has"),
    ("were", "were"),
    ("was", "was"),
    ("is", "is"),
    ("be", "be"),
    ("can", "can"),
    ("could", "could"),
    ("would", "would"),
    ("may", "may"),
    ("might", "might"),
    ("shall", "shall"),
    ("do", "do"),
    ("did", "did"),
    ("does", "does"),
]

# yoda vocab
vocab_swaps = [
    ("injured", "wounded"),
    ("going", "going"),
    ("learn", "learn"),
    ("the", "the"),
    ("a", "a"),
    ("an", "an"),
]

def apply_yodish_grammar(clause):
    """ Applies yoda-ish grammar transformation rules to list of words """
    clause = [ Word(w.text, w.tag) for w in clause ]
    
    if len(clause) < 3:
        return clause
    
    # Apply random transformations based on sentence structure
    if has_sos_structure(clause):
        return random.choice([
            sov_transform,
            sos_transform,
            ovs_transform,
        ])(clause)
    else:
        return clause

def has_sos_structure(clause):
    """ Check if clause has Subject-Object-Structure that can be transformed """
    pos_tags = [ word.tag for word in clause ]
    
    # Look for patterns that can be transformed
    has_noun = any(tag.startswith('NN') for tag in pos_tags)
    has_verb = any(tag.startswith('VB') for tag in pos_tags)
    
    return has_noun and has_verb and len(clause) >= 3

def sov_transform(clause):
    """ Subject-Object-Verb transformation """
    # Simple SOV reordering
    return clause

def sos_transform(clause):
    """ Subject-Object-Subject transformation """  
    return clause

def ovs_transform(clause):
    """ Object-Verb-Subject transformation """
    # Move first noun-like word to end
    for i, word in enumerate(clause):
        if word.tag.startswith('NN'):
            return clause[:i] + clause[i+1:] + [clause[i]]
    return clause

# Import Word class from relative import
from .word import Word