#CRAWLER
import os
import pickle
import requests
from bs4 import BeautifulSoup
from collections import deque


domain = "uic.edu"
crawl_limit = 3580
start_url = "https://www.cs.uic.edu"
pages_folder = "./FetchedPages/" #Store all the visited URL's html content
extensions_to_ignore = [
    ".pdf", ".doc", ".docx",
    ".ppt", ".pptx", ".xls",
    ".xlsx", ".css", ".js",
    ".aspx", ".png", ".jpg",
    ".jpeg", ".gif", ".svg",
    ".ico",".mp4", ".avi", ".tar",".gz",".tgz",".zip",]

#Creating error log
error_file = "error_log.txt"
f = open(error_file, "w+")
f.close()

#Queue to store start URL and all outlinks from a given URL during BFS
url_queue = deque()
url_queue.append(start_url)

# List to store URLs found during BFS at any crawled URL
urls_found = []
urls_found.append(start_url)

# Dict to keep track of order in which URLs are crawled and to store later
# on in pickle file to avoid repeated crawling.
pages_crawled = {}
page_index = 0

#Running BFS till url_queue is not empty
while url_queue:

    try:
        # Poll URL from the queue
        url = url_queue.popleft()
        rqst = requests.get(url,verify=False)
        
        if rqst.status_code == 200:
            soup = BeautifulSoup(rqst.text, "lxml")
            tags_extracted = soup.find_all("a")

            if len(tags_extracted) != 0:
                pages_crawled[page_index] = url
                output_file = pages_folder + str(page_index)

                # create file to store html code
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, "w", encoding="utf-8") as file:
                    file.write(rqst.text)
                file.close()

                #Searching for outlinks and storing them
                for tag in tags_extracted:

                    link = tag.get("href")

                    if (
                        link is not None
                        and link.startswith("http")
                        and not any(ext in link.lower() for ext in extensions_to_ignore)
                    ):

                        link = link.lower()
                        # removing intra page anchor tags from URL
                        link = link.split("#")[0]
                        # removing query parameters from URL
                        link = link.split("?", maxsplit=1)[0]
                        # removing trailing / from URL
                        link = link.rstrip("/")
                        link = link.strip()

                        #Avoiding duplicates
                        if link not in urls_found and domain in link:
                            # valid URL to append to the queue
                            url_queue.append(link)
                            urls_found.append(link)
                print('No of pages crawled: ',len(pages_crawled))
                #Stop crawling once limit is reached
                if len(pages_crawled) > crawl_limit:
                    break

                page_index += 1

    except Exception as e:
        # add error message to error log
        with open(error_file, "a+") as log:
            log.write(f"Could not connect to {url}")
            log.write(f"\nError occurred: {e}\n\n")
        log.close()

        print("Could not connect to ", url)
        print("Error occurred: ", e, " \n")
        continue


# Creating folder to store pickle files
pickle_folder = "./PickleFiles/"
os.makedirs(pickle_folder, exist_ok=True)

# Pickling the dict of crawled pages
with open(pickle_folder + "6000_pages_crawled.pickle", "wb") as f:
    pickle.dump(pages_crawled, f)
