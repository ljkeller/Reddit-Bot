import praw
from praw import Reddit
import time
import os

import config


def bot_login():
    r: Reddit = praw.Reddit(username=config.username,
                            password=config.password,
                            client_id=config.client_id,
                            client_secret=config.client_secret,
                            user_agent="Tyrannosaurus-Rekt's informative bot v0.1")
    return r


# Looks for certain keywords
def run_bot_search(r: Reddit):
    # Declare the words we are searching for
    search_strings = ['helser', 'hot']
    comment_counter = 0

    word1, word2 = search_strings

    for comment in r.subreddit('iastate').comments(limit=1000):
        if word1 in comment.body.lower() and word2 in comment.body.lower():
            comment_counter += 1
            print(f'I found the comment: {comment.body}. It has the author {comment.author.name}')
            # comment.reply("I heard you mentioned geese: lets page /u/Tyrannosaurus-Rekt.")
    print(f'I found {comment_counter} comments containing {search_strings}.')


def run_user_search(r: Reddit, comments_replied_to):
    # Define a search user, create a list to track all comments
    search_user = config.HiddenUser

    # Track comments replied to
    comments_replied_to = []

    # Track time of newest submission and submission in stream
    new_message_time_utc = 0
    current_comment_time_utc = 0


    #Finds the most recently posted comment
    newest_comment = r.redditor(search_user).comments.new(limit=1).next()
    new_message_time_utc = newest_comment.created_utc
    print(f'The most recent comment was {newest_comment.body!r}')

    # # looks at new comments made by user to a limited amount
    # for comment in r.redditor(search_user).comments.new(limit=1):
    #     comments_replied_to.append(comment.id)
    #     new_message_time_utc = comment.created_utc
    #     print(f'The most recent comment was {comment.body!r}')

    # Streams new comments in
    for comment in r.redditor(search_user).stream.comments():
        current_comment_time_utc = comment.created_utc
        # If new comment is found, reply and update
        if (current_comment_time_utc > new_message_time_utc):
            print(f'I found a new comment {comment.body!r}')
            # comment.reply("")

            comments_replied_to.append(comment.id)

            # Opens comment tracking archive and trims it to maximum 25 comment IDs
            with open("comments_replied_to.txt", "r") as fread:
                comment_id_archive = fread.read().splitlines(True)
                comment_id_archive = comment_id_archive[-24:]

            # Adds the newest comment we've found and replied to as the 25 comment ID, at the end of the
            # list
            with open("comments_replied_to.txt", "w") as fout:
                for comment_id in comment_id_archive:
                    fout.write(comment_id)
                fout.write(comment.id)

            #Track time of most recent message.
            new_message_time_utc = current_comment_time_utc


def get_saved_comments():
    if not os.path.isfile("comments_replied_to.txt"):
        comments_replied_to = []
    else:
        with open("comments_replied_to.txt", "r") as f:
            comments_replied_to = f.read()
            comments_replied_to = comments_replied_to.split("\n")
            comments_replied_to = filter(None, comments_replied_to)

    return comments_replied_to


# Looks for certain user and goes through their comments
r = bot_login()

comments_replied_to = get_saved_comments()
# Currently only does one or the other, will change then when I decide what comment sifting I want
run_user_search(r, comments_replied_to)
run_bot_search(r)
