import telebot

bot = telebot.TeleBot('7634899396:AAHMYtF01bJfVjAK36ASmu61daNAGThkKi8'
                      )  # Substitua pelo seu token real
url = 'https://bot-sofia.onrender.com/7634899396:AAHMYtF01bJfVjAK36ASmu61daNAGThkKi8'
bot.set_webhook(url=url)
