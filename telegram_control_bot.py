import os
import json
import asyncio
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler
from datetime import datetime

# Telegram bot token and data file for chat IDs and filter rules
BOT_TOKEN = "api:token"
DATA_FILE = 'data.json'
admin_id = 000000000  # Replace with your admin chat ID

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        return {"chat_ids": {}, "filter_rules": {}}

def save_data(data):
    if not os.path.exists(DATA_FILE):
        open(DATA_FILE, "a").close()
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

def load_chat_ids():
    data = load_data()
    return data["chat_ids"]

def save_chat_ids(chat_ids):
    data = load_data()
    data["chat_ids"] = chat_ids
    save_data(data)

def load_filter_rules(chat_id):
    data = load_data()
    return data["filter_rules"].get(str(chat_id), [])

def save_filter_rules(chat_id, filter_rules):
    data = load_data()
    data["filter_rules"][str(chat_id)] = filter_rules
    save_data(data)

async def add_filter_rules(bot, message, chat_id):
    rules = message.split()[1:]
    if not rules:
        await send_add_example(bot, chat_id)
    else:
        filter_rules = load_filter_rules(chat_id)
        new_rules = set(rule.strip() for rule in rules if rule.strip())
        filter_rules.extend(new_rules)
        save_filter_rules(chat_id, filter_rules)
        await bot.send_message(chat_id=chat_id, text="Filter rules added.")

async def delete_filter_rules(bot, message, chat_id):
    rules = message.split()[1:]
    if not rules:
        await send_delete_example(bot, chat_id)
    else:
        filter_rules = load_filter_rules(chat_id)
        to_remove = set(rule.strip() for rule in rules if rule.strip())
        filter_rules = [rule for rule in filter_rules if rule not in to_remove]
        save_filter_rules(chat_id, filter_rules)
        await bot.send_message(chat_id=chat_id, text="Filter rules deleted.")

async def delete_all_rules(bot, message, chat_id):
    save_filter_rules(chat_id, [])
    await bot.send_message(chat_id=chat_id, text="All filter rules deleted.")

async def show_all_rules(bot, message, chat_id):
    filter_rules = load_filter_rules(chat_id)
    if filter_rules:
        await bot.send_message(chat_id=chat_id, text="Filter rules:\n" + "\n".join(filter_rules))
    else:
        await bot.send_message(chat_id=chat_id, text="No filter rules found.")

async def start_command(bot, chat_id):
    chat_ids = load_chat_ids()
    if str(chat_id) not in chat_ids:
        chat_ids[str(chat_id)] = True
        save_chat_ids(chat_ids)
        await bot.send_message(chat_id=chat_id, text="Bot started. Welcome!")

async def send_add_example(bot, chat_id):
    help_text = (
        "Example for adding filter keywords:\n\n"
        "/addfilterrules [your keyword]\n"
        "You can add multiple keywords separated by spaces.\n"
        "The bot will forward tweets containing any of these keywords."
    )
    await bot.send_message(chat_id=chat_id, text=help_text)

async def send_delete_example(bot, chat_id):
    help_text = (
        "Example for deleting filter keywords:\n\n"
        "/deletefilterrules [your keyword]\n"
        "The specified keyword(s) will be removed from your filters."
    )
    await bot.send_message(chat_id=chat_id, text=help_text)

async def stop_command(bot, chat_id):
    chat_ids = load_chat_ids()
    if str(chat_id) in chat_ids:
        del chat_ids[str(chat_id)]
        save_chat_ids(chat_ids)
        await bot.send_message(chat_id=chat_id, text="Bot stopped. Goodbye!")

async def help_command(bot, chat_id):
    help_text = (
        "This bot forwards tweets according to your filter keywords.\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/stop - Stop the bot\n"
        "/addfilterrules [rules] - Add filter rules\n"
        "/deletefilterrules [rules] - Delete filter rules\n"
        "/deleteallrules - Delete all filter rules\n"
        "/showallrules - Show your current filter rules\n"
        "/list - Display examples for adding and deleting filters"
    )
    await bot.send_message(chat_id=chat_id, text=help_text)
    
    additional_text = (
        "Expert Tips:\n"
        "- You can add multiple keywords separated by spaces.\n"
        "Examples:\n"
        "/addfilterrules keyword1 keyword2\n"
        "/deletefilterrules keyword1 keyword2"
    )
    await bot.send_message(chat_id=chat_id, text=additional_text)

