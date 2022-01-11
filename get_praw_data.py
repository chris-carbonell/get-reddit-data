# dependencies

# general
import datetime
import os
import re
import sys
import time

# data
import csv
import requests
import json
import pandas as pd
import praw

# constants

path_post_id_data_base = "./data/post_ids"
path_post_id_data_error_base = f"./data/{datetime.datetime.now().strftime('%Y-%m-%d %H%M')}_post_ids_error"
path_reddit_data_base = "./data/reddit_data"

path_praw_config = "./config/praw.json"

threshold_score_minimum = 3  # score must be greater than this to get scraped
ls_ignore_selftext = ["[deleted]", "[removed]", ""]

# funcs

def getValueForCSV(val):
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

        return str(val_clean.encode("cp1252", "ignore")).strip("b\'\"") # encode string

    else:
        return val

if __name__ == "__main__":

    # get args
    file_id = sys.argv[1]  # e.g., 00, 01, 02, ...

    # assume input and output files
    path_post_id_data = f"{path_post_id_data_base}_{file_id}.csv"
    path_post_id_data_error = f"{path_post_id_data_error_base}_{file_id}.csv"
    path_reddit_data = f"{path_reddit_data_base}_{file_id}.csv"

    # get list of target ids
    with open(path_post_id_data, "r") as f_ids:
        ls_post_ids = f_ids.readlines()
    ls_post_ids = [idx.replace("\n", "") for idx in ls_post_ids]  # clean up newline character

    # get list of already scrubbed ids
    if os.path.exists(path_reddit_data):
        df_scrubbed = pd.read_csv(path_reddit_data, encoding="cp1252")
        ls_scrubbed = df_scrubbed['id'].to_list()
    else:
        ls_scrubbed = []

    # get list of ids to scrub
    ls_scrub_me = list(set(ls_post_ids).difference(set(ls_scrubbed)))

    # get PRAW config

    with open(path_praw_config) as f:
        keys = json.load(f)

    # get PRAW data
    
    start_time = time.time()

    bool_header = not os.path.exists(path_reddit_data)

    with open(path_reddit_data, "a", newline='', encoding="cp1252") as f:

        # set up output file
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        if bool_header:
            header = ["id", "url", "timestamp", "title", "selftext", "edited", "link_flair_text", "score", "num_comments", "upvote_ratio"]
            writer.writerow(header)

        # get data
        counter = 0             # total post count
        counter_success = 0     # count of posts successfully written
        counter_min = 0         # count of posts not meeting minimum score
        counter_ignore = 0      # count of posts with ignorable text
        counter_errors = 0      # count of posts that ran into an error
        for idx in ls_scrub_me:

            # counter
            counter += 1  # i.e., counter is 1-indexed

            # log
            print(f"Total Post Count: {counter}")
            print(f"Time Elapsed (min): {round((time.time() - start_time)/60, 2)}")
            print(f"Target Post ID: {idx}")
            
            # get reddit instance
            try:
                if reddit.auth.limits['remaining'] == 0:
                    reddit = praw.Reddit(client_id=keys['client_id'],
                             client_secret=keys['client_secret'],
                             user_agent=keys['user_agent'])
            except:
                reddit = praw.Reddit(client_id=keys['client_id'],
                             client_secret=keys['client_secret'],
                             user_agent=keys['user_agent'])

            # get submission
            try:
                post = reddit.submission(idx)
                score = post.score
                url = getValueForCSV(post.url)

                # log
                print(f"Target Post Link: {url}")

            except Exception as e:
                counter_errors += 1
                # save errors for debugging
                with open(path_post_id_data_error, "a", newline='', encoding="cp1252") as f_errors:
                    try:
                        f_errors.write(", ".join(["requesting", str(idx), "", url, str(e)]) + "\n")

                        # log
                        print(f"Target Post Link: {url}")
                    except:
                        f_errors.write(", ".join(["requesting", str(idx), "", "", str(e)]) + "\n")

                        # log
                        print(f"Target Post Link: none found")

                continue
            
            # log
            print(reddit.auth.limits)
            
            # get data
            if score >= threshold_score_minimum:

                selftext = getValueForCSV(post.selftext)

                # check selftext
                if selftext in ls_ignore_selftext:
                    counter_ignore += 1
                    print("Result: ignorable selftext")
                    print()
                    continue

                title = getValueForCSV(post.title)
                edited = post.edited
                num_comments = post.num_comments
                created_utc = datetime.datetime.utcfromtimestamp(post.created_utc)
                upvote_ratio = post.upvote_ratio

                link_flair_text = getValueForCSV(post.link_flair_text)
                if not link_flair_text:
                    link_flair_text = None

                line_stuff = [idx, url, created_utc, title, selftext, edited, link_flair_text, score, num_comments, upvote_ratio]
                
                # write
                try:
                    counter_success += 1
                    writer.writerow(line_stuff)
                    print("Result: successfully written")
                except Exception as e:
                    # save errors for debugging
                    counter_errors += 1
                    with open(path_post_id_data_error, "a", newline='', encoding="cp1252") as f_errors:
                        f_errors.write(", ".join(["writing", str(idx), title, url, str(e)]) + "\n")
                    print("Result: error in writing")

            else:
                counter_min += 1
                print("Result: minimum score threshold not met")

            # prep for next

            print()  # newline for log

            url = None
            created_utc = None
            title = None
            selftext = None
            edited = None
            link_flair_text = None
            score = None
            num_comments = None
            upvote_ratio = None
            line_stuff = None

            time.sleep(0.2)  # 0.1 hit rate limits

# log
print("Complete!")
print(f"Time Elapsed (min): {round((time.time() - start_time)/60, 2)}")
print()
print(f"Total Post Count: {counter} ({len(ls_scrub_me)}/{len(ls_post_ids)})")
print(f"Success: {counter_success}")
print(f"Min Thresh: {counter_min}")
print(f"Ignore: {counter_ignore}")
print(f"Errors: {counter_errors}")
print(f"Other: {counter-counter_success-counter_min-counter_ignore-counter_errors}")