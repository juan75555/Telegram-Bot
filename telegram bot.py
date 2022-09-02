##  Code extracted from documentation of various used libraries and some posts on stackoverflow.
##  Edited by @ruflas on github.com
import logging
import math
from telegram import Update, ForceReply
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from xml.dom.minidom import TypeInfo
import requests
import json
import time
import ping3
import random
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from gtts import gTTS
from playsound import  playsound

# model_name = "microsoft/DialoGPT-large"
model_name = "microsoft/DialoGPT-medium"
# model_name = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = "INSERT TELEGRAM TOKEN"
bot = telegram.Bot(token=TOKEN)   

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

def refresh_data(url):
     resp = requests.get(url)
     data = resp.json()
     return data

def chatid(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    return chat_id

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def say(update: Update, context: CallbackContext) -> None:
    s = context.args
    sf = ""
    for i in range(len(s)):
        sf = sf+" "+s[i]
    update.message.reply_text(str(sf))

def ping(update: Update, context: CallbackContext) -> None:
    web = str(context.args[0])
    try:
        result = float(ping3.ping(web))*1000
        result = round(result)
        result = str(result)
        update.message.reply_text(result+"ms")
    except:
        update.message.reply_text("Ups something happened.")

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def conversation(update: Update, context: CallbackContext) -> None:
    s = context.args
    sf = ""
    for i in range(len(s)):
        sf = sf+" "+s[i]
    for step in range(5):
        # take user input
        # encode the input and add end of string token
        input_ids = tokenizer.encode(sf + tokenizer.eos_token, return_tensors="pt")
        # concatenate new user input with chat history (if there is)
        bot_input_ids = torch.cat([chat_history_ids, input_ids], dim=-1) if step > 0 else input_ids
        # generate a bot response
        chat_history_ids = model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=tokenizer.eos_token_id,
        )
        #print the output
        output = tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    #update.message.reply_text(f"{output}")
    mytext=f"{output}"
    language='en'
    myobj=gTTS(text=mytext,lang=language,slow=True)
    myobj.save("talk.mp3")
    chat_id=chatid(update,context)
    bot.send_audio(chat_id=chat_id, audio=open('talk.mp3', 'rb'))

def cat(update: Update, context: CallbackContext) -> None:
    chat_id=chatid(update,context)
    cat_url = 'https://api.thecatapi.com/v1/images/search'
    cat_url=refresh_data(cat_url)
    cat_url=cat_url[0]
    cat_url=cat_url['url']
    bot.send_photo(chat_id, cat_url)

def main():
    updater = Updater(TOKEN) #Put in TOKEN the Telegram Bot Token.
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("say", say))
    dispatcher.add_handler(CommandHandler("ping", ping))
    dispatcher.add_handler(CommandHandler('talk',	conversation))
    dispatcher.add_handler(CommandHandler('cat',	cat))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    main()
