import nltk
import sys
import re

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | S Conj S | S Conj VP NP
NP -> N | N PP | N Adv | Det NP
VP -> V | VP Det NP | VP PP | V AP | V Adv | V AP NP
AP -> Det Adj NP | Det AP | Adj AP | Adj
PP -> P NP | P AP | Det P NP
"""

'''
S -> NP VP | DP NP VP | S Conj S | S Conj VP
NP -> N | N PP | AP
VP -> V | V Det NP | V PP | Adv VP | VP Adv | VP NP | VP AP
DP -> Det | Det AP
AP -> Adj | Adj AP | Adj N | Adj N PP
PP -> P | P Det | P Det AP | P N | P Det N Adv | P Det NP
'''

'''
S -> NP VP | S Conj S | S Conj VP NP
NP -> N | N PP | N Adv | Det NP
VP -> V | VP Det NP | VP PP | V AP | V Adv | V AP NP
AP -> Det Adj NP | Det AP | Adj
PP -> P NP | P AP | Det P NP
'''

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    words = nltk.word_tokenize(sentence)
    for i in range(len(words)):
        word = words[i]
        words[i] = word.lower()
        if re.search('[a-zA-Z]', words[i]) is None:
            words.pop(i)
    return words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    # chunks = list()
    # print(tree.subtrees(lambda t: t.label() == 'NP'))
    # print(tree.subtrees())
    # for subtree in tree.subtrees(lambda t: t.label() == 'NP'):
    #     chunks.append(subtree)
    # return chunks

    return [subtree for subtree in tree.subtrees(is_np_chunk)]

def is_np_chunk(tree):
    """
    Returns true if given tree is a NP chunk.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    if tree.label() == 'NP' and \
            not list(tree.subtrees(lambda t: t.label() == 'NP' and t != tree)):
        return True
    else:
        return False

if __name__ == "__main__":
    main()
