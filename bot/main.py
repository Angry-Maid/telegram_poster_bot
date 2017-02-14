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
import json


bot = telepot.aio.Bot(config.bot_token)
interval = 60 * 60  # e.g. 1 hour
current_time = datetime.datetime.now().time()
channels = []
post_file = "post.txt"
config.load_admins()

# TODO: check for updates (when bot was added to any channel)
# TODO: "https://api.telegram.org/bot" + config.bot_token + "/getUpdates"
# TODO: parse -> dict['chat']['id']


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


async def get_new_channel():
    global channels

    request = "https://api.telegram.org/bot" + config.bot_token + "/getUpdates"
    res = urlopen(request).readall().decode().json()
    try:
        print(res['new_chat_participant']) # if bot was actually added and not deleted from chat
    except Exception:
        _id = None
    else:
        _id = int(res['chat']['id'])

    channels.append(_id)


async def post_on_channels(_content):
    for channel in channels: # add a check: if a channel value is None then we pass else we sendMessage
        bot.sendMessage(channel, _content)
    await asyncio.sleep(interval)


def post(_chat_id, _content, _interval):



def handle(msg):
    user_id = msg['from']['id']
    command = msg['text']

    if user_id in config.admin_list:
        if "/" in command:

            cmd = command.replace('/', '').split()

            if cmd[0] == 'interval' and len(cmd) >= 3:
                _interval = int(cmd[1])
                if cmd[2] == 's':
                    set_interval(_interval)
                elif cmd[2] == 'm':
                    set_interval(_interval * 60)
                elif cmd[2] == 'h':
                    set_interval(_interval * 60 * 60)
            elif cmd[0] == 'post' and len(cmd) >= 2:
                post_on_channels(cmd[1:])  # send text(text itself without chat command)


def main():
    loop = asyncio.get_event_loop()

    loop.create_task(bot.message_loop(handle))
    loop.create_task(get_new_channel())
    loop.create_task(get_new_post())

    loop.run_forever()


if __name__ == "__main__":
    main()
