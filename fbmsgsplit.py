#!/usr/bin/env python3

import argparse
import os

from copy import copy
from datetime import datetime

from bs4 import BeautifulSoup


def parse_time_str(time_str):
    '''
    Parse:
        Saturday, July 27, 2013 at 11:01pm CDT
    '''
    return datetime.strptime(time_str, '%A, %B %d, %Y at %I:%M%p %Z')


def parse_msg_metadata(data):
    '''
    return {
        user: user,
        time: time
    }
    '''
    user = data.find("span", {"class": "user"}).text
    time_str = data.find("span", {"class": "meta"}).text

    return {
        "user": user,
        "timestamp": parse_time_str(time_str),
    }


def parse_thread(t):
    children = list(t.children)

    index = 1
    messages = []
    while index < len(children):
        msg_metadata = children[index]

        assert (index + 1 < len(children)), "msg_metadata without msg"
        msg = children[index + 1]

        assert msg_metadata.name == "div", "msg_metadata not div"
        assert msg.name == "p", "msg not p"

        msg_obj = parse_msg_metadata(msg_metadata)
        msg_obj["msg"] = msg.text
        msg_obj["raw"] = str(msg_metadata) + str(msg)
        messages.append(msg_obj)

        index += 2

    messages.reverse()
    return {
        "messages": messages,
        "user": children[0]
    }


def combine_threads(thread_obj_arr):
    # user => message_arr
    thread_obj_cache = {}

    for thread_obj in thread_obj_arr:
        user = thread_obj["user"]

        if not user in thread_obj_cache:
            thread_obj_cache[user] = []
        thread_obj_cache[user] += thread_obj["messages"]

    # convert thread_obj_cache to thread_objs
    thread_objs = []
    for user in thread_obj_cache:
        obj = {
            "messages": thread_obj_cache[user],
            "user": user
        }
        thread_objs.append(obj)

    return thread_objs


def split_userstring(userstring):
    found_users = userstring.split(",")
    found_users = list(map(lambda x: x.strip(), found_users))
    return found_users


def guess_users(threads):
    userstring_arr = list(map(lambda x: x["user"], threads))
    parsed_users = list(map(split_userstring, userstring_arr))

    # Only look at conversations with 2 people
    parsed_users = list(filter(lambda x: len(x) == 2, parsed_users))

    cache = {}
    for user_arr in parsed_users:
        for u in user_arr:
            if not u in cache:
                cache[u] = 0

            cache[u] += 1

    # Find the users who are involved in more than 5 1-on-1 conversations
    # Shouldn't be more than 2, but let's say 5 :)
    return list(filter(lambda x: cache[x] > 5, cache.keys()))


def prune_users(threads, prune_arr):
    '''
    Prune the given users from the "user" field of threads
    This method modifies threads in-place!!
    '''

    def _find_match(arr1, arr2):
        for x in arr1:
            if x in arr2:
                return x
        return None

    for t in threads:
        parsed_users = split_userstring(t["user"])
        matched = _find_match(prune_arr, parsed_users)
        if matched:
            parsed_users.remove(matched)

        t["user"] = ",".join(parsed_users)

    return threads


def get_html_threads(filename="messages.htm"):
    with open(filename) as f:
        html = "".join(f.readlines())
    soup = BeautifulSoup(html)

    return soup.body.find_all("div", {"class": "thread"})


def get_threads(filename, prune_list=[]):
    parsed_thread_arr = list(map(parse_thread, get_html_threads(filename)))
    thread_arr = combine_threads(parsed_thread_arr)
    thread_arr = prune_users(thread_arr, prune_list)

    return thread_arr


def generate_msg_html(msg_obj, colors={}):
    MSG_TEMPLATE = '''
    <font color="%s">
    <font size="2">(%s)</font>
    <b>%s:</b></font>
    %s
    <br/>
    '''
    font_color = "#000000" # Black as default
    timestamp = str(msg_obj["timestamp"])
    user = msg_obj["user"]
    message = msg_obj["msg"]

    variables = (font_color, timestamp, user, message)
    return MSG_TEMPLATE % variables


def generate_thread_html(thread_obj):
    HTML_TEMPLATE = '''
    <html>
    <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>%s</title>
    </head>
    <body>
    <h3>%s</h3>
    %s
    </body>
    </html>
    '''
    title = "Conversation with " + thread_obj["user"]

    # Build messages_html
    messages_html = ""
    for msg_obj in thread_obj["messages"]:
        messages_html += generate_msg_html(msg_obj)

    variables = (title, title, messages_html)
    return HTML_TEMPLATE % variables


def write_messages(dest_dir, threads):
    try:
        os.mkdir(dest_dir)
    except FileExistsError:
        print("Directory \"%s\" already exists. Continuing..." % dest_dir)
        pass

    for t in threads:
        filename = os.path.join(dest_dir, t["user"])

        # Limit filename to 100 chars
        filename = filename[:100]

        counter = 2
        while os.path.isfile(filename + ".html"):
            filename = filename[:-1] + str(counter)
            counter += 1
        else:
            html = generate_thread_html(t)
            with open(filename + ".html", "w") as f:
                f.write(html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", metavar="INPUT_FILE",
                        nargs="?", default="messages.htm",
                        help="The input messages file. Default: messages.htm")
    parser.add_argument("output_dir", metavar="OUTPUT_DIR",
                        nargs="?", default="fb_messages",
                        help="Output directory for generated chat logs")
    parser.add_argument("-p", "--prune-users", type=lambda x:x.split(","),
                        nargs="?", default=[],
                        help=("Specify your own Facebook name(s) (separated by"
                              " commas) to prune from the filenames of generated"
                              " files. "
                              "Run --list-guesses to get a list of guesses for"
                              " your Facebook name."))
    parser.add_argument("-l", "--list-guesses", action="store_true",
                        help="list guesses for your Facebook name(s).")
    args = parser.parse_args()


    print("Reading file: %s" % args.input_file)
    print("\tThis may take a few moments")
    threads = get_threads(args.input_file, args.prune_users)
    if args.list_guesses:
        guesses = guess_users(threads)
        print("Guess(es):", ",".join(guesses))
    else:
        write_messages(args.output_dir, threads)


if __name__ == "__main__":
    main()
