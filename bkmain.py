from flask import Flask
from threading import Thread
import threading
import telebot
import requests
import time
from datetime import datetime, timedelta

# === CONFIGURAÇÕES ===
TOKEN = "7634899396:AAHMYtF01bJfVjAK36ASmu61daNAGThkKi8"
ASAAS_TOKEN = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6Ojk3ZDAyM2ViLTY0ODgtNDAzYi04YTljLWVjZWQ3ZTk0YTEzZDo6JGFhY2hfYzVmY2I0NmEtMGI0NS00ODUyLWIxNTctNmQxYjE3MzZmYmFm"
CANAL_CHAT_ID = -1007791482092
PRECO = 9.90
bot = telebot.TeleBot(TOKEN)
cobrancas_pendentes = {}


# === INÍCIO AUTOMÁTICO ===
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.chat.id
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("🚀 Iniciar",
                                             callback_data="iniciar")
    markup.add(btn)
    bot.send_message(
        user_id,
        "👋 Seja bem-vindo ao *Prévias da Sofia*! Clique no botão abaixo para começar 🔥",
        parse_mode="Markdown",
        reply_markup=markup)


# === AÇÃO DO BOTÃO INICIAR ===
@bot.callback_query_handler(func=lambda call: call.data == "iniciar")
def iniciar_handler(call):
    boas_vindas(call.message)


# === MENSAGEM E VÍDEO DE BOAS-VINDAS ===
def boas_vindas(message):
    user_id = message.chat.id
    video = open("video_boas_vindas.mp4", "rb")
    bot.send_video(user_id, video)

    texto = ("Oi amor! 😈\n\n"
             "Que bom ter você no meu canal!! 🥰\n\n"
             "Olha o que te aguarda... 🔥\n\n"
             "Tudo aquilo que não posso mostrar em nenhum outro lugar 😏\n\n"
             "Tenha acesso aos meus vídeos mais safados 😜\n\n"
             "Vou fazer você gozar como nunca 💦\n\n"
             "Não perca tempo, te espero no canal de Conteúdo Vip 💋")

    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("💖 Quero Conteúdo Vip",
                                             callback_data="comprar")
    markup.add(btn)

    bot.send_message(user_id, texto, reply_markup=markup)


# === BOTÃO DE COMPRA ===
@bot.callback_query_handler(func=lambda call: call.data == "comprar")
def comprar_handler(call):
    user_id = call.message.chat.id
    nome = call.from_user.first_name or "Usuário"

    bot.send_message(user_id,
                     "💳 Gerando sua cobrança PIX... Aguarde um instante 🔄")

    url = "https://www.asaas.com/api/v3/payments"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_TOKEN,
    }

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
        bot.send_message(
            user_id, "❌ Erro ao gerar cobrança. Tente novamente mais tarde.")
        print("Erro:", data)
        return

    payment_id = data["id"]
    cobrancas_pendentes[user_id] = {
        "payment_id": payment_id,
        "status": "PENDING"
    }

    time.sleep(2)

    pix_url = f"https://www.asaas.com/api/v3/payments/{payment_id}/pixQrCode"
    for tentativa in range(3):
        pix_res = requests.get(pix_url, headers=headers).json()
        if "payload" in pix_res:
            pix_copiaecola = pix_res["payload"]
            break
        else:
            print(f"⚠️ Tentativa {tentativa+1} falhou ao buscar PIX:", pix_res)
            time.sleep(2)
    else:
        bot.send_message(
            user_id, "❌ Erro ao gerar código PIX. Tente novamente mais tarde.")
        return

    # Mensagem inicial com instrução
    bot.send_message(
        user_id,
        f"💳 *Pagamento via PIX*\n\n"
        f"Para acessar o conteúdo exclusivo por 7 dias, efetue o pagamento de *R$ {PRECO:.2f}* usando o código abaixo:"
        , parse_mode="Markdown"
    )

    # Mensagem separada só com o código
    bot.send_message(user_id, f"`{pix_copiaecola}`", parse_mode="Markdown")

    # Botão de já paguei separado
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton("✅ Já paguei", callback_data="paguei")
    markup.add(btn1)

    bot.send_message(user_id, "🔁 Após o pagamento, clique no botão abaixo para confirmar:", reply_markup=markup)


# === VERIFICA PAGAMENTOS A CADA 1 MINUTO ===
def verificar_pagamentos():
    while True:
        for user_id, dados in list(cobrancas_pendentes.items()):
            payment_id = dados["payment_id"]
            url = f"https://www.asaas.com/api/v3/payments/{payment_id}"
            headers = {
                "accept": "application/json",
                "access_token": ASAAS_TOKEN
            }
            res = requests.get(url, headers=headers).json()
            if res.get("status") == "RECEIVED":
                bot.send_message(
                    user_id,
                    "✅ *Pagamento confirmado!*\n\nVocê agora tem acesso ao conteúdo VIP por *7 dias*.\n\nClique no link abaixo para acessar o canal exclusivo:\n👉 https://t.me/+iN6NGTm_LMtlNTYx",
                    parse_mode="Markdown")

                try:
                    bot.approve_chat_join_request(CANAL_CHAT_ID, user_id)
                except:
                    pass

                bot.send_message(
                    user_id,
                    f"⌛ Em 7 dias seu acesso expira. Para renovar, use este link: https://t.me/ConteudoVipBot?start=renovar"
                )
                del cobrancas_pendentes[user_id]
        time.sleep(60)


# === BOTÃO "JÁ PAGUEI" ===
@bot.callback_query_handler(func=lambda call: call.data == "paguei")
def pagamento_handler(call):
    user_id = call.message.chat.id
    bot.send_message(user_id,
                     "⏳ Verificando pagamento... Aguarde até 1 minuto.")


# === CRIA CLIENTE ASAAS ===
def criar_cliente_asaas(user_id, nome):
    url = "https://www.asaas.com/api/v3/customers"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "access_token": ASAAS_TOKEN,
    }
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


# === SERVIDOR FLASK ===
app = Flask('')


@app.route('/')
def home():
    return "Bot rodando!"


def run():
    app.run(host='0.0.0.0', port=8080)


server = Thread(target=run)
server.daemon = True
server.start()

# === INICIA O BOT ===
if __name__ == "__main__":
    thread = threading.Thread(target=verificar_pagamentos)
    thread.daemon = True
    thread.start()

    print("🤖 Bot iniciado com polling...")
    bot.infinity_polling()
