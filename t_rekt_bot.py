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
    keywords = ['!helser', '!goose', '!butler', '!why', '!t-rekt-commands',
                '!fth']

    time_started_utc = time.time()
    print(f'I started my session on: '
          f'{time.asctime(time.localtime(time_started_utc))}')

    for newest_comment in r.subreddit('test').comments(limit=1):
        body = newest_comment.body
        newest_comment_utc = newest_comment.created_utc
        print(f'The newest comment was"{body}" at a time '
              f'{time.asctime(time.localtime(newest_comment_utc))}'
              f' by {newest_comment.author.name}')

    # Stream new comments in, look through them for commands
    for new_comment in r.subreddit('test').stream.comments():
        if new_comment.created_utc > time_started_utc and \
                'T-Rekt-Bot' not in new_comment.author.name:
            print(f'New comment "{new_comment.body}" at '
                  f'{time.asctime(time.localtime(new_comment.created_utc))}'
                  f'by {new_comment.author.name}')
            command = search.search_keywords(keywords,
                                             new_comment.body.lower())
            if command or 'good bot' in new_comment.body.lower() and \
                    new_comment.parent().author.name:
                respond_comment(new_comment, command, 3)


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


def respond_comment(comment, command, attempts):
    """
    A function used to respond to user comments containing a command! Will run
    an 'attemps' amount of time before it stops executing
    :param comment: Given comment containing a command to be responded to
    :param command: Given command that needs response/action
    :param attemps: Number of attemps bot will try responding before giving up
    """
    response = ''

    if 'good bot' in comment.body.lower():
        print(f'{comment.author.name} said I was a good bot!')
        response = "I'm so happy you think I'm a good bot, " \
                   "" + comment.author.name + "!\n\n"

    if command == '!helser':
        response += commands.HELSER
    elif command == '!goose' or command is '!geese':
        response += commands.GOOSE
    elif command == '!butler':
        response += commands.BUTLER
    elif command == '!why':
        response += commands.WHY
    elif command == '!t-rekt-commands':
        response += commands.COMMANDS
    elif command == '!fth':
        response += commands.FTH

    while attempts > 0:
        # if successful we want to return, otherwise we have error messages
        try:
            comment.reply(response)
            print(f'I responded to the comment {comment.body} with command '
                  f'{command}')
            return
        # Allows bot to exit on ^c
        except KeyboardInterrupt:
            break
        except Exception as e:
            # Avoiding the RateLimitExceeded exception. Usually have to wait
            # 600 seconds
            print(f'I just experienced {e.with_traceback()}')
            print("I have to sleep for 5 minutes")
            time.sleep(301)
            respond_comment(comment, command, attempts - 1)

    print(f'I failed to respond to command {command!r} in comment'
          f'{comment.body!r} by {comment.author.name!r}')
    return


# Looks for certain user and goes through their comments
r = bot_login()

serve_iastate(r)

'''
 Currently, this bot only operates within /r/iastate. If I wanted to follow 
 a user around, I would set comments_replied_to = get_saved_comments() and 
 throw that parameter in run_user_search.
'''
