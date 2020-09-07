"""
Filename: sgeorge_authorship_part2.py
Author: Samuel George
Date Created: 11/24/18
Date Modified: 12/1/18
Python Version: 3.6.6
"""
import os
import re
import sys
import csv
import platform
import nltk
from nltk.book import FreqDist
from nltk.corpus import gutenberg

'''
-------------------------
Helpers
-------------------------
'''

def cleanup(dirty_words):
    '''
    set all words to lower case.
    '''
    clean_words = [w.lower() for w in dirty_words if w not in '.,-?!\'"\\']
    return clean_words
'''
-------------------------
Features
-------------------------
'''
def avg_word_len(words):
    '''
    compute the average length of words in the text.
    '''
    num_chars = 0

    for word in words:
        num_chars += len(word)

    return num_chars / len(words)

def lexical_div(words):
    '''
    (aka TTL) compute the lexical diversity for a file in
    the gutenberg corpus.
    '''
    # divide the number of words used in the text
    # by the total number of words
    cleaned = cleanup(words)
    n_words = len(cleaned)
    n_vocab = len(set(cleaned))
    l_div = n_vocab / n_words
    return l_div

def hapax_legomana_ratio(words):
    '''
    compute the hapax legomana ratio for a file
    in the gutenberg corpus.
    '''
    # use the Frequency Distribution Hapax function to retrieve
    # hapaxes and divide the result by the number of words in a text.
    n_hapaxes = len(FreqDist(words).hapaxes())
    n_words = len(words)
    return  n_hapaxes / n_words

def avg_sent_len(words, sentences):
    '''
    compute the average number of words per sentence for a file.
    '''
    value = 0
    for sentence in sentences:
        value += len(sentence)
    return value / len(sentences)

def average_sentence_complexity(sents):
    '''
    compute the phrases per sentence for a file
    in the gutenberg corpus.
    '''
    # retrieve all sents from text indicated by fileid.
    # count 'phrases' by splitting on :, ;, and , in a
    # joined list of sents
    phrase_count = 0
    for sent in sents:
        phrase_count += len(re.split('[:;,]', ' '.join(sent)))
    return phrase_count / len(sents)


'''
--------------------------
Compare Signatures
--------------------------
'''

def compute_signature(words, sentences, author):
    '''
    Compute each linguistic feature and append it to a list
    return the list
    '''
    sig = [author]
    sig.append(avg_word_len(words))
    sig.append(lexical_div(words))
    sig.append(hapax_legomana_ratio(words))
    sig.append(avg_sent_len(words, sentences))
    sig.append(average_sentence_complexity(sentences))
    return sig

def compare_signatures(sig1, sig2, weights):
    '''Return a non-negative real number indicating the similarity of two
    linguistic signatures. The smaller the number the more similar the
    signatures. Zero indicates identical signatures.
    sig1 and sig2 are 6 element lists with the following elements
    0  : author name (a string)
    1  : average word length (float)
    2  : lexical diversity (float)
    3  : Hapax Legomana Ratio (float)
    4  : average sentence length (float)
    5  : average sentence complexity (float)
    weight is a list of multiplicative weights to apply to each
    linguistic feature. weight[0] is ignored.
    '''

    n_fields = len(sig1)
    score = 0.0
    # compare passed signatures using provided formula
    for i in range(1, n_fields):
        #if ('austen' in sig1[0].lower() or 'chesterton' in sig1[0].lower()) and '6a' in sig2[0]:
            #print(str(i) + ':', abs(sig1[i] - sig2[i]) * weights[i - 1])
        score += abs(sig1[i] - sig2[i]) * weights[i - 1]

    return score

'''
--------------------------
Reading and Writing files
--------------------------
'''

def write_signatures(sig_list, o_filename):
    '''
    writes all features and matches to a .csv file titled author_signatures.csv.
    '''
    # find the os and select desktop or user directory and add/ open file indicated by filename
    if platform.system() == "Windows":
        csv_file = open(os.path.join(os.environ["HOMEPATH"], "Desktop/" + o_filename), mode='w')
    elif platform.system() == "Linux":
        csv_file = open(os.path.join(os.environ["HOME"], o_filename), mode='w')
    # initialize csv writer
    sig_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    # write features to csv
    sig_writer.writerow(["FILE", "AVG WORD LENGTH", "LEXICAL DIVERSITY", "HAPAX RATIO", "AVG SENTENCE LENGTH",
                         "AVG SENTENCE COMPLEXITY"])
    for sig in sig_list:
        sig_writer.writerow([sig[0], round(sig[1], 4), round(sig[2], 4), round(sig[3], 4), round(sig[4], 4), round(sig[5], 4)])

