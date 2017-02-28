from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import re
import csv
import html
import queue
import config
import asyncio
import telepot
import datetime
import feedparser
import telepot.aio


feed_queue = queue.Queue()
bot = telepot.aio.Bot(config.bot_token)
interval = 60 * 10
check_rate = 60 * 10
first_launch = [True, True]
to_post = {
    "title": "",
    "content": ""
}
keyboard_commands_list = [
    "Послать пост",
    "Послать текст подписчикам",
    "Установить интервал",
    "Установить таймер проверки rss",
    "Добавить администратора",
    "Удалить администратора",
    "Показать интервалы",
    "Показать администраторов",
    "Сохранить текущие параметры",
    "Перезагрузить конфиг",
    "Закрыть клавиатуру"
]

channels = config.load_channels()
subscribed_users = config.load_ids()
admins_dict = config.load_admins()


def set_interval(_interval):
    global interval
    interval = _interval


def set_check_rate(_check_rate):
    global check_rate
    check_rate = _check_rate


async def get_new_post():
    rss_entry = {
        "title": "",
        "content": ""
    }
    while True:
        print("Reading feed...")
        feed = feedparser.parse(config.feed_url)
        if rss_entry['title'] != feed.entries[0].title:
            rss_entry['title'] = feed.entries[0].title
            rss_entry['content'] = html.unescape(feed.entries[0].description)
            to_post['title'] = feed.entries[0].title
            to_post['content'] = html.unescape(feed.entries[0].description)
            with open("posts.csv", "a") as csv_file:
                fields = ["title", "content"]
                writer = csv.DictWriter(csv_file, fieldnames=fields, quotechar="|", delimiter=' ')

                writer.writeheader()
                writer.writerow(rss_entry)
            print("Done reading feed.")
            feed_queue.put(rss_entry)
        else:
            print("RSS wasn't updated yet on server side")
        await asyncio.sleep(check_rate)  # e.g. wait 10 minutes(by standard) and check for new post


async def post_on_channels():
    while True:
        if not first_launch[0]:
            print("Start posting on channels...")
            if not feed_queue.empty():
                content = feed_queue.get()
                to_delete = []
                for channel in channels:
                    try:
                        await bot.sendMessage(channel, content["title"] + "\n" + content["content"])
                    except Exception:
                        to_delete.append(channel)
                for channel in to_delete:
                    channels.remove(channel)
                print("Done posting on channels.")
            else:
                print("Feed queue empty")
        else:
            first_launch[0] = False
        await asyncio.sleep(interval)


async def post(_content=None):
    if not first_launch[1]:
        if _content is None:
            print("Start writing to subs...")
            if not feed_queue.empty():
                content = to_post
                to_delete = []
                for user_id in subscribed_users:
                    try:
                        await bot.sendMessage(user_id, content["title"] + "\n" + content["content"])
                    except Exception:
                        to_delete.append(user_id)
                for user_id in to_delete:
                    subscribed_users.remove(user_id)
                print("Done writing to subs.")
            else:
                print("Feed queue empty")
        else:
            print("Start writing to subs...")
            content = ' '.join(_content)
            to_delete = []
            for user_id in subscribed_users:
                try:
                    await bot.sendMessage(user_id, content)
                except Exception:
                    to_delete.append(user_id)
            for user_id in to_delete:
                subscribed_users.remove(user_id)
            print("Done writing to subs.")

        with open("subscribers.txt", "w") as subs_file:
            for sub in subscribed_users:
                subs_file.write(str(sub) + "\n")
    else:
        first_launch[1] = False


async def safe_save():
    while True:
        print("Start saving info...")
        with open("channels.txt", "w") as channels_file:
            for channel in channels:
                channels_file.write(str(channel) + "\n")

        with open("subscribers.txt", "w") as subs_file:
            for sub in subscribed_users:
                subs_file.write(str(sub) + "\n")

        with open("admins.cfg", "w") as admins_file:
            for key, value in admins_dict.items():
                admins_file.write(str(key) + " " + value["name"] + "\n")

        print("Done saving info.")
        await asyncio.sleep(60 * 30)


