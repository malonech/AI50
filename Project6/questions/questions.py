import nltk
import sys
import os
import string
import numpy

FILE_MATCHES = 4
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    # Get list of directory titles
    corpus = os.listdir(directory)
    # Initialize return dictionary
    text_dict = dict()
    # Loop through each file in the corpus
    for text_file in corpus:
        # Get files filepath
        text_file_path = os.path.join(directory, text_file)

        # Open text into variable, read text into variable, then close text
        text = open(text_file_path, "r", encoding="latin1")
        content = text.read()
        text.close()
        # Update return dictionary with file content
        text_dict[text_file] = content
    return text_dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # if len(document) == 1:
    #     return document

    # Tokenize words in the document
    words = nltk.word_tokenize(document)

    # Loop in range of number of words
    for i in range(len(words)):
        # Get current word
        word = words[i]
        # Loop through words letters and remove punctuation
        for letter in word:
            if letter in string.punctuation:
                word = word.replace(letter, "")
        # Replace current word with the lowercase version
        words[i] = word.lower()

        # Check if word is a stopword, and mark it as removed
        if word in nltk.corpus.stopwords.words("english"):
            words[i] = "removed"
    # Loop through updated word list and remove "removed" words
    while "removed" in words:
        words.remove("removed")
    # Loop through updated word list and remove empty words (from punctuation)
    while '' in words:
        words.remove('')
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    # Get number of documents for math later
    number_documents = len(documents)
    # Initialize IDF dictionary for return
    idf = dict()
    # Initialize dictionary mapping words to how many documents they appear in
    global_word_map = dict()
    # Loop through each document
    for document in documents:
        # Initialize word list for document
        document_word_map = list()
        # Loop through words in document
        for word in documents[document]:
            # If we have seen it, skip. Don't need repeats for IDF. Else, add to document wordlist
            if word in document_word_map:
                continue
            document_word_map.append(word)
        # Loop through all the unique words in document.
        for word in document_word_map:
            # If it's in global, add 1 to document count. Otherwise, equals 1 (first occurrence)
            if word in global_word_map:
                global_word_map[word] += 1
            else:
                global_word_map[word] = 1
     # Calculate IDF for each word and update idf dictionary.
    for word in global_word_map:
        idf[word] = numpy.log(number_documents / global_word_map[word])
    #print(idf)
    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    # Initialize TF-IDF Dictionary
    tfidfs = dict()
    # Loop through words in each file
    for filename in files:
        # Initialize dictionary value as empty list
        tfidfs[filename] = list()
        # Initialize dictionary of tf value for each query word
        tf_word = dict()
        # Initialize dictionary of tfidf values  for each query word
        tfidf_word = dict()
        # Initialize tf values for each query word. If word not in file, default tf is zero
        for word in query:
            tf_word[word] = 0
        # Loop through words in file. If word is a query word, add one for frequency
        for word in files[filename]:
            if word in query:
                tf_word[word] += 1
        # Loop through query words and calculate tfidf values for query words
        for word in query:
            tfidf_word[word] = tf_word[word] * idfs[word]
        # Sum tfidf values of each query word for the document, and put in tfidf dictionary
        tfidfs[filename] = sum(tfidf_word.values())
    # Get n top sites based on tfidf values. return em
    top_results = sorted(tfidfs.keys(), key=tfidfs.get, reverse=True)[:n]
    return top_results


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    # Initialize sentence rank list to compare after full analysis of query
    sentence_rank = list()
    # Loop through all sentences to generatee list for comparison
    for sentence in sentences:
        # Initialize 3-entry list for sentence, idf count, and the query term density count
        sentence_tally = [sentence, 0, 0]
        # Loop through query words
        for word in query:
            # When word found in sentence, continue
            word_qtd = 0
            if word in sentences[sentence]:
                # Make sure word is in IDFS
                if word not in idfs:
                    continue
                # Calculate QTD of word
                word_qtd = sentences[sentence].count(word) / len(sentences[sentence])
                # Update sentence tally with word idfs count and QTD
                sentence_tally[1] += idfs[word]
                sentence_tally[2] += word_qtd
        # Add sentence to sentence rank list
        sentence_rank.append(sentence_tally)
    # Sort sentences by idfs, then by QTD for when ties exist. return n number of sentences
    top_sentence_list = sorted(sentence_rank, key=lambda t: (t[1], t[2]), reverse=True)[:n]
    # Get the sentences in ranked order for return
    return_sentences = list()
    for sentence in top_sentence_list:
        return_sentences.append(sentence[0])
    return return_sentences


if __name__ == "__main__":
    main()
