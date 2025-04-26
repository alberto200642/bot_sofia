from flask import Flask, request
import telebot
import time

# === CONFIGURAÇÕES ===
TOKEN = "7634899396:AAFBrnm4Mg-Xne39L8kXpURKh-NYOFyRFxU"
WEBHOOK_URL = "https://bot-sofia.onrender.com/" + TOKEN

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === HANDLERS ===
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    print(f"👤 Recebendo mensagem de {user_id}: {message.text}")
    
    # Enviar a mensagem de boas-vindas assim que o usuário enviar qualquer mensagem
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("🚀 Iniciar", callback_data="iniciar")
        markup.add(btn)

        bot.send_message(user_id, "👋 Seja bem-vindo ao *Prévias da Sofia*! Clique no botão abaixo para começar 🔥", parse_mode="Markdown", reply_markup=markup)
        print("✅ Mensagem de boas-vindas enviada com sucesso")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de boas-vindas: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "iniciar")
def iniciar_handler(call):
    print("✅ Clicou em Iniciar")
    boas_vindas(call.message)


def boas_vindas(message):
    user_id = message.chat.id
    print(f"🎥 Enviando vídeo de boas-vindas para {user_id}")
    video = open("video_boas_vindas.mp4", "rb")
    bot.send_video(user_id, video)
    texto = (
        "Oi amor! 😈\n\nQue bom ter você no meu canal!! 🥰\n\nOlha o que te aguarda... 🔥\n\n"
        "Tudo aquilo que não posso mostrar em nenhum outro lugar 😏\n\n"
        "Tenha acesso aos meus vídeos mais safados 😜\n\n"
        "Vou fazer você gozar como nunca 💦")
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("💖 Quero Conteúdo Vip", callback_data="comprar")
    markup.add(btn)
    bot.send_message(user_id, texto, reply_markup=markup)

# === WEBHOOK FLASK ===
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    print("📬 Recebeu update:", update)

    if update.message:
        print("📝 É mensagem de texto")
        bot.process_new_messages([update.message])
    elif update.callback_query:
        print("➡️ É callback query")
        bot.process_new_callback_queries([update.callback_query])

    return "OK", 200

@app.route('/')
def home():
    return "Bot rodando via Webhook!"

# === CONFIGURA WEBHOOK ===
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook configurado para:", WEBHOOK_URL)

    # Start the server to handle webhook requests
    app.run(host="0.0.0.0", port=5000)
