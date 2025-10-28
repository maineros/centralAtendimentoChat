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

cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente_socket.connect(('127.0.0.1', 12345))

cliente_socket.send("CLIENTE".encode())

threading.Thread(target=ouvir_servidor, args=(cliente_socket,)).start()

print("Conectado como CLIENTE. Aguardando na fila...")
try:
    while True:
        mensagem = input("Sua mensagem: ")
        if not cliente_socket.fileno() == -1:
             cliente_socket.send(mensagem.encode())
        else:
             break
except:
    print("Saindo...")

cliente_socket.close()