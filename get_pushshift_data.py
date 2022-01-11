# dependencies

# general
import datetime
import os
import re
import time

# data
import csv
import requests
import json
import pandas as pd

# constants

target_subreddit = "amitheasshole"

path_post_id_data = "./data/post_ids.csv"
path_post_id_data_error = f"./data/{datetime.datetime.now().strftime('%Y-%m-%d %H%M')}_post_ids_error.csv"
path_reddit_data = "./data/reddit_data.csv"
path_praw_config = "./config/praw.json"

# first_epoch = 1370000000 # Right before the first post in 2012
first_epoch = 1631598076  # testing
last_epoch = round(time.time(), 0) # e.g., 1577836800 = January 1, 2020

threshold_score_minimum = 3  # score must be greater than this to get scraped

# funcs

def getPushshiftURL(subreddit, after, before):
    return f"https://api.pushshift.io/reddit/submission/search/?sort_type=created_utc&sort=asc&subreddit={subreddit}&after={str(after)}before{str(before)}size=1000"

def getPushshiftData(url):
    r = requests.get(url)
    data = json.loads(r.text)
    return data['data']

def getKeyValueSafe(d, key, default=None):
    if key in d:
        val = d[key]
        if isinstance(val, str):
            
            # clean up weird newline characters
            val_clean = re.sub(
                r"\\t|\\n|\\r",
                "",
                re.sub(
                    "\t|\n|\r",
                    "",
                    val
                )
            )
            
            return val_clean.encode("cp1252", "ignore") # encode string
        
        else:
            return val
    else:
        return default

if __name__ == "__main__":

    # set up
    ls_fields = ["id", "created_utc", "title", "full_link", "score", "num_comments", "link_flair_css_class", "link_flair_text", "over_18", "selftext"]
    after = first_epoch
    start_time = time.time()

    # loop
    ls_data = []
    counter_posts = 0
    with open(path_post_id_data, "a", newline="", encoding="cp1252") as f_data:
        
        # get writer and write header
        writer = csv.writer(f_data, quoting=csv.QUOTE_ALL)
        writer.writerow(ls_fields)
        
        # get data
        while int(after) < last_epoch:

            # get page data
            url = getPushshiftURL(target_subreddit, after, last_epoch)
            data = getPushshiftData(url)

            # check
            if len(data) == 0:
                break

            # get data for each post
            for post in data:

                # log
                counter_posts += 1
                print(f"Completed Post Count: {counter_posts-1}")  # ignore next target
                print(f"Time Elapsed (min): {round((time.time() - start_time)/60, 2)}")
                print()
                print(f"Target Post ID: {post['id']}")
                print(f"Target Post URL: {post['full_link']}")
                print(f"Target Post Created UTC: {post['created_utc']}")

                # skip posts
                if getKeyValueSafe(post, 'selftext') == "[removed]" or getKeyValueSafe(post, 'num_comments') == 0:
                    continue
                else:
                    try:
                        ls_post = [getKeyValueSafe(post, field) for field in ls_fields]
                        writer.writerow(ls_post)
                    except Exception as e:
                        # save errors for debugging
                        with open(path_post_id_data_error, "a", newline='', encoding="cp1252") as f_errors:
                            f_errors.write(", ".join([post['id'], post['title'], post['url'], str(e)]) + "\n")

            # reset
            after = post['created_utc']  # work backwards
            time.sleep(0.3)  # 0.1 hit rate limits