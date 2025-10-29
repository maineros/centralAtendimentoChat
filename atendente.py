import socket
import threading

conectado_com_cliente = False
cliente_nome = ""

def ouvir_servidor(sock):
    global conectado_com_cliente, cliente_nome
    while True:
        try:
            dados = sock.recv(1024).decode()
            if not dados:
                print("\n[!] Desconectado do servidor.")
                break
            
            # Detecta quando um cliente conecta
            if dados.startswith("CONECTADO:"):
                conectado_com_cliente = True
                cliente_nome = dados.split(":", 1)[1].strip()
                print(f"\n[✓] Conectado com cliente: {cliente_nome}")
                print("Conectado! Digite sua mensagem:")
            # Detecta quando o cliente encerra a conexão
            elif dados.startswith("FIM:"):
                print(f"\n[!] Conexão encerrada pelo cliente {cliente_nome}")
                conectado_com_cliente = False
                cliente_nome = ""
                break
            else:
                print(f"\n{dados}")
                
        except:
            break
    sock.close()

atendente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
atendente_socket.connect(('127.0.0.1', 12345))

# Identificação
atendente_socket.send("ATENDENTE".encode())
nome = input("Digite seu nome: ")
atendente_socket.send(nome.encode())

threading.Thread(target=ouvir_servidor, args=(atendente_socket,), daemon=True).start()

print(f"Conectado como ATENDENTE ({nome}). Aguardando clientes...")

try:
    while True:
        msg = input()
        
        # Só permite enviar mensagens se estiver conectado com cliente
        if conectado_com_cliente:
            atendente_socket.send(f"[{nome}]: {msg}".encode())
        else:
            if msg.strip():  # Se digitou algo
                print("[!] Aguardando conexão com cliente para enviar mensagens...")
except KeyboardInterrupt:
    print("\nSaindo...")
except:
    print("Erro na conexão...")
finally:
    atendente_socket.close()
