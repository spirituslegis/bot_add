import time

import schedule as schedule
import telethon
from telethon.sync import TelegramClient

api_hash = "1693ef5cf3536775f51ed9090d2ac974"
api_id = "25134689"
phone_number = '+996507553565'

# Задайте путь к файлу, где будет сохраняться сессия
session_file = 'session_name.session'

# Задайте имена пользователей или ID группы
source_group = 'sobeistanbul'
target_group = 'test_post_add'


# Загружаем информацию о последнем посте из файла
def load_last_post_id():
    try:
        with open('last_post_id.txt', 'r') as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return None


# Сохраняем информацию о последнем загруженном посте в файл
def save_last_post_id(post_id):
    with open('last_post_id.txt', 'w') as file:
        file.write(str(post_id))


def get_messages_by_ids(client, chat_id, message_ids):
    messages = []
    chunk_size = 100

    for i in range(0, len(message_ids), chunk_size):
        chunk_ids = message_ids[i:i + chunk_size]
        chunk_messages = client.get_messages(chat_id, ids=chunk_ids)
        messages.extend(chunk_messages)

    return messages


def process_posts():
    with TelegramClient(session_file, api_id, api_hash) as client:
        last_post_id = load_last_post_id()
        messages = client.get_messages(source_group, limit=20)

        media_group = []
        post_text = None
        separator_emoji = '✅✅'
        within_posts = False
        new_posts = []

        for message in messages:
            post_id = message.id
            if last_post_id is not None and post_id <= last_post_id:
                continue

            if separator_emoji in message.text:
                if within_posts:
                    if media_group:
                        new_posts.append((media_group, post_text))

                    media_group = []
                    post_text = None

                within_posts = not within_posts
                continue

            if within_posts:
                if not post_text:
                    post_text = message.text
                else:
                    post_text += '\n' + message.text

                if message.media:
                    if isinstance(message.media, telethon.tl.types.MessageMediaPhoto):
                        media_group.append(message.media.photo)
                    elif isinstance(message.media, telethon.tl.types.MessageMediaDocument):
                        media_group.append(message.media.document)
                    # Другие типы медиа, если необходимо

                if len(media_group) ==10:
                    new_posts.append((media_group, post_text))
                    media_group = []
                    post_text = None

            if last_post_id is not None and post_id > last_post_id:
                last_post_id = post_id

        if within_posts and new_posts:
            for post in new_posts:
                client.send_file(target_group, post[0], caption=post[1])

        save_last_post_id(last_post_id)


process_posts()
schedule.every(20).minutes.do(process_posts)

# Бесконечный цикл для выполнения задачи
while True:
    schedule.run_pending()
    time.sleep(20 * 60)  # Задержка в 20 минут

