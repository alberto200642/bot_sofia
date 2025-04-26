import os
import telebot
from flask import Flask, request
from telebot import types

TOKEN = '7634899396:AAFBrnm4Mg-Xne39L8kXpURKh-NYOFyRFxU'
WEBHOOK_URL = 'https://teu-dominio-na-render.com/' + TOKEN  # coloque tua URL pública real

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# 📌 /start — boas-vindas com vídeo + botão
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    # Envia vídeo de boas-vindas
    video_path = "video_boas_vindas.mp4"
    with open(video_path, 'rb') as video:
        bot.send_video(chat_id, video, caption="🔥 Seja bem-vindo ao VIP da Sofia! 🔥\n\nClique no botão abaixo pra ver os conteúdos exclusivos 👇")

    # Cria botão
    markup = types.InlineKeyboardMarkup()
    btn_conteudo = types.InlineKeyboardButton("🔥 Quero Conteúdo VIP 🔥", callback_data="conteudo_vip")
    markup.add(btn_conteudo)

    # Envia mensagem com botão
    bot.send_message(chat_id, "Escolha abaixo:", reply_markup=markup)

# 📌 Responde ao botão pressionado
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "conteudo_vip":
        bot.send_message(call.message.chat.id, "✅ Perfeito! Em breve você receberá os conteúdos VIP 🔥")

# 📌 Endpoint default
@app.route("/", methods=["GET"])
def index():
    return "Bot está rodando!"

# 📌 Endpoint do Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# 📌 Configurar webhook na primeira request
@app.before_first_request
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

# 📌 Start app (caso local)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
