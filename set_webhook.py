import telebot

TOKEN = "7634899396:AAFBrnm4Mg-Xne39L8kXpURKh-NYOFyRFxU"
WEBHOOK_URL = "https://bot-sofia.onrender.com/7634899396:AAFBrnm4Mg-Xne39L8kXpURKh-NYOFyRFxU"

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

print("✅ Webhook configurado com sucesso.")
