import functools
from word import Word

def index_tag_seq(words, seq):
    """ Return index of first occurrence of seq in words (fuzzy) """
    if len(seq) > len(words):
        return -1
    
    nouns = [ 'NN', 'NNS', 'NNP' ]
    seq = [ ('NN' if tag in nouns else tag) for tag in seq ]
    tags = [ ('NN' if w.tag in nouns else w.tag) for w in words ]

    for i in range(len(tags)):
        if tags[i:i+len(seq)] == seq:
            return i

    return -1

def move_tag_seq(words, seq, dest, punc=None):
    """ If seq present (order matters), move words to dest.
    Prepend (for 'end') or append (for 'start') with punctuation if required. """
    seq_start = index_tag_seq(words, seq)
    if seq_start > -1:
        move_words = words[seq_start:seq_start+len(seq)]
        rest = words[:seq_start] + words[seq_start+len(seq):]
        punc = [ punc ] if punc else []
        if dest == 'start':
            words = move_words + rest + punc 
        if dest == 'end':
            words = rest + punc + move_words
        return words
    return None

def replace_tag_seq(words, seq1, seq2):
    """ Move/change words matching tag sequence 1 to match sequence 2. 
        Weird things may happen if tags are duplicated in seq1/seq2 """
    seq_start = index_tag_seq(words, seq1)
    if seq_start > -1:
        pre = words[:seq_start]
        post = words[seq_start+len(seq1):]
        tag_to_word = dict([ (word.tag, word) for word in words[seq_start:seq_start + len(seq1)] ])
        new = filter(lambda x : x is not None, [ tag_to_word[x] if x in tag_to_word else None for x in seq2 ])
        return pre + list(new) + post
    return None

def rule_prp_vbp(words):
    """ You are conflicted. -> Conflicted, you are. """
    return move_tag_seq(words, ['PRP', 'VBP'], 'end', Word(',', 'punct'))


def rule_rb_jjr(words):
    """ I sense much anger in him. -> Much anger I sense in him. """
    return move_tag_seq(words, ['RB', 'JJR'], 'start')


def rule_vb_prp_nn(words):
    """ Put your weapons away. -> Away put your weapons. """
    if index_tag_seq(words, ['VB', 'PRP$', 'NNS', 'RB']) > -1:
        return move_tag_seq(words, ['VB', 'PRP$', 'NNS'], 'end')
    return None


def rule_dt_vbz(words):
    """ This is my home. -> My home this is. """
    return move_tag_seq(words, ['DT', 'VBZ'], 'end')


def rule_nn_vbz_rb_vb(words):
    """ Size does not matter. -> Size matters not. 
    Conversion of VB to VBZ is blunt at best (adding 's'). 
    Fixed: Changed from NNP to NN to match SpaCy's actual tagging of 'Size' as common noun. """
    original_len = len(words)
    words = replace_tag_seq(
        words,
        ['NN','VBZ','RB','VB'],
        ['NN','VB','RB']
    )
    if words is not None:
        if len(words) < original_len:
            i = index_tag_seq(words, ['NN', 'VB', 'RB'])
            words[i+1].text += 's'
            words[i+1].tag = 'VBZ'
    return words
    
def apply_yodish_grammar(clause):
    def apply_rule(inp, r):
        applied = r(inp)
        return (applied if applied else inp)

    rules = [
        rule_prp_vbp,
        rule_rb_jjr,
        rule_vb_prp_nn,
        rule_dt_vbz,
        rule_nn_vbz_rb_vb,
    ]
    return functools.reduce(apply_rule, rules, clause)
