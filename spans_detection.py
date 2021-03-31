import preprocessing as pre
from nltk.stem.porter import *
from nltk.stem.snowball import SnowballStemmer
import sys

''' 
Checks if the piece of text contains toxic words from the list of words provided in the second argument
Arguments:
text - Single string to check for toxic words
words - List of toxic words
'''
def get_detected_toxic_words(text, words):
    detected_words = []

    for unigram in text.split():
        if unigram in words:
            detected_words.append(unigram)
            
    return detected_words
    
''' 
Extracts annotated toxic words from the dataset
Arguments:
spans - List of character offsets 
texts - List of comments
include_empty_spans - Binary flag to include empty spans in the result
'''
def get_toxic_words_from_spans(spans, texts, include_empty_spans = False):
    extracted_words = []
    sample_count = 0;

    # Extract toxic characters
    while sample_count < len(spans):
        char_count = 0
        char_index = sys.maxsize
        
        # Include empty spans
        if include_empty_spans and len(spans[sample_count]) == 0:
            extracted_words.append(' NULL ')
        
        while char_count < len(spans[sample_count]):
            if spans[sample_count][char_count] > (char_index + 1):
                extracted_words.append(' ')
            char_index = spans[sample_count][char_count]
            extracted_words.append(texts[sample_count][char_index])
            char_count += 1
        extracted_words.append('| ')
        sample_count += 1
        
    # Join characters into toxic word list
    extracted_words = ''.join(extracted_words).split('| ')
    
    while '' in extracted_words:
        extracted_words.remove('')
    extracted_words = [x.strip() for x in extracted_words]

    toxic_words_list = []
    for sentence in extracted_words:
        if sentence == "NULL":
            toxic_words_list.append([])
        else:
            toxic_words_list.append(sentence.split())
        
    return toxic_words_list

'''
Find exact position of word appearances in the comment and return those positions
Arguments:
word - word to look for in the comment
comment - comment to check for the word
'''
def find_word_in_comment(word, comment):
    needless_punctuation = [',', ' ', '.', '\'', '\"', '?', '!']
    search_idx = 0
    spans = []
  
    while comment.find(word, search_idx) != -1:
        word_idx = comment.find(word, search_idx)
        previous_ch = word_idx - 1
        next_ch = word_idx + len(word)
	
        if comment[previous_ch] in needless_punctuation or previous_ch == -1:
            if next_ch == len(comment) or comment[next_ch] in needless_punctuation:
                spans = spans + list(range(word_idx, next_ch))
        search_idx = next_ch
  
    return spans

'''
Check if the toxic word is in preprocessed comment
Arguments:
toxic_word - word to look for in the comment
comment - comment in which the word might appear
stemming - option to turn on stemming of the toxic word
'''
def check_word_in_comment_preprocessed(toxic_word, comment, stemming = False):
    if stemming:
        stemmer = PorterStemmer()
#         stemmer = SnowballStemmer('english')
        stemmed_word = stemmer.stem(toxic_word)
    
        if stemmed_word in comment.split():
           return toxic_word
        else:
           return None
    else: 
        if toxic_word in comment.split():
            return toxic_word
        else:
            return None
    
'''
Get spans of toxic word appearances from dataset of comments
Arguments:
comment_dataset - dataset of online comments
toxic_list - list of toxic words
'''
def get_spans_from_dataset(comment_dataset, toxic_list):
    result = []
    
    for sentence in comment_dataset:
        detected_spans = []
        
        preprocessed_sentence = pre.text_preprocessing(sentence)
        for word in toxic_list:
            detected_word = check_word_in_comment_preprocessed(word, preprocessed_sentence)
            if (detected_word != None):
                sentence = sentence.lower()
                detected_spans = detected_spans + find_word_in_comment(detected_word, sentence)
        
        detected_spans = sorted(set(detected_spans))
        result.append(detected_spans)
    
    return result


