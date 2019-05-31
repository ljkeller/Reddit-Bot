import praw
from praw import Reddit
import time
import os
import search
import commands
import config


def bot_login():
    """
    Initializes the reddit bot by linking it with reddit and loging in. Takes
    info from config.py.
    :return: instance of Reddit for other functions
    """
    r: Reddit = praw.Reddit(username=config.username,
                            password=config.password,
                            client_id=config.client_id,
                            client_secret=config.client_secret,
                            user_agent="Tyrannosaurus-Rekt's informative "
                                       "bot. Serves /r/iastate "
                                       "v0.2")
    return r


def run_user_search(r: Reddit, comments_replied_to):
    """
    Runs a stream of new comments from a designated Redditor. Replies to new
    comments with a message.
    todo    link this with some api to make funny comment responses. Update
        time to be based off time at start of program.
    :param r: an instance of Reddit
    :param comments_replied_to: the archive of comment IDs for comments this
    bot has replied to already
    """
    # Define a search user, create a list to track all comments
    search_user = config.HiddenUser

    # Track comments replied to
    comments_replied_to = []

    # Track time of newest submission and submission in stream
    new_message_time_utc = 0
    current_comment_time_utc = 0

    # Finds the most recently posted comment
    newest_comment = r.redditor(search_user).comments.new(limit=1).next()
    new_message_time_utc = newest_comment.created_utc
    print(f'The most recent comment was {newest_comment.body!r}')

    # Streams new comments in
    for comment in r.redditor(search_user).stream.comments():
        current_comment_time_utc = comment.created_utc
        # If new comment is found, reply and update
        if (current_comment_time_utc > new_message_time_utc):
            print(f'I found a new comment {comment.body!r}')
            comment.reply(commands.HELSER)

            comments_replied_to.append(comment.id)

            # Opens comment tracking archive and trims it to maximum 25
            # comment IDs
            with open("comments_replied_to.txt", "r") as fread:
                comment_id_archive = fread.read().splitlines(True)
                comment_id_archive = comment_id_archive[-24:]

            # Adds the newest comment we've found and replied to as the 25
            # comment ID, at the end of the
            # list
            with open("comments_replied_to.txt", "w") as fout:
                for comment_id in comment_id_archive:
                    fout.write(comment_id)
                fout.write(comment.id)

            # Track time of most recent message.
            new_message_time_utc = current_comment_time_utc


def serve_iastate(r: Reddit):
    """
    This is the subreddit-serving functionality of the bot. In its current
    form, it reads new comments in /r/iastate and sifts through, looking for
    commands directed at it. It will act when given the commands ! followed by
    helser, goose, butler, why, and t-rekt-commands.
    :param r: an instance of Reddit
    """

    # keywords we are looking for in new comments
    keywords = ['!helser', '!goose', '!butler', '!why', '!t-rekt-commands']

    time_started_utc = time.time()
    print(f'I started my session on: '
          f'{time.asctime(time.localtime(time_started_utc))}')

    for newest_comment in r.subreddit('iastate').comments(limit=1):
        body = newest_comment.body
        newest_comment_utc = newest_comment.created_utc
        print(f'The newest comment was "{body}" at a time '
              f'{time.asctime(time.localtime(newest_comment_utc))}')

    # Stream new comments in, look through them for commands
    for new_comment in r.subreddit('iastate').stream.comments():
        if new_comment.created_utc > time_started_utc and new_comment.author \
                is not r.user.me():
            print(f'New comment "{new_comment.body}" at '
                  f'{time.asctime(time.localtime(new_comment.created_utc))}')
            command = search.search_keywords(keywords,
                                             new_comment.body.lower())

            if command is '!helser':
                new_comment.reply(commands.HELSER)
            elif command is '!goose' or command is '!geese':
                new_comment.reply(commands.GOOSE)
            elif command is '!butler':
                new_comment.reply(commands.BUTLER)
            elif command is '!why':
                new_comment.reply(commands.WHY)
            elif command is '!t-rekt-commands':
                new_comment.reply(commands.COMMANDS)

            if 'good bot' in new_comment.body.lower() and \
                    new_comment.parent.author \
                    is \
                    r.user.me():
                new_comment.reply(":D Thanks so much! ")
                print('Somebody said I was a good bot!')


def get_saved_comments():
    """
    This function reads all the archived comments our bot has responded to.
    Note: comments are only saved in the run_user_search method at this moment
    in time.
    :return: An archive of the comments weve responded to in the form of an
    iterable holding the comment IDs.
    """
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

serve_iastate(r)

'''
 Currently, this bot only operates within /r/iastate. If I wanted to follow 
 a user around, I would set comments_replied_to = get_saved_comments() and 
 throw that parameter in run_user_search.
'''
