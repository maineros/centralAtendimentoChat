import socket
import threading

def ouvir_servidor(sock):
    while True:
        try:
            dados = sock.recv(1024).decode()
            if not dados:
                print("\nDesconectado do servidor.")
                break
            print(f"\n[Mensagem Recebida] {dados}")

            if dados.startswith("FIM:"):
                break
        except:
            break
    print("Sessão encerrada.")
    sock.close()

atendente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
atendente_socket.connect(('127.0.0.1', 12345))

atendente_socket.send("ATENDENTE".encode())

threading.Thread(target=ouvir_servidor, args=(atendente_socket,)).start()

print("Conectado como ATENDENTE. Aguardando clientes...")

try:
    while True:
        mensagem = input("Sua mensagem: ")
        if not atendente_socket.fileno() == -1:
             atendente_socket.send(mensagem.encode())
        else:
             break
except:
    print("Saindo...")

atendente_socket.close()