def button_save():
    print("Start saving info...")
    with open("channels.txt", "w") as channels_file:
        for channel in channels:
            channels_file.write(str(channel) + "\n")

    with open("subscribers.txt", "w") as subs_file:
        for sub in subscribed_users:
            subs_file.write(str(sub) + "\n")

    with open("admins.cfg", "w") as admins_file:
        for key, value in admins_dict.items():
            admins_file.write(str(key) + " " + value["name"] + "\n")

    print("Done saving info.")


def save_reload():
    global channels
    global subscribed_users
    global admins_dict
    channels = config.load_channels()
    subscribed_users = config.load_ids()
    admins_dict = config.load_admins()


async def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command = msg['text']
    print(datetime.datetime.now().time())
    print("Chat message:", content_type, chat_type, chat_id)
    print("Command:", command)

    is_command = True
    is_exists = False

    try:
        if chat_id in admins_dict:
            if msg['forward_from_chat']['id'] not in channels:
                channels.append(msg['forward_from_chat']['id'])
            else:
                is_exists = True
    except KeyError:
        pass
    else:
        if chat_id in admins_dict:
            is_command = False
            if not is_exists:
                await bot.sendMessage(chat_id, "Канал добавлен в список")
                print(msg['forward_from_chat']['id'])
            else:
                await bot.sendMessage(chat_id, "Канал уже есть в списке")

    if chat_type == "private" and content_type == "text" and is_command:

        cmd = command.split(' ')

        if chat_id in admins_dict:

            if cmd[0] == "/kb":
                reply_markup = ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="Послать пост"), KeyboardButton(text="Послать текст подписчикам")],
                    [KeyboardButton(text="Установить интервал"), KeyboardButton(text="Установить таймер проверки rss")],
                    [KeyboardButton(text="Добавить администратора"), KeyboardButton(text="Удалить администратора")],
                    [KeyboardButton(text="Показать интервалы"), KeyboardButton(text="Показать администраторов")],
                    [KeyboardButton(text="Сохранить текущие параметры"), KeyboardButton(text="Перезагрузить конфиг")],
                    [KeyboardButton(text="Закрыть клавиатуру")]
                ])
                await bot.sendMessage(chat_id, "Настройки", reply_markup=reply_markup)

            elif cmd[0] == "/help":
                await bot.sendMessage(
                    chat_id,
                    """
/kb - показать клавиатуру с настройками
Помошь по настройкам:
Послать пост - посылает последний пост с rss всем пользователям, которые подписались на бота.\n
Послать текст подписчикам - требует ввода от администратора. Рассылает пользователям которые подписались на бота текст который ввел администратор.\n
Установить интервал - устанавливает интервал отправки сообщений с rss на канал.\n
Установить таймер проверки rss - устанавливает интервал с которым проверяется rss на новую запись (желательно держать его в районе 5-20 минут).\n
Добавить администратора - добавляет администратора по ID его профиля в телеграме и дополнительно устанавливается имя для будущей удобности.\n
Удалить администратора - удаляет права администратора у пользователя по имени под которым он был записан в администраторы.\n
Показать интервалы - показывает текущие интервал отправки постов на каналы и проверки rss.\n
Показать администраторов - показывает текущий список администраторов.\n
Сохранить текущие параметры - сохраняет список пользователей, админисраторов и каналов на данный момент.\n
Перезагрузить конфиг - загружает из файлов конфигурации данные, на случай если локальный администратор изменил что-то в конфиг файлах.\n
Закрыть клавиатуру - закрывает клавиатуру настроек.\n
Как добавить канал на который нужно постить?
Первым делом нужно добавить бота на канал, после нужно создать запись на канале с надписью "test", а потом переслать эту запись с цитированием в личные сообщения боту(сделать это может только администратор).
                    """
                )

            elif admins_dict[chat_id]["bools"][0] and ' '.join(cmd) not in keyboard_commands_list:
                    await post(cmd)
                    admins_dict[chat_id]["bools"][0] = False
            elif admins_dict[chat_id]["bools"][1] and ' '.join(cmd) not in keyboard_commands_list:
                is_match = ' '.join(cmd)
                if re.match(r"\d+ [hms]", is_match):
                    _interval = int(cmd[0])
                    if cmd[1] == 's':
                        set_interval(_interval)
                    elif cmd[1] == 'm':
                        set_interval(_interval * 60)
                    elif cmd[1] == 'h':
                        set_interval(_interval * 60 * 60)
                    admins_dict[chat_id]["bools"][1] = False
                else:
                    await bot.sendMessage(chat_id, "Пожалуйста, введите правильно время в формате: [время (h|m|s)]")
            elif admins_dict[chat_id]["bools"][2] and ' '.join(cmd) not in keyboard_commands_list:
                is_match = ' '.join(cmd)
                if re.match(r"\d+ [hms]", is_match):
                    _check_rate = int(cmd[0])
                    if cmd[1] == 's':
                        set_check_rate(_check_rate)
                    elif cmd[1] == 'm':
                        set_check_rate(_check_rate * 60)
                    elif cmd[1] == 'h':
                        set_check_rate(_check_rate * 60 * 60)
                    admins_dict[chat_id]["bools"][2] = False
                else:
                    await bot.sendMessage(chat_id, "Пожалуйста, введите правильно время в формате: [время (h|m|s)]")
            elif admins_dict[chat_id]["bools"][3] and ' '.join(cmd) not in keyboard_commands_list:
                if len(cmd) == 2:
                    admins_dict.update(
                        {
                            int(cmd[0]): {
                                "bools": [False, False, False, False, False],
                                "name": cmd[1].strip()
                            }
                        }
                    )
                    admins_dict[chat_id]["bools"][3] = False
                    await bot.sendMessage(chat_id, "Администратор успешно добавлен")
                else:
                    await bot.sendMessage(chat_id, "Имя администратора должно быть одним словом. Пожалуйста введите ещё раз")
            elif admins_dict[chat_id]["bools"][4] and ' '.join(cmd) not in keyboard_commands_list:
                key_ = None
                for key, value in admins_dict.items():
                    if cmd[0] == value["name"]:
                        key_ = key
                        break
                if key_ is None:
                    await bot.sendMessage(chat_id, "Пожалуйста, укажите правильно имя администратора как оно записано в списке")
                else:
                    del admins_dict[key_]
                    with open("admins.cfg", "w") as admins_file:
                        for key, value in admins_dict.items():
                            admins_file.write(str(key) + " " + value["name"] + "\n")
                    admins_dict[chat_id]["bools"][4] = False
                    await bot.sendMessage(chat_id, "Администратор успешно удалён")
            elif ' '.join(cmd) == 'Послать пост':
                await post()
            elif ' '.join(cmd) == 'Послать текст подписчикам':
                for i in range(len(admins_dict[chat_id]["bools"])):
                    admins_dict[chat_id]["bools"][i] = False
                admins_dict[chat_id]["bools"][0] = True
                await bot.sendMessage(chat_id, "Пожалуйста, напишите текст")
            elif ' '.join(cmd) == 'Установить интервал':
                for i in range(len(admins_dict[chat_id]["bools"])):
                    admins_dict[chat_id]["bools"][i] = False
                admins_dict[chat_id]["bools"][1] = True
                await bot.sendMessage(chat_id,
                                      "Текущий интервал: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(interval),
                                          float(interval) / 60,
                                          (float(interval) / 60) / 60)
                                      )
                await bot.sendMessage(chat_id,
                                      "Пожалуйста, укажите время в формате [время (h|m|s)] (например \"1 h\" или \"35 m\")")
            elif ' '.join(cmd) == 'Установить таймер проверки rss':
                for i in range(len(admins_dict[chat_id]["bools"])):
                    admins_dict[chat_id]["bools"][i] = False
                admins_dict[chat_id]["bools"][2] = True
                await bot.sendMessage(chat_id,
                                      "Текущий таймер: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(check_rate),
                                          float(check_rate) / 60,
                                          (float(check_rate) / 60) / 60)
                                      )
                await bot.sendMessage(chat_id,
                                      "Пожалуйста, укажите время в формате [время (h|m|s)] (например \"1 h\" или \"35 m\")")
            elif ' '.join(cmd) == 'Добавить администратора':
                for i in range(len(admins_dict[chat_id]["bools"])):
                    admins_dict[chat_id]["bools"][i] = False
                admins_dict[chat_id]["bools"][3] = True
                await bot.sendMessage(chat_id, "Пожалуйста, укажите id и запишите его имя (id имя) администратора которого нужно добавить в список")
            elif ' '.join(cmd) == 'Удалить администратора':
                for i in range(len(admins_dict[chat_id]["bools"])):
                    admins_dict[chat_id]["bools"][i] = False
                admins_dict[chat_id]["bools"][4] = True
                await bot.sendMessage(chat_id, "Пожалуйста, укажите имя администратора котого нужно удалить")
            elif ' '.join(cmd) == 'Показать интервалы':
                await bot.sendMessage(chat_id,
                                      "Текущий интервал: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(interval),
                                          float(interval) / 60,
                                          (float(interval) / 60) / 60)
                                      )
                await bot.sendMessage(chat_id,
                                      "Текущий(rss) таймер: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(check_rate),
                                          float(check_rate) / 60,
                                          (float(check_rate) / 60) / 60)
                                      )
            elif ' '.join(cmd) == 'Показать администраторов':
                list_ = ""
                for key, value in admins_dict.items():
                    list_ += value["name"] + " - " + str(key) + "\n"
                await bot.sendMessage(chat_id, list_)
            elif ' '.join(cmd) == 'Сохранить текущие параметры':
                button_save()
                await bot.sendMessage(chat_id, "Данные успешно сохранены")
            elif ' '.join(cmd) == 'Перезагрузить конфиг':
                save_reload()
                await bot.sendMessage(chat_id, "Данные успешно загружены")
            elif ' '.join(cmd) == 'Закрыть клавиатуру':
                await bot.sendMessage(chat_id, "Хорошо", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        elif cmd[0] == "/sub":
            if chat_id not in subscribed_users:
                subscribed_users.append(chat_id)
                with open("subscribers.txt", "w") as subs_file:
                    for sub in subscribed_users:
                        subs_file.write(str(sub) + "\n")
                await bot.sendMessage(chat_id, "Вы подписались на бота")
            else:
                await bot.sendMessage(chat_id, "Вы уже подписаны на бота")
        elif cmd[0] == "/unsub":
            if chat_id in subscribed_users:
                subscribed_users.remove(chat_id)
                with open("subscribers.txt", "w") as subs_file:
                    for sub in subscribed_users:
                        subs_file.write(str(sub) + "\n")
                await bot.sendMessage(chat_id, "Вы отписались от бота")
            else:
                await bot.sendMessage(chat_id, "Вы не подписаны ещё на бота")
        elif cmd[0] == "/help":
            await bot.sendMessage(
                chat_id,
                """
/sub - подписаться на бота
/unsub - отписаться от бота
                """
            )


def main():
    loop = asyncio.get_event_loop()

    loop.create_task(bot.message_loop(handle))
    loop.create_task(get_new_post())
    loop.create_task(post_on_channels())
    loop.create_task(safe_save())

    loop.run_forever()


if __name__ == "__main__":
    main()
