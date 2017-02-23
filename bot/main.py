from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import csv
import queue
import config
import asyncio
import telepot
import datetime
import feedparser
import telepot.aio


feed_queue = queue.Queue()
bot = telepot.aio.Bot(config.bot_token)
interval = 60 * 60  # e.g. 1 hour
check_rate = 60 * 30  # e.g. half an hour
send_to_subs = False

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
    rss_entry = {"title": "", "content": ""}
    while True:
        print("Reading feed...")
        feed = feedparser.parse(config.feed_url)

        print(feed.entries[0].title, feed.entries[0].description)
        if rss_entry['title'] != feed.entries[0].title:
            rss_entry['title'] = feed.entries[0].title
            rss_entry['content'] = feed.entries[0].description
            with open("posts.csv", "a") as csv_file:
                fields = ["title", "content"]
                writer = csv.DictWriter(csv_file, fieldnames=fields)

                writer.writeheader()
                writer.writerow(rss_entry)
            print("Done reading feed.")
            feed_queue.put(rss_entry)
        else:
            pass
        await asyncio.sleep(check_rate)  # e.g. wait half an hour(by standard) and check for new post


async def post_on_channels():
    while True:
        print("Starting posting on channels...")
        content = await feed_queue.get()
        for channel in channels:
            await bot.sendMessage(channel, content["title"] + "\n" + content["content"])
        print("Done posting on channels.")
        await asyncio.sleep(interval)


async def post(_content=None):
    if _content is None:
        print("Starting writing to subs...")
        content = await feed_queue.get()
        for user_id in subscribed_users:
            await bot.sendMessage(user_id, content["title"] + "\n" + content["content"])
        print("Done writing to subs.")
    else:
        print("Starting writing to subs...")
        content = ' '.join(_content)
        for user_id in subscribed_users:
            await bot.sendMessage(user_id, content)
        print("Done writing to subs.")


async def safe_save():
    while True:
        print("Starting saving info...")
        with open("channels.txt", "w") as channels_file:
            for channel in channels:
                channels_file.write(str(channel) + "\n")

        with open("subscribers.txt", "w") as subs_file:
            for sub in subscribed_users:
                subs_file.write(str(sub) + "\n")

        with open("admins.cfg", "w") as admins_file:
            for admin in admins_dict.keys():
                admins_file.write(str(admin) + "\n")

        print("Done saving info.")
        await asyncio.sleep(60 * 30)


async def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    command = msg['text']
    print(datetime.datetime.now().time())
    print("Chat message: ", content_type, chat_type, chat_id)
    print("Command: ", command)

    is_command = True

    try:
        channels.append(msg['forward_from_chat']['id'])
    except KeyError:
        pass
    else:
        is_command = False
        await bot.sendMessage(chat_id, "Канал добавлен в список")

    if chat_type == "private" and content_type == "text" and is_command:

        cmd = command.split(' ')

        if chat_id in admins_dict:

            if cmd[0] == "/kb":
                reply_markup = ReplyKeyboardMarkup(keyboard=[
                    [KeyboardButton(text="Послать пост"), KeyboardButton(text="Послать текст подписчикам")],
                    [KeyboardButton(text="Установить интервал"), KeyboardButton(text="Установить таймер проверки rss")],
                    [KeyboardButton(text="Добавить администратора"), KeyboardButton(text="Показать интервалы")],
                    [KeyboardButton(text="Закрыть клавиатуру")]
                ])
                await bot.sendMessage(chat_id, "Настройки", reply_markup=reply_markup)

            elif cmd[0] == "/help":
                await bot.sendMessage(chat_id,
                                      """
                                      /kb - показать кнопки
                                      """)

            elif admins_dict[chat_id][0]:
                post(cmd)
                admins_dict[chat_id][0] = False
            elif admins_dict[chat_id][1]:
                _interval = int(cmd[0])
                if cmd[1] == 's':
                    set_interval(_interval)
                elif cmd[1] == 'm':
                    set_interval(_interval * 60)
                elif cmd[1] == 'h':
                    set_interval(_interval * 60 * 60)
                admins_dict[chat_id][1] = False
            elif admins_dict[chat_id][2]:
                _check_rate = int(cmd[0])
                if cmd[1] == 's':
                    set_interval(_check_rate)
                elif cmd[1] == 'm':
                    set_interval(_check_rate * 60)
                elif cmd[1] == 'h':
                    set_interval(_check_rate * 60 * 60)
                admins_dict[chat_id][2] = False
            elif admins_dict[chat_id][3]:
                admins_dict.update({int(cmd[0]): [False, False, False, False]})
                admins_dict[chat_id][3] = False
            elif ' '.join(cmd) == 'Послать пост':
                post()
            elif ' '.join(cmd) == 'Послать текст подписчикам':
                admins_dict[chat_id][0] = True
                await bot.sendMessage(chat_id, "Пожалуйста, напишите текст")
            elif ' '.join(cmd) == 'Установить интервал':
                admins_dict[chat_id][1] = True
                await bot.sendMessage(chat_id,
                                      "Текущий интервал: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(interval),
                                          float(interval) / 60,
                                          (float(interval) / 60) / 60)
                                      )
                await bot.sendMessage(chat_id,
                                      "Пожалуйста, укажите время в формате [время (h|m|s)] (например \"1 h\" или \"35 m\")")
            elif ' '.join(cmd) == 'Установить таймер проверки rss':
                admins_dict[chat_id][2] = True
                await bot.sendMessage(chat_id,
                                      "Текущий таймер: {:.2f} секунд, {:.2f} минут, {:.2f} часов".format(
                                          float(check_rate),
                                          float(check_rate) / 60,
                                          (float(check_rate) / 60) / 60)
                                      )
                await bot.sendMessage(chat_id,
                                      "Пожалуйста, укажите время в формате [время (h|m|s)] (например \"1 h\" или \"35 m\")")
            elif ' '.join(cmd) == 'Добавить администратора':
                admins_dict[chat_id][3] = True
                await bot.sendMessage(chat_id, "Пожалуйста, укажите id администратора которого нужно добавить в список")
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
            elif ' '.join(cmd) == 'Закрыть клавиатуру':
                await bot.sendMessage(chat_id, "Хорошо", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))

        elif cmd[0] == "/sub":
            subscribed_users.append(chat_id)
        elif cmd[0] == "/help":
            await bot.sendMessage(chat_id,
                                  """
                                  /sub - подписаться на бота
                                  """)


def main():
    loop = asyncio.get_event_loop()

    loop.create_task(bot.message_loop(handle))
    loop.create_task(get_new_post)
    loop.create_task(post_on_channels)
    loop.create_task(safe_save)

    loop.run_forever()


if __name__ == "__main__":
    main()
