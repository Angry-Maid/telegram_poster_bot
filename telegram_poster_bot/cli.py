#!/usr/bin/env python3

import asyncio

import feedparser
import telepot
import telepot.aio

from telegram_poster_bot.config import config


def handle_msg(msg):
    print(msg)


async def parse_feeds():
    while True:
        for feed in config.FEEDS:
            d = feedparser.parse(feed)
            print(d)
        await asyncio.sleep(config.FEEDS_INTERVAL)


def main():
    bot = telepot.aio.Bot(config.BOT_TOKEN)
    loop = asyncio.get_event_loop()

    # loop.create_task(bot.message_loop(handle_msg))
    # loop.create_task(post_on_channels())
    loop.create_task(parse_feeds())

    loop.run_forever()


if __name__ == "__main__":
    main()
