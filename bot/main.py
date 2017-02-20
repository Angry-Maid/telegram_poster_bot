# shitcode

from urllib.request import urlopen
from urllib.request import Request
import json
import os
import feedparser
import time
import datetime
import config
import telepot
import telepot.aio
import asyncio


bot = telepot.aio.Bot(config.bot_token)
interval = 60 * 60  # e.g. 1 hour
current_time = datetime.datetime.now().time()
channels = []
ids = config.load_ids()
post_file = "post.txt"
admin_list = config.load_admins()
last_post = {"title": "", "content": ""}
current_post = {"title": "", "content": ""}


def set_interval(_interval):
    global interval
    interval = _interval


async def get_new_post():
    if not os.path.isfile(post_file):
        with open(post_file, "w+") as write_cache:
            content = feedparser.parse(config.feed_url)

            #  parse feed and write first post to file
    else:
        with open(post_file, "w+") as r_w_cache:
            content = r_w_cache.read()
            #  if content != first post from feed
            #  rewrite


def get_new_channel(_id):
    global channels
    channels.append(_id)


"""
Runs in loop just to send post from feed on channel with interval
"""


async def post_on_channels():
    while True:
        with open(post_file, "r") as read_cache:
            content = read_cache.read()
            for channel in channels:
                bot.sendMessage(channel, content)
        await asyncio.sleep(interval)


"""
Sends post to all users who subscribed to bot
If it's called without argument's it will post from parsed feed
"""


def post(_content=None):
    if _content is None:
        with open(post_file, "r") as read_cache:
            content = read_cache.read()
            for user_id in ids:
                bot.sendMessage(user_id, content)
    else:
        content = ' '.join(_content)
        for user_id in ids:
            bot.sendMessage(user_id, content)


def handle(msg):
    user_id = msg['from']['id']
    command = msg['text']

    command = command.replace(config.bot_username, '')

    if user_id in admin_list:
        if "/" == command[0]:

            cmd = command.replace('/', '').split()

            if cmd[0] == 'interval' and len(cmd) >= 3:
                _interval = int(cmd[1])
                if cmd[2] == 's':
                    set_interval(_interval)
                elif cmd[2] == 'm':
                    set_interval(_interval * 60)
                elif cmd[2] == 'h':
                    set_interval(_interval * 60 * 60)
            elif cmd[0] == 'post' and len(cmd) == 1:
                post()  # sends post from file
            elif cmd[0] == 'post' and len(cmd) >= 2:
                post(cmd[1:])  # sends post with content
            elif cmd[0] == 'add_channel' and len(cmd) == 2:
                get_new_channel(int(cmd[1]))
    else:
        if "/" == command[0]:

            cmd = command.replace('/', '').split()

            if cmd[0] == 'start':
                with open("user_id.txt", "a+") as write_cache:
                    write_cache.write(str(user_id) + "\n")
                    ids.append(user_id)


def main():
    loop = asyncio.get_event_loop()

    loop.create_task(bot.message_loop(handle))
    loop.create_task(post_on_channels())
    loop.create_task(get_new_post())

    loop.run_forever()


if __name__ == "__main__":
    main()
