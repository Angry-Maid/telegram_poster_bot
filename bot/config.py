import os


bot_token = ""  # botfather api key
bot_username = "@"  # ur bot username
feed_url = ""


def load_admins():
    admin_list = []
    if os.path.isfile("admins.cfg"):
        with open("admins.cfg", "r") as admins:
            for admin in admins:
                admin_list.append(int(admin))
        return admin_list
    else:
        with open("admins.cfg", "w+") as admins:
            print("Please add admin ID's to the admins.cfg file")
            raise FileExistsError


def load_ids():
    ids = []
    if os.path.isfile("user_id.txt"):
        with open("user_id.txt", "r") as users:
            for user in users:
                ids.append(int(user))
        return ids
    else:
        with open("user_id.txt", "w+") as users:
            return []
