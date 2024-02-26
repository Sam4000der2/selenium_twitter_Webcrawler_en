import asyncio
import os
import json
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler

# Telegram secret access bot token
BOT_TOKEN = "api:token"

#The bot's users and their keywords are stored in the file. Recommend absolute paths.
DATA_FILE = 'data.json'

# Function for loading the data from the file
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    else:
        return {"chat_ids": {}, "filter_rules": {}}

# Function for saving the data to the file
def save_data(data):
    #Check if the file exists and read existing tweets
    if not os.path.exists(DATA_FILE):
        # If the file does not exist, create it
        open(DATA_FILE, "a").close()  # Create the file if it does not exist

    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Function for loading the chat IDs from the data
def load_chat_ids():
    data = load_data()
    return data["chat_ids"]

# Function for saving the chat IDs in the data
def save_chat_ids(chat_ids):
    data = load_data()
    data["chat_ids"] = chat_ids
    save_data(data)

# Function for loading the filter rules from the data
def load_filter_rules(chat_id):
    data = load_data()
    return data["filter_rules"].get(str(chat_id), [])

# Function for saving the filter rules in the data
def save_filter_rules(chat_id, filter_rules):
    data = load_data()
    data["filter_rules"][str(chat_id)] = filter_rules
    save_data(data)

# Function for adding filter rules
async def add_filter_rules(bot, message, chat_id):
    rules = message.split()[1:]  # Extract filter rules from the message
    if not rules:
        await add_exempel_command(bot, chat_id)
    else:
        filter_rules = load_filter_rules(chat_id)
        new_rules = set(filter(lambda x: x.strip(), rules))
        filter_rules.extend(new_rules)
        save_filter_rules(chat_id, filter_rules)
        await bot.send_message(chat_id=chat_id, text="Filter rules added.")

# Function for deleting filter rules
async def delete_filter_rules(bot, message, chat_id):
    rules = message.split()[1:]  # Extract filter rules from the message
    if not rules:
        await del_exempel_command(bot, chat_id)
    else:
        filter_rules = load_filter_rules(chat_id)
        to_remove = set(filter(lambda x: x.strip(), rules))
        filter_rules = [rule for rule in filter_rules if rule not in to_remove]
        save_filter_rules(chat_id, filter_rules)
        await bot.send_message(chat_id=chat_id, text="Filter rules deleted.")

# Function for deleting all filter rules
async def delete_all_rules(bot, message, chat_id):
    save_filter_rules(chat_id, [])
    await bot.send_message(chat_id=chat_id, text="All filter rules deleted.")

# Function for displaying all filter rules
async def show_all_rules(bot,message, chat_id):
    filter_rules = load_filter_rules(chat_id)
    if filter_rules:
        await bot.send_message(chat_id=chat_id, text="Filter rules:\n" + '\n'.join(filter_rules))
    else:
        await bot.send_message(chat_id=chat_id, text="No filter rules found.")
        
# Function for the /start command to save the chat ID
async def start_command(bot, chat_id):
    chat_ids = load_chat_ids()
    if str(chat_id) not in chat_ids:
        chat_ids[str(chat_id)] = True
        save_chat_ids(chat_ids)
        await bot.send_message(chat_id=chat_id, text="Bot started. Welcome!")
        
        
# Function for the /start command to save the chat ID
async def add_example_command(bot, chat_id):
    help_text = "Example of the function to add filter keywords:\n\n"
    help_text += "/addfilterrules [your keyword]\n"
    help_text += "/addfilterrules #S42\n"
    help_text += "/addfilterrules Heerstr\n"
    help_text += "/addfilterrules Alexanderplatz\n"
    help_text += "/addfilterrules #M4_BVG\n"
    help_text += "/addfilterrules #100_BVG\n"
    help_text += "/addfilterrules #U1_BVG\n"
    help_text += "\n"
    help_text += "In this example, the bot forwards you all messages for the U1, 100 (Bus), M4 (Tram), and S42 lines. Also for Alexanderplatz and Heerstr.\n"
    help_text += "\n"
    help_text += "Note: This is a free text. As long as the keyword is included in the incoming tweets, you'll receive a message."
    
    await bot.send_message(chat_id=chat_id, text=help_text)
    
