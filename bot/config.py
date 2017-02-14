bot_token = ""  # botfather api key
feed_url = ""

admin_list = []


def load_admins():
    with open("admins.cfg", "r") as admins:
        for admin in admins:
            admin_list.append(admin)


if __name__ == "__main__":
    load_admins()
