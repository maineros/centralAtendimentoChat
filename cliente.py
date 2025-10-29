import socket
import threading

def ouvir_servidor(sock):
    while True:
        try:
            dados = sock.recv(1024).decode()
            if not dados:
                print("\n[!] Desconectado do servidor.")
                break
            print(f"\n{dados}")
            if dados.startswith("FIM:"):
                break
        except:
            break
    sock.close()

cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente_socket.connect(('127.0.0.1', 12345))

# Identificação
cliente_socket.send("CLIENTE".encode())
nome = input("Digite seu nome: ")
cliente_socket.send(nome.encode())

threading.Thread(target=ouvir_servidor, args=(cliente_socket,)).start()

print(f"Conectado como CLIENTE ({nome}). Aguardando atendimento...")
try:
    while True:
        msg = input()
        cliente_socket.send(f"[{nome}]: {msg}".encode())
except:
    print("Saindo...")
cliente_socket.close()