def read_signatures(in_filename):
    try:
        read = []
        # find the os and select desktop or user directory and add/ open file indicated by filename
        if platform.system() == "Windows":
            with open(os.path.join(os.environ["HOMEPATH"], "Desktop/" + in_filename), mode='r') as csv_file:
                sig_reader = csv.reader(csv_file, delimiter=',')
                for row in sig_reader:
                    if row != []:
                        sig = []
                        if 'FILE' not in row[0] and 'mystery' not in row[0]: # ensure field titles and mystery files are not included
                            for value in row:
                                try:
                                    sig.append(float(value))
                                except:
                                    sig.append(value)
                            read.append(sig)
        elif platform.system() == "Linux":
            with open(os.path.join(os.environ["HOME"], in_filename), mode='r') as csv_file:
                sig_reader = csv.reader(csv_file, delimiter=',')
                for row in sig_reader:
                    print(row)
        return read
    except:
        print("File", in_filename, "not found.")
        return []

def read_text(in_filename):
    try:
        f_in = open(file, encoding='utf8')
        raw = f_in.read()
        f_in.close()
    except:
        print('failed to open:', in_filename)
        return ''
    return raw


'''
--------------------------
Printing the output
--------------------------
'''

def print_sig_table(sig_list):
    '''
    print all known author signatures
    '''
    print('list of reference signatures')
    print('{:<25}{:<15}{:<15}{:<15}{:<15}{:<15}'.format("Author", "Avg Word Len", "Lexical Div", "Hapax Ratio", "Avg Sent Len", "Avg Sent Comp"))
    for sig in sig_list:
        print('{:<25}{:<15}{:<15}{:<15}{:<15}{:<15}'.format(sig[0], round(sig[1], 4), round(sig[2], 4), round(sig[3], 4), round(sig[4], 4), round(sig[5], 4)))

def print_scores(sig_list, m_sig_list, weights):
    '''
    
    '''
    print('\ntable of scores\n')
    for m_sig in m_sig_list:
        scores = dict()
        print("Scores for:", m_sig[0])
        for sig in sig_list:
            if 'mystery' not in sig[0] or 'mystery' not in m_sig[0]:
                print('{:<25}{:<15}'.format(sig[0], round(compare_signatures(sig, m_sig, weights), 4)))
                # assign score results to dictionary with score as key and known author as the value
                scores[round(compare_signatures(sig, m_sig, weights), 4)] = sig[0]
        print("\nClosest Match:", scores[min(scores.keys())].split('-')[0].upper(), "with score:", str(min(scores.keys())) + ".\n")

'''
-------------------------
main
-------------------------
'''
if __name__ == '__main__':
    passed_files = []
    external = False
    # Check for passed filenames if external execution
    if(len(sys.argv) > 1):
        external = True
        print(len(sys.argv), external)
        for arg in sys.argv:
            if 'mystery' in arg:
                passed_files.append(arg)
                print(arg)

    # DO NOT CHANGE THESE WEIGHTS
    weights = [3, 0.001, 18.5, 0.09, 0.375]
    sig_list = []
    sig_list = read_signatures('test.csv')
    if sig_list == []:
        print("\nManually calculating signatures\n")
        fileids = gutenberg.fileids()
        for fid in fileids:
            # compute features, make a list of features
            words = gutenberg.words(fid)
            sents = gutenberg.sents(fid)
            signature = compute_signature(words, sents, fid)
            sig_list.append(signature)
    print_sig_table(sig_list)
    write_signatures(sig_list, 'test.csv')
    n_files = -1
    if external is False:
        while n_files < 0:
            try:
                n_files = int(input('Enter number of mystery files: '))
            except:
                print("Enter integer greater than 0.")
                n_files = -1
    elif external is True:
        n_files = len(passed_files)
    m_sig_list = []
    for f in range(n_files):
        file = ''
        if external is False:
            while not os.path.isfile(file):
                try:
                    filename = input('enter name of mystery file: ')
                    path = 'corpora/gutenberg/' + filename
                    file = nltk.data.find(path)
                except:
                    file = ''
                    print('File not found')
        elif external is True:
            print(f, passed_files[f])
            # In this case isfile condition is checked in external program
            filename = passed_files[f]
            path = 'corpora/gutenberg/' + filename
            file = nltk.data.find(path)
        raw_text = read_text(file)

        m_words = gutenberg.words(filename)
        m_sents = gutenberg.sents(filename)
        m_sig = compute_signature(m_words, m_sents, filename)
        m_sig_list.append(m_sig)
    print_scores(sig_list, m_sig_list, weights)
