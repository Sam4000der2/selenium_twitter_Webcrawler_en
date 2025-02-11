import os
import json
import asyncio
import telegram
from telegram.ext import Updater

admin_chat_id = "your_admin_chat_id"  # Customize if you want admin notifications
bot_token = "API:TOKEN"  # Telegram bot token
FILTER_DATA_FILE = 'data.json'  # File containing filter settings

def load_filter_data():
    # Load filter data from JSON file. Customize the returned structure if needed.
    if os.path.exists(FILTER_DATA_FILE):
        with open(FILTER_DATA_FILE, 'r') as file:
            return parse_filter_data(file)
    else:
        return []  # default to empty list if file not found

def parse_filter_data(json_file):
    data_list = []
    json_data = json_file.read()
    data = json.loads(json_data)
    chat_ids = data.get("chat_ids", {})
    filter_rules = data.get("filter_rules", {})
    for chat_id, keywords in filter_rules.items():
        if chat_id in chat_ids:
            entry = {"chat_id": int(chat_id), "keywords": keywords}
            data_list.append(entry)
    return data_list

async def send_telegram_message(bot, chat_id, message):
    await bot.send_message(chat_id=chat_id, text=message)
    
async def send_telegram_picture(bot, chat_id, image_url):
    if image_url:
        await bot.send_photo(chat_id, image_url)

async def main(new_tweets):
    bot = telegram.Bot(token=bot_token)
    filter_data = load_filter_data()
    
    for tweet in new_tweets:
        user = tweet['user']
        username = tweet['username']
        content = tweet['content']
        posted_time = tweet['posted_time']
        source_url = tweet['var_href']  # renamed for clarity
        images = tweet['images']
        extern_urls_as_string = tweet.get('extern_urls_as_string', '')
        message = (
            f"{username} posted a new tweet:\n\n{content}\n\n"
            f"Tweet time: {posted_time}\n\nLink: {source_url}\n\n{extern_urls_as_string}"
        )
        message = message.replace('@', '#')
        
        # Generic filtering logic: notify if no keywords defined or if any defined keyword is found.
        for entry in filter_data:
            chat_id = entry["chat_id"]
            keywords = entry.get("keywords", [])
            if not keywords or any(keyword in content for keyword in keywords):
                await send_telegram_message(bot, chat_id, message)
                # Uncomment to send images as well:
                # for image_url in images:
                #     await send_telegram_picture(bot, chat_id, image_url)
                
if __name__ == '__main__':
    # This script is meant to be imported; do not run directly.
    print("This script should be imported and not run directly.")
