import praw
from praw import Reddit
import time

import config

def bot_login():
    r: Reddit = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = "Tyrannosaurus-Rekt's informative bot v0.1")
    return r

#Looks for certain keywords
def run_bot_search(r: Reddit):
    #Declare the words we are searching for
    SearchStrings = ['helser', 'hot']
    CommentCounter = 0

    Word1, Word2 = SearchStrings

    for comment in r.subreddit('iastate').comments(limit=1000):
        if Word1 in comment.body.lower() and Word2 in comment.body.lower():
            CommentCounter += 1
            print(f'I found the comment: {comment.body}. It has the author {comment.author.name}')
            #comment.reply("I heard you mentioned geese: lets page /u/Tyrannosaurus-Rekt.")
    print(f'I found {CommentCounter} comments containing {SearchStrings}.')

def run_user_search(r: Reddit):
    #Define a search user, create a list to track all comments
    SearchUser = config.HiddenUser

    #Track comments replied to
    CommentsRepliedTo = []

    #Track time of newest submission and submission in stream
    NewMessageTimeUTC = 0
    CurrentCommentTimeUTC = 0

    #looks at new comments made by user to a limited amount
    for comment in r.redditor(SearchUser).comments.new(limit=1):
        CommentsRepliedTo.append(comment.id)
        NewMessageTimeUTC = comment.created_utc
        print(f'The most recent comment was {comment.body!r}')


    #Streams new comments in
    for comment in r.redditor(SearchUser).stream.comments():
        CurrentCommentTimeUTC = comment.created_utc
        #If new comment is found, reply and update
        if(CurrentCommentTimeUTC > NewMessageTimeUTC):
            print(f'I found a new comment {comment.body!r}')
            comment.reply("Hey Eric! Get off reddit and do something useful. You're probably boasting about your elo right now. *Love you baby*")
            CommentsRepliedTo.append(comment.id)
            NewMessageTimeUTC = CurrentCommentTimeUTC

#Looks for certain user and goes through their comments
r = bot_login()

#Currently only does one or the other, will change then when I decide what comment sifting I want
run_user_search(r)
run_bot_search(r)