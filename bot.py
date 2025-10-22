import os
from pathlib import Path
from dotenv import load_dotenv
import telebot
import random
import logging
import time
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)


TOKEN = os.getenv("TOKEN")       
VIP_CHAT_ID = os.getenv("VIP_CHAT_ID")
LOG_LEVEL = logging.INFO
CAPTCHA_TIMEOUT = 60                    

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

captcha_data = {}

@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name


    a = random.randint(1, 9)
    b = random.randint(1, 9)
    result = a + b
    captcha_data[user_id] = result

    bot.send_message(
        user_id,
        f" Hello, *{first_name}*!\n\n"
        f"Solve this captcha.:\n"
        f" How much is *{a} + {b}?*\n\n"
        f"Just send the number as a reply."
    )
    logging.info(f"Captcha enviado para {user_id}, resposta={result}")


@bot.message_handler(func=lambda msg: msg.from_user.id in captcha_data)
def check_captcha(message):
    user_id = message.from_user.id
    text = message.text.strip()

    try:
        answer = int(text)
    except ValueError:
        bot.send_message(user_id, "Please send numbers only.")
        return

    correct = captcha_data[user_id]

    if answer == correct:

        try:
            invite = bot.create_chat_invite_link(
                chat_id=VIP_CHAT_ID,
                member_limit=1,                   
                expire_date=int(time.time()) + 60 
            )
            bot.send_message(
                user_id,
                f" Welcome..\n\n👉 {invite.invite_link} valid 1 min / 1 use"
            )
            logging.info(f"Link criado para {user_id}: {invite.invite_link}")

        except Exception as e:
            bot.send_message(user_id, "Error generating link. Please try again later.")
            logging.error(f"Error creating link: {e}")

    else:
        bot.send_message(user_id, "incorrect. Send /start to try again.")
        logging.info(f"User {user_id} failed captcha.")

    captcha_data.pop(user_id, None)

@bot.message_handler(commands=['id'])
def get_id(message):
    chat_id = message.chat.id
    bot.reply_to(message, f"O ID deste chat é: `{chat_id}`", parse_mode="Markdown")

print(" Bot rodando... ")
bot.infinity_polling()
