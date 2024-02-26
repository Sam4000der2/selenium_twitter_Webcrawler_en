import asyncio
import os
import telegram
from telegram.ext import Updater
import json

# Telegram-Bot token
bot_token = "API:TOKEN"

#The bot's users and their keywords are stored in the file. Recommend absolute paths.
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return read_json_to_dict(file)
    else:
        return {"chat_id": {}, "keywords": {}}

def read_json_to_dict(json_file):
    data_dict = []
    json_data = json_file.read()  # The content of the TextIOWrapper object is read here
    data = json.loads(json_data)

    chat_ids = data.get("chat_ids", {})
    filter_rules = data.get("filter_rules", {})

    for chat_id, keywords in filter_rules.items():
        # Check whether the chat_id is present in chat_ids
        if chat_id in chat_ids:
            entry = {"chat_id": int(chat_id), "keywords": keywords}
            data_dict.append(entry)

    return data_dict

async def send_telegram_message(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)
    
async def send_telegram_picture (bot, chat_id, images):
    for image_url in images:
        if image_url != "":
            await bot.send_photo(chat_id, image_url)
        

async def main(new_tweets):
    # Initialise the Telegram bot
    bot = telegram.Bot(token=bot_token)
    my_filter = load_data()
    
    # Output of the tweet texts
    for n, tweet in enumerate(new_tweets, start=1):
        user = tweet['user']
        username = tweet['username']
        content = tweet['content']
        posted_time = tweet['posted_time']
        var_href = tweet['var_href']
        images = tweet['images']
        message = f"{username} has posted a new tweet\n"
        message += f"{content}\n"
        message += f"Tweeted at: {posted_time}\n"
        message += f"Link to tweet: {var_href}\n"
        message = message.replace('@', '#')
        
        for entries in my_filter:
            
            chat_id = entries["chat_id"]
            keywords = entries["keywords"]

            if not keywords:
                await send_telegram_message(bot, chat_id, message)
            else:
                for keyword in keywords:
                    if keyword in content:  # Check whether the keyword is included
                        await send_telegram_message(bot, chat_id, message)
                        #await send_telegram_picture(bot, chat_id, images)
        

if __name__ == '__main__':
    #asyncio.run(main(tweet_data))
    print("This script should be imported and not run directly.")
