from flask import Flask, request
from threading import Thread
import telebot
import requests
import time
from datetime import datetime, timedelta

# === CONFIGURAÇÕES ===
TOKEN = "7634899396:AAFBrnm4Mg-Xne39L8kXpURKh-NYOFyRFxU"
API_TOKEN = "$aact_prod_000MzkwODA2MWRlMDU2NWM3MzJlNzZmNGZhZGY6Ojk3ZDAyM2ViLTY0ODgtNDAzYi04YTljLWVjZWQ3ZTk0YTEzZDo6JGFhY2hfYzVmY2I0NmEtMGI0NS00ODUyLWIxNTctNmQxYjE3MzZmYmFm"
CANAL_CHAT_ID = -1007791482092
PRECO = 9.90
WEBHOOK_URL = "https://bot-sofia.onrender.com/" + TOKEN

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
cobrancas_pendentes = {}

# === HANDLERS ===
@bot.chat_member_handler()
def on_new_member(message):
    user_id = message.new_chat_member.user.id
    print(f"👤 Novo usuário entrou: {user_id}")

    # Enviar a mensagem de boas-vindas assim que o usuário entra
    try:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton("🚀 Iniciar", callback_data="iniciar")
        markup.add(btn)

        bot.send_message(user_id, "👋 Seja bem-vindo ao *Prévias da Sofia*! Clique no botão abaixo para começar 🔥", parse_mode="Markdown", reply_markup=markup)
        print("✅ Mensagem de boas-vindas enviada automaticamente")
    except Exception as e:
        print(f"❌ Erro ao enviar mensagem de boas-vindas: {e}")



@bot.message_handler(commands=['start'])
def start_handler(message):
    print("🔔 Entrou no start_handler")
    user_id = message.chat.id
    print(f"👤 user_id recebido: {user_id}")

    # Enviando a mensagem de boas-vindas diretamente
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

@bot.callback_query_handler(func=lambda call: call.data == "comprar")
def comprar_handler(call):
    user_id = call.message.chat.id
    nome = call.from_user.first_name or "Usuário"
    bot.send_message(user_id, "💳 Gerando sua cobrança PIX... Aguarde um instante 🔄")

    url = "https://www.asaas.com/api/v3/payments"
    headers = {"accept": "application/json", "content-type": "application/json", "access_token": API_TOKEN}
    due_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    payload = {
        "billingType": "PIX",
        "customer": criar_cliente_asaas(user_id, nome),
        "value": PRECO,
        "dueDate": due_date,
        "description": f"Cobrança Conteúdo Premium para {nome}",
        "externalReference": str(user_id)
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if "id" not in data:
        bot.send_message(user_id, "❌ Erro ao gerar cobrança. Tente novamente mais tarde.")
        print("Erro:", data)
        return

    payment_id = data["id"]
    cobrancas_pendentes[user_id] = {"payment_id": payment_id, "status": "PENDING"}
    time.sleep(2)

    pix_url = f"https://www.asaas.com/api/v3/payments/{payment_id}/pixQrCode"
    pix_res = requests.get(pix_url, headers=headers).json()

    if "payload" not in pix_res:
        bot.send_message(user_id, "❌ Erro ao gerar código PIX. Tente novamente mais tarde.")
        return

    pix_copiaecola = pix_res["payload"]

    bot.send_message(user_id, f"💳 *Pagamento via PIX*\n\nEfetue o pagamento de *R$ {PRECO:.2f}* usando o código abaixo.\n\n🔁 Após o pagamento, clique em *'Já paguei'*. Liberação em até 1 minuto.", parse_mode="Markdown")
    bot.send_message(user_id, f"📲 *Copia e Cola PIX:*\n\n`{pix_copiaecola}`", parse_mode="Markdown")

    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("✅ Já paguei", callback_data="paguei")
    markup.add(btn1)
    bot.send_message(user_id, "Após o pagamento, clique abaixo 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "paguei")
def pagamento_handler(call):
    user_id = call.message.chat.id
    bot.send_message(user_id, "⏳ Verificando pagamento... Aguarde até 1 minuto.")

def criar_cliente_asaas(user_id, nome):
    url = "https://www.asaas.com/api/v3/customers"
    headers = {"accept": "application/json", "content-type": "application/json", "access_token": API_TOKEN}
    payload = {
        "name": nome,
        "email": f"{user_id}@fake.com",
        "cpfCnpj": "14541692813",
        "externalReference": str(user_id)
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if "id" in data:
        return data["id"]
    else:
        print("❌ Erro ao criar cliente:", data)
        raise Exception("Erro ao criar cliente")

# Verificação de pagamentos em paralelo (ACESSO VITALÍCIO)
def verificar_pagamentos():
    while True:
        for user_id, dados in list(cobrancas_pendentes.items()):
            payment_id = dados["payment_id"]
            url = f"https://www.asaas.com/api/v3/payments/{payment_id}"
            headers = {"accept": "application/json", "access_token": API_TOKEN}
            res = requests.get(url, headers=headers).json()
            if res.get("status") == "RECEIVED":
                bot.send_message(user_id, "✅ *Pagamento confirmado!*\n\nVocê agora faz parte do meu canal VIP vitalício! 😈🔥\nAcesse agora:\n👉 https://t.me/+iN6NGTm_LMtlNTYx", parse_mode="Markdown")
                try:
                    bot.approve_chat_join_request(CANAL_CHAT_ID, user_id)
                except Exception as e:
                    print(f"❌ Falha ao aprovar entrada no canal: {e}")
                del cobrancas_pendentes[user_id]
        time.sleep(60)

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

# === CONFIGURA WEBHOOK E THREAD DE PAGAMENTOS ===
if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook configurado para:", WEBHOOK_URL)

    # Start the server to handle webhook requests
    app.run(host="0.0.0.0", port=5000)