async def del_example_command(bot, chat_id):
    help_text = "Example of the function to delete filter keywords:\n\n"
    help_text += "/deletefilterrules [your keyword]\n"
    help_text += "/deletefilterrules #S42\n"
    help_text += "/deletefilterrules Heerstr\n"
    help_text += "/deletefilterrules Alexanderplatz\n"
    help_text += "/deletefilterrules #M4_BVG\n"
    help_text += "/deletefilterrules #100_BVG\n"
    help_text += "/deletefilterrules #U1_BVG\n"
    help_text += "\n"
    help_text += "In this example, the bot deletes the search terms for the U1, 100 (Bus), M4 (Tram), and S42 lines. Also for Alexanderplatz and Heerstr.\n"
    help_text += "\n"
    help_text += "This means you won't receive messages for the specific terms anymore. Pay attention to the spelling.\n"
    help_text += "\n"
    help_text += "If in doubt, use /showallrules to retrieve your existing filter terms. If no terms are set, you will continue to receive all messages."
    
    await bot.send_message(chat_id=chat_id, text=help_text)

# Function for the /stop command to delete the chat ID
async def stop_command(bot, chat_id):
    chat_ids = load_chat_ids()
    if str(chat_id) in chat_ids:
        del chat_ids[str(chat_id)]
        save_chat_ids(chat_ids)
        await bot.send_message(chat_id=chat_id, text="Bot stopped. Goodbye!")


# Function for the /help command to display all available commands
async def help_command(bot, chat_id):
    help_text = "The bot forwards all tweets from #SbahnBerlin #BVG_Bus #BVG_UBahn #BVG_Tram #VIZ_Berlin to the user.\n\n"
    help_text += "Unless the user uses the bot's filter keyword function. Then only corresponding tweets are forwarded.\n\n"
    help_text += "/start - Start the bot\n/stop - Stop the bot\n/addfilterrules [rules] - Add filter rules\n/deletefilterrules [rules] - Delete filter rules\n/deleteallrules - Delete all filter rules\n/showallrules - Show all filter rules\n"
    help_text += "/list - Provides detailed instructions for the add and delete filter functions."
    await bot.send_message(chat_id=chat_id, text=help_text)
    
    help_text = "Expert tips:\n"
    help_text += "\n"
    help_text += "Multiple keywords can be passed to the bot simultaneously (separated by spaces)\n"
    help_text += "\n"
    help_text += "The functions for adding and deleting filter rules support shortened forms of the command.\n"
    help_text += "\n"
    help_text += "Example:\n"
    help_text += "/addrule [your keywords]\n"
    help_text += "/delrule [your keywords]\n"
    await bot.send_message(chat_id=chat_id, text=help_text)

# Function to start the bot
async def start_bot():
    bot = telegram.Bot(token=BOT_TOKEN)
    update_id = None
    while True:
        updates = await bot.get_updates(offset=update_id)
        for update in updates:
            update_id = update.update_id + 1
            await process_update(bot, update)

# Function for processing an update
async def process_update(bot, update):
    if update.message:
        message = update.message.text
        chat_id = update.message.chat.id
        if message.startswith('/start'):
            await start_command(bot, chat_id)
            await help_command(bot, chat_id)
        elif message.startswith('/stop'):
            await stop_command(bot, chat_id)
        elif message.startswith('/hilfe'):
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
            await add_exempel_command(bot, chat_id)
            await del_exempel_command(bot, chat_id)
        elif message.startswith('/'):
            await help_command(bot, chat_id)
        else:
            await start_command(bot, chat_id)
            await help_command(bot, chat_id)

# Ausführen des Bots
if __name__ == "__main__":
    asyncio.run(start_bot())
