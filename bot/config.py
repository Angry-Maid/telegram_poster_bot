# -*- coding: utf-8 -*-

import os


bot_token = ""  # botfather api key
bot_username = "@"  # ur bot username


def load_admins():
    admin_list = {}
    if os.path.isfile("admins.cfg"):
        with open("admins.cfg", "r") as admins:
            for admin in admins:
                to_write = admin.split(" ")
                admin_list.update(
                    {
                        int(to_write[0]): {
                            "bools": [False, False, False, False, False],
                            "name": to_write[1].strip()
                        }
                    }
                )
        return admin_list
    else:
        with open("admins.cfg", "w+") as admins:
            print("Please add admin ID's and name (id name) to the admins.cfg file")
            raise FileExistsError


def load_ids():
    ids = []
    if os.path.isfile("subscribers.txt"):
        with open("subscribers.txt", "r") as users:
            for user in users:
                ids.append(int(user))
        return ids
    else:
        with open("subscribers.txt", "w+") as users:
            return []


def load_channels():
    channels = []
    if os.path.isfile("channels.txt"):
        with open("channels.txt", "r") as ids:
            for channel_id in ids:
                channels.append(int(channel_id))
        return channels
    else:
        with open("channels.txt", "w+") as ids:
            return []


def load_feeds():
    feeds = []
    if os.path.isfile("feeds.txt"):
        with open("feeds.txt", "r") as feeds_f:
            for feed in feeds_f:
                feeds.append(feed)
        return feeds
    else:
        return []
