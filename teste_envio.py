import os
import sys
import time
from neonize.client import NewClient
from neonize.events import ConnectedEv
from neonize.utils import build_jid

# Puxa a configuração do banco igual ao bot principal
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")

# O número de telefone deve ser passado como argumento ao rodar o script
if len(sys.argv) < 2:
    print("❌ Erro: Forneça o número de telefone com o código do país. Ex: 5511999999999")
    sys.exit(1)

numero_destino = sys.argv[1]

# O Neonize utiliza o mesmo nome de sessão para carregar as credenciais salvas
print("🔄 Conectando ao cliente WhatsApp no banco de dados...")
client = NewClient(DATABASE_URL, uuid="bot_producao")

@client.event(ConnectedEv)
def on_connected(client: NewClient, event: ConnectedEv):
    print("✅ Bot conectado com sucesso!")
    try:
        # Converte o número de telefone string no formato JID interno que o WhatsApp reconhece
        jid = build_jid(numero_destino)
        
        print(f"🚀 Enviando mensagem de teste para {numero_destino}...")
        client.send_message(jid, "Olá! Este é um disparo de teste automático vindo do Docker. 🐳🚀")
        print("✅ Mensagem enviada com sucesso!")

    except Exception as e:
        print(f"❌ Falha ao enviar a mensagem: {e}")

    finally:
        # Desconecta para liberar o processo
        print("🔌 Desconectando...")
        try:
            client.disconnect()
        except Exception as e:
            print(f"Erro ao desconectar: {e}")
        os._exit(0)

# Conecta
client.connect()