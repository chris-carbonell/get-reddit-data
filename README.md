# Overview

<b>get-reddit-data</b> downloads submission data from a specified subreddit

# Process

1. Collect post IDs from Pushshift
2. Request submission data for each post ID using PRAW

# Quickstart

1. Create a Reddit app ([https://www.reddit.com/prefs/apps](link)) and update <code>config/praw.json</code> with the client ID, client secret, and user agent.
	* The user agent is a string of your choosing though the Reddit API has recommendations on what that string should look like.
2. Update the constants in <code>get_pushshift_data.py</code> as necessary.
	* For example, you can specify a different subreddit in line 17.
3. Collect the post IDs using <code>python -m get_pushshift_data</code>.
4. Update the constants in <code>get_praw_data.py</code> as necessary.
5. Request submission data for each post ID using <code>python -m get_praw_data.py</code>.

# Table of Contents

| Path                  | Desc                                             |
|-----------------------|--------------------------------------------------|
| config/praw.json      | connection details for Reddit API (used by PRAW) |
| helpers               | random Jupyter notebooks with helpful code       |
| get_praw_data.py      | script to request post IDs from Pushshift        |
| get_pushshift_data.py | script to request submission data using PRAW     |
| README.md             | this README                                      |
| requirements.txt      | Python requirements                              |

# Environment

* Microsoft Windows 10 Home
* Python 3.9.7

# Installation

Just install the required Python dependencies:<br>
<code>python -m pip install -r requirements.txt</code>

# Runtime

* Pushshift
In my testing, submissions were requested and lightly scrubbed from Pushshift at a rate of about 3,700 submissions per minute.
* PRAW<br>
In my testing, submissions were requested and lightly scrubbed from PRAW at a rate of just 30 submissions per minute. Therefore, I highly recommend using multiprocessing if possible.

# Why Pushshift & PRAW?

Pushshift provides the post IDs in pages (1000 at a time). Crawling PRAW for post IDs similarly is not currently possible anymore ([link]((https://stackoverflow.com/questions/53988619/praw-6-get-all-submission-of-a-subreddit))).

# Resources
* Helpful Repos
	* Similar Process<br>
	[https://github.com/iterative/aita_dataset](https://github.com/iterative/aita_dataset)
	* Great Examples of Feateure Engineering<br>
	[https://github.com/h-parker/AITA_classifier](https://github.com/h-parker/AITA_classifier)
	* Simple Model<br>
	[https://github.com/jenajeanmartine/AmITheAsshole](https://github.com/jenajeanmartine/AmITheAsshole)
* Pushshift vs PRAW<br>
[https://stackoverflow.com/questions/53988619/praw-6-get-all-submission-of-a-subreddit](https://stackoverflow.com/questions/53988619/praw-6-get-all-submission-of-a-subreddit)

# Future Enhancements

* Better Logging<br>
e.g., output to CSV so we can easily remove IDs that error out
* Multithreading<br>
Can we improve the efficiency further with multithreading?