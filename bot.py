import os
import logging
from neonize.client import NewClient
from neonize.events import MessageEv, ConnectedEv, event
from neonize.utils import log

log.setLevel(logging.INFO)

# O Docker Compose vai injetar a URL do banco aqui
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

client = NewClient(DATABASE_URL, uuid="bot_producao")

@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):
    print("✅ Bot conectado com sucesso via Docker!")

@client.event(MessageEv)
def on_message(client: NewClient, event: MessageEv):
    text = event.Message.conversation or event.Message.extendedTextMessage.text
    if text == "ping":
        client.reply_message("pong! 🏓", event)

client.connect()
event.wait()