from flask import Flask, request
from flask_ngrok import run_with_ngrok
import telebot

# === CONFIGURAÇÕES ===
TOKEN = "7634899396:AAHMYtF01bJfVjAK36ASmu61daNAGThkKi8"
PRECO = 9.90

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
run_with_ngrok(app)  # inicia com ngrok

# === ROTAS FLASK ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    print("📩 Recebido update do Telegram!")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# === COMANDOS DO BOT ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    print(f"🚀 /start recebido de {message.chat.id}")
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(
        "Obter Conteúdo Premium R$ 9,90", callback_data="comprar"
    )
    markup.add(btn)
    bot.send_message(
        message.chat.id, "Clique abaixo para obter o conteúdo premium:", reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "comprar":
        user_id = call.message.chat.id
        print(f"🛒 Usuário {user_id} clicou em comprar")

        # Simula o código PIX
        codigo_pix = "00020126580014br.gov.bcb.pix0136email@provedor.com52040000530398654059.905802BR5925Nome da Loja Teste6009SAO PAULO62100506abcde6304ABCD"

        markup = telebot.types.InlineKeyboardMarkup()
        btn1 = telebot.types.InlineKeyboardButton("Efetuei o pagamento", callback_data="paguei")
        btn2 = telebot.types.InlineKeyboardButton("QRCode", url="https://api.qrserver.com/v1/create-qr-code/?data=" + codigo_pix)
        markup.add(btn1, btn2)

        bot.send_message(
            user_id,
            f"💳 Copie o código PIX abaixo e efetue o pagamento de R$ {PRECO:.2f}:\n\n`{codigo_pix}`",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif call.data == "paguei":
        user_id = call.message.chat.id
        print(f"💰 Usuário {user_id} afirmou que pagou")
        # Aqui é onde você validará o pagamento real depois
        bot.send_message(
            user_id,
            "✅ Pagamento em análise... em breve você receberá o acesso ao conteúdo!"
        )

# === INÍCIO DO BOT ===
if __name__ == "__main__":
    import requests
    webhook_url = ""  # será preenchido automaticamente com ngrok

    @app.before_first_request
    def setup_webhook():
        global webhook_url
        from flask_ngrok import _ngrok_url
        webhook_url = f"{_ngrok_url}/{TOKEN}"
        print(f"🌐 Configurando webhook para: {webhook_url}")
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}")
        print("✅ Webhook configurado!")

    app.run(port=5000)
