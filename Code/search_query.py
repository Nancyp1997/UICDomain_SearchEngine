# Python Script to implement vector space model
import math
import os
import copy
import re
from nltk.corpus import stopwords
from collections import Counter
from nltk.stem import PorterStemmer
import pickle
from tkinter import *
from tkinter import ttk

# number of webpages indexed
N = 3580

# extracting english stop words
stop_words = stopwords.words("english")

# Initializing Porter Stemmer object
st = PorterStemmer()

# folder to store pickle files
pickle_folder = "./PickleFiles/"
os.makedirs(pickle_folder, exist_ok=True)

webpages_idf = {}
max_freq = {}
webpages_tf_idf = {}

# unloading all the pickle files
with open(pickle_folder + "6000_inverted_index.pickle", "rb") as f:
    inverted_index = pickle.load(f)

with open(pickle_folder + "6000_webpages_tokens.pickle", "rb") as f:
    webpages_tokens = pickle.load(f)

with open(pickle_folder + "6000_pages_crawled.pickle", "rb") as f:
    urls = pickle.load(f)


# function for computing idf of each token in the collection of webpages
def calc_idf(inverted_index):
    idf = {}
    for key in inverted_index.keys():
        df = len(inverted_index[key].keys())
        # calculating IDF for a token
        idf[key] = math.log2(N / df)
    return idf


# function to compute tf-idf of each token
def calc_tfidf(inverted_index):
    # making a temporary copy of the inverted index
    tf_idf = copy.deepcopy(inverted_index)
    for token in tf_idf:
        for page in tf_idf[token]:
            # calculating TF for the webpage
            tf = tf_idf[token][page] / max_freq[page]
            # calculating TF-IDF for token
            tf_idf[token][page] = tf * webpages_idf[token]
    return tf_idf


# function to calculate document vector length for a particular webpage
# params: url as a string, list of clean stemmed tokens in the url
def calc_doc_len(doc, doc_tokens):
    doc_len = 0
    for token in set(doc_tokens):
        # adding square of weight of token to document vector length
        doc_len += webpages_tf_idf[token][doc] ** 2
    doc_len = math.sqrt(doc_len)
    return doc_len


def doc_len_pages(list_of_tokens):
    doc_lens = {}
    for page in list_of_tokens:
        doc_lens[page] = calc_doc_len(page, list_of_tokens[page])
    return doc_lens


# Function to compute cosine similarity
def calc_cos_sim_scores(query, doc_lens):
    similarity_scores = {}
    query_len = 0
    query_weights = {}
    query_dict = Counter(query)

    for token in query_dict.keys():
        token_tf = query_dict[token] / query_dict.most_common(1)[0][1]
        query_weights[token] = token_tf * webpages_idf.get(token, 0)
        query_len += query_weights[token] ** 2

    query_len = math.sqrt(query_len)

    for token in query:
        token_weight = query_weights.get(token)

        if token_weight:
           
            for page in webpages_tf_idf[token].keys():
                similarity_scores[page] = similarity_scores.get(page, 0) + (
                    webpages_tf_idf[token][page] * token_weight
                )

    
    for page in similarity_scores:
        similarity_scores[page] = similarity_scores[page] / (doc_lens[page] * query_len)

    return similarity_scores



def tokenize_query(query_text):
    text = query_text.lower()
    text = re.sub("[^a-z]+", " ", text)
    tokens = text.split()
    clean_stem_tokens = [
        st.stem(token)
        for token in tokens
        if (token not in stop_words and st.stem(token) not in stop_words)
        and len(st.stem(token)) > 2
    ]
    return clean_stem_tokens


def show_relevant_pages(count, webpages):
    result=[]
    for i in range(count, count + 10):
        try:
            url_no = int(webpages[i][0])

        # executed when their are no more relevant pages to display
        except Exception as e:
            print("\nNo more results found !!")
            break

        if urls.get(url_no, None):
            print(i + 1, urls.get(url_no))
            num_append = i+1
            result.append(str(num_append)+' '+urls.get(url_no)+'\n')
    return result
    


# calculating IDF for all tokens
webpages_idf = calc_idf(inverted_index)

# finding the frequency of most frequent token in each webpage
for page in webpages_tokens:
    max_freq[page] = Counter(webpages_tokens[page]).most_common(1)[0][1]

# calculating TF-IDF for all tokens
webpages_tf_idf = calc_tfidf(inverted_index)

# calculating document vector length for all webpages
# Dict key=url value= list of clean stemmed tokens in the content of url
webpages_lens = doc_len_pages(webpages_tokens)


print("\n UIC Web Search Engine starting now..... \n")
# win= Tk()
# win.geometry("750x250")
# def display_text():
#    global entry
#    string= entry.get()
#    label.configure(text=string)
# label=Label(win, text="", font=("Courier 22 bold"))
# label.pack()


import tkinter as tk

root= tk.Tk()

canvas1 = tk.Canvas(root, width = 400, height = 400,  relief = 'raised')
canvas1.pack()

label1 = tk.Label(root, text='UIC search engine')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label1)

label2 = tk.Label(root, text='Type your query:')
label2.config(font=('helvetica', 10))
canvas1.create_window(200, 100, window=label2)

entry1 = tk.Entry (root) 
canvas1.create_window(200, 140, window=entry1)
cnt =0

def passtoOtherFunction ():
    
    user_entered_query = entry1.get()
    
    label3 = tk.Label(root, text= 'Loading results for' + user_entered_query + '.....\n',font=('helvetica', 10))
    canvas1.create_window(200, 210, window=label3)
    label4 = tk.Label(root, text= 'Results: ' ,font=('helvetica', 10, 'bold'))
    canvas1.create_window(200, 230, window=label4)
    label4['text']=''
    query_tokens = tokenize_query(user_entered_query)
    query_sim_pages = calc_cos_sim_scores(query_tokens, webpages_lens)
    most_relevant_pages = sorted(query_sim_pages.items(), key=lambda x: x[1], reverse=True)
    yes = {"y", "yes"}

    count = 0
    toDisplay = show_relevant_pages(count, most_relevant_pages)
    for eachUrl in toDisplay:
        label4['text'] += eachUrl
    if(len(toDisplay)<10):
        #No more results to display
        label4['text'] += '...No more results to display....'        
    else:
        label4['text'] += '\n...DisplayMore results available. Search again....'
    
            
button1 = ttk.Button(text='Search', command=passtoOtherFunction).pack(pady=20)
canvas1.create_window(200, 180, window=button1)    

root.mainloop()


