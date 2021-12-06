#Text preprocessor
import os
import re
import pickle
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


#Stop words variable and initialising porter stemmer object
stop_words = stopwords.words("english")
st = PorterStemmer()

#pickle directory location & creating one if it doesn't exist.
pickle_folder = "./PickleFiles/"
os.makedirs(pickle_folder, exist_ok=True)

# Fetched pages directory to get the pages fetched by the crawler in prev step
pages_folder = "./FetchedPages/"
filenames = os.listdir(pages_folder)

#List to store all file names in the FetchedPages directory
files = []
for name in filenames:
    files.append(name)



# Function that returns True if the passed HTML element is an invisible tag
# that don't contain useful information related to search engine.
def is_visible_tag(element):
    if element.parent.name in ["style", "script", "head", "meta", "[document]"]:
        return False
    elif isinstance(element, Comment):
        return False
    elif re.match(r"[\s\r\n]+", str(element)):
        return False
    else:
        return True


# Function to extract only the visible text from the html code of each webpage
# Return value: string that contains all word tokens separated by space present
# in html code parsed by beautiful soup and is visible.
def token_string_from_page(page):
    soup = BeautifulSoup(page, "lxml")
    # return all text in page
    text_in_page = soup.find_all(text=True)
    # return only visible text
    visible_text = filter(is_visible_tag, text_in_page)
    return " ".join(term.strip() for term in visible_text)


# Inverted index to map each work token to a list of docs along with the token freq in each file.
inverted_index = {}

# Dict that maps webpage or filename to list of word tokens in that web page/file.
webpage_tokens = {}

for file in files:
    web_page = open(pages_folder + file, "r", encoding="utf-8")
    code = web_page.read()
    # Fetching visible text on webpage
    text = token_string_from_page(code)
    text = text.lower()
    # Removing all punctuations and digits
    text = re.sub("[^a-z]+", " ", text)
    tokens = text.split()
    # Stop words removal and stemming
    clean_stem_tokens = [
        st.stem(token)
        for token in tokens
        if (token not in stop_words and st.stem(token) not in stop_words)
        and len(st.stem(token)) > 2
    ]

    # Adding tokens in web page to dict webpage_tokens
    webpage_tokens[file] = clean_stem_tokens

    #inverted index of form key = stemmed_token & value = dict(key=file_name & value= freq of token in file_name)
    for token in clean_stem_tokens:
        # get frequency of token and set to 0 if token not in dict
        freq = inverted_index.setdefault(token, {}).get(file, 0)

        # add 1 to frequency of token in current webpage
        inverted_index.setdefault(token, {})[file] = freq + 1


# Pickling inverted index and web page tokens
with open(pickle_folder + "6000_inverted_index.pickle", "wb") as f:
    pickle.dump(inverted_index, f)

with open(pickle_folder + "6000_webpages_tokens.pickle", "wb") as f:
    pickle.dump(webpage_tokens, f)