async def admin_help(bot, chat_id):
    help_text = (
        "Admin Commands:\n"
        "/send [message] - Broadcasts the message to all users (Telegram and Mastodon)\n"
        "/me [message] - Sends a test message only to you\n"
        "/tele [message] - Broadcasts the message to Telegram users\n"
        "/mast [message] - Broadcasts the message to Mastodon users"
    )
    await bot.send_message(chat_id=chat_id, text=help_text)

def service_tweet(message):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    return [{
        "user": "Service",
        "username": "Service",
        "content": message,
        "posted_time": timestamp,
        "source_url": "",
        "images": "",
        "extern_urls": "",
        "images_as_string": "",
        "extern_urls_as_string": ""
    }]

def split_service_message(message, max_length=450):
    parts = []
    while message:
        if len(message) <= max_length:
            parts.append(message)
            break
        split_index = message[:max_length].rfind('. ')
        split_index = split_index + 1 if split_index != -1 else max_length
        parts.append(message[:split_index].strip())
        message = message[split_index:].strip()
    for i in range(len(parts)):
        parts[i] = f"[Part {i+1}]\n\n{parts[i]}"
    return parts

def format_text(message):
    message = message.replace('. ', '.\n')
    message = message.replace(': ', ':\n')
    message = message.replace('! ', '!\n')
    message = message.replace('? ', '?\n')
    message = message.replace('/n', '\n')
    return message

async def admin_send_telegram(message):
    formatted_message = format_text(message)
    service_message = service_tweet(formatted_message)
    try:
        await telegram_bot.main(service_message)
    except Exception as e:
        print(e)

def admin_send_mastodon(message):
    service_message = service_tweet(message)
    message_str = format_text(service_message[0]["content"])
    try:
        if len(message_str) > 470:
            parts = split_service_message(message_str)
            for part in parts:
                mastodon_bot.main(part)
        else:
            mastodon_bot.main(message_str)
    except Exception as e:
        print(e)

async def admin_send_all(message):
    formatted_message = format_text(message)
    service_message = service_tweet(formatted_message)
    try:
        await telegram_bot.main(service_message)
    except Exception as e:
        print(e)
    try:
        message_str = format_text(service_message[0]["content"])
        if len(message_str) > 470:
            parts = split_service_message(message_str)
            for part in parts:
                mastodon_bot.main(part)
        else:
            mastodon_bot.main(message_str)
    except Exception as e:
        print(e)

async def admin_send_me(message):
    message_content = format_text(message)
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    service_message = [{
        "user": "TestUser",
        "username": "TestUser",
        "content": message_content,
        "posted_time": timestamp,
        "source_url": "",
        "images": "",
        "extern_urls": "",
        "images_as_string": "",
        "extern_urls_as_string": ""
    }]
    try:
        await telegram_bot.main(service_message)
    except Exception as e:
        print(e)

async def start_bot():
    bot = telegram.Bot(token=BOT_TOKEN)
    update_id = None
    while True:
        updates = await bot.get_updates(offset=update_id)
        for update in updates:
            update_id = update.update_id + 1
            await process_update(bot, update)

async def process_update(bot, update):
    if update.message:
        message = update.message.text
        chat_id = update.message.chat.id
        if message.startswith('/start'):
            await start_command(bot, chat_id)
            await help_command(bot, chat_id)
        elif message.startswith('/stop'):
            await stop_command(bot, chat_id)
        elif message.startswith('/help'):
            await help_command(bot, chat_id)
        elif message.startswith('/add'):
            await add_filter_rules(bot, message, chat_id)
        elif message.startswith('/deleteallrules'):
            await delete_all_rules(bot, message, chat_id)
        elif message.startswith('/del'):
            await delete_filter_rules(bot, message, chat_id)
        elif message.startswith('/showallrules'):
            await show_all_rules(bot, message, chat_id)
        elif message.startswith('/list'):
            await send_add_example(bot, chat_id)
            await send_delete_example(bot, chat_id)
        elif message.startswith('/') and chat_id == admin_id:
            command, *args = message.split()
            message_content = ' '.join(args)
            if command == '/me' and message_content:
                await admin_send_me(message_content)
            elif command == '/mast' and message_content:
                admin_send_mastodon(message_content)
            elif command == '/tele' and message_content:
                await admin_send_telegram(message_content)
            elif command == '/send' and message_content:
                await admin_send_all(message_content)
            else:
                await admin_help(bot, chat_id)
        elif message.startswith('/'):
            await help_command(bot, chat_id)
        else:
            await start_command(bot, chat_id)
            await help_command(bot, chat_id)

# ...existing code...
if __name__ == "__main__":
    asyncio.run(start_bot())
