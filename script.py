import nltk
from nltk.util import ngrams
from nltk.stem import LancasterStemmer
import gensim.utils
import re
import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import json

known_degrees = ['b.arch', 'b.a', 'b.a.m.s', 'b.b.a', 
    'b.com', 'b.c.a', 'b.d.s', 'b.d', 'b.des', 
    'b.e', 'b.tech', 'm.e', 'm.tech', 'm.s', 'm.phil'  
]

similar_known_degrees = []

for known_degree in known_degrees:
    if '.' in known_degree :
        similar_known_degrees.append(known_degree.replace('.', '. '))         

known_degrees = known_degrees + similar_known_degrees

known_colleges = [' iit ', ' vit ', ' bits ', ' nit ']

other_known_educational_words = ['CBSE', 'SSE', 'university', 'master of', 
    'bachelor of', 'gradudate', 'institute', 'of technology', 
    'school', 'college', '%'
]

all_known_education_words = known_degrees + known_colleges + other_known_educational_words

lancaster = LancasterStemmer()

class TextMiner:

    def mine_links(self, resume, sentence): 
        for word in sentence.split() : 
            if 'http:' in word or 'https:' in word or 'www.' in word:            
                resume._links(word) 
        return resume

    def mine_email_addresses(self, resume):
        r = re.compile(r'[\w\.-]+@[\w\.-]+')
        addresses = r.findall(resume.plain_text)
        # remove duplicates
        resume._email(list(set(addresses))) 
        return resume

    def mine_phone_number(self, resume):
        r = re.compile(r'\+?\d[\d -]{8,12}\d')
        phone_numbers = r.findall(resume.plain_text)
        # remove duplicates
        resume._contact(list(set(phone_numbers)))
        return resume

    def mine(self, resume):
        self.mine_email_addresses(resume)
        # mine phone number
        self.mine_phone_number(resume)
        # tokenize sentences
        sentences = sent_tokenize(resume.plain_text)
        for sentence in sentences:
            self.mine_links(resume, sentence)
            # tokenize words
            words = nltk.word_tokenize(sentence)
            # remove stop words
            words = [word for word in words if not word in stop_words]
            self.mine_certifications_and_experience(resume, sentence, words)
            self.mine_education(resume, sentence, words)

            #  Using a Tagger. Which is part-of-speech
            # tagger or POS-tagger.
            tagged = nltk.pos_tag(words)
            # print(str(tagged) + "\n*******")  

    def mine_education(self, resume, sentence, words_in_sentence): 
        for line in sentence.lower().splitlines():
            for term in all_known_education_words :
                if term in line :
                    resume._education(line.strip())

    def mine_certifications_and_experience(self, resume, sentence, words_in_sentence):
        word_index = 0
        for word in words_in_sentence :
            word_index = word_index + 1
            stemmed = lancaster.stem(word)
            if stemmed == "cert":    
                hashtags = self.hashtags_from_ngram(words_in_sentence, word, 3)
                resume._certificates(hashtags)  
            elif stemmed == "award":        
                hashtags = self.hashtags_from_ngram(words_in_sentence, word, 4)
                resume._awards(hashtags)
            elif (stemmed == "expery" or stemmed == 'exp') and 'years' in sentence.lower():    
                resume._experience(self.mine_experience_line(sentence))
        return resume        

    def mine_experience_line(self, sentence):
        line = sentence
        for line in sentence.lower().splitlines():
            if 'years' in line :
                return line
        return line

    def hashtags_from_ngram(self, words, keyword, n):
        all_ngrams = ngrams(words, n)
        ngrams_of_keyword = [ngram for ngram in all_ngrams if keyword in ngram]
        hashtags = []
        for ngram_tuple in ngrams_of_keyword :
            hashtag = ''.join(ngram_tuple)
            # Remove special characters
            hashtag = "#" + re.sub('[^a-zA-Z0-9 \n\.]', '', hashtag)    
            hashtags.append(hashtag)
        return hashtags
    

class Resume :
    def __init__(self, directory_path, filename):
        self.directory_path = directory_path
        self.filename = filename
        self.plain_text = open(directory_path + filename, "r").read()
        self.certifications  = []
        self.email_addresses = []
        self.contact_numbers  = []
        self.awards_and_recogitions = []
        self.experience = []
        self.career = []
        self.education = []
        self.links = []

    def _certificates(self, certifications):
        self.certifications = self.certifications + certifications

    def _email(self, addresses):
        self.email_addresses = self.email_addresses + addresses

    def _contact(self, contact_numbers):
        self.contact_numbers = self.contact_numbers + contact_numbers

    def _awards(self, awards):
        self.awards_and_recogitions = self.awards_and_recogitions + awards    

    def _experience(self, experience):
        if experience not in self.experience:
            self.experience.append(experience) 

    def _education(self, education): 
        self.education.append(education)

    def _links(self, link):
        if link not in self.links:
            self.links.append(link)

    def json(self):
        summary = {
            'filename'                  : self.filename, 
            'email_addresses'           : self.email_addresses,
            'contact_numbers'           : self.contact_numbers,
            'certifications'            : self.certifications,
            'awards_and_recogitions'    : self.awards_and_recogitions,
            'experience'                : self.experience, 
            'education'                 : self.education,
            'links'                     : self.links
        }
        return json.dumps(summary, indent=4, sort_keys=True)

    def log(self):
        print(self.filename)
        print("\tEMAIL ADDRESSES       = " + str(self.email_addresses))
        print("\tCONTACT NUMBERS       = " + str(self.contact_numbers))    
        print("\tCERTIFICATIONS        = " + str(self.certifications))    
        print("\tAWARDS & RECOGNITION  = " + str(self.awards_and_recogitions))    
        print("\tEXPERIENCE            = " + str(self.experience))    
        print("\tEDUCATION             = " + str(self.education))    
        print("\tLINKS                 = " + str(self.links))    

def process_folder(directory_path):
    miner = TextMiner()
    for filename in os.listdir(directory_path) :
        resume = Resume(directory_path, filename)
        miner.mine(resume)
        #preProcess(resume.plain_text)
        print(resume.json())


def intersection(first_list, second_list): 
    return list(set(first_list) & set(second_list))    

def preProcess(plain_text):
    result=[]
    for token in gensim.utils.simple_preprocess(plain_text) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(token)
    print(result)

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

# Tokenize and lemmatize
def preprocess(text):
    result=[]
    for token in gensim.utils.simple_preprocess(text) :
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))

    return result


if __name__ == '__main__':
    stop_words = set(stopwords.words('english'))
    inputs = "/Users/vamsie/Downloads/resumes/inputs/"
    process_folder(inputs)
    #plain_text = open(inputs + "AvnishChouhan[4_3].txt", "r").read()
    #print(extract_email_addresses(plain_text))
    #print(extract_phone_number(plain_text))
    
