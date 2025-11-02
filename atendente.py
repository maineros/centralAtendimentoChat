import socket
import threading

# ------------------ FUNÇÃO PARA OUVIR O SERVIDOR ------------------
def ouvir_servidor(sock):
    print("\nSua mensagem: ", end="", flush=True)
    while True:
        try:
            # Recebe dados do servidor
            dados = sock.recv(1024).decode()
            if not dados:
                print(f"\r{' ' * 70}\r\n*** DESCONECTADO do servidor. ***")
                break
            
            # Atendente esperando cliente
            if dados.startswith("FILA:"):
                print(f"\r{' ' * 70}\r(Aguardando clientes...)\nSua mensagem: ", end="", flush=True)
            
            # Quando um cliente é conectado
            elif dados.startswith("CONECTADO:"):
                mensagem_limpa = dados.split("CONECTADO: ")[1] 
                print(f"\r{' ' * 70}\r*** Cliente conectado! {mensagem_limpa} ***\nSua mensagem: ", end="", flush=True)
            
            # Quando a sessão termina
            elif dados.startswith("FIM:"):
                mensagem_limpa = dados.split("FIM:")[1]
                print(f"\r{' ' * 70}\r*** {mensagem_limpa} ***\n*** Chat encerrado. ***\nSua mensagem: ", end="", flush=True)
            
            # Mensagens comuns no chat
            else:
                print(f"\r{' ' * 70}\r{dados}\nSua mensagem: ", end="", flush=True)
        except:
            print(f"\r{' ' * 70}\r\n*** Erro de conexão ou socket fechado. ***")
            break
            
    print("Encerrando thread de escuta...")

# ------------------ CONEXÃO INICIAL COM O SERVIDOR ------------------
try:
    atendente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    atendente_socket.connect(('127.0.0.1', 12345))
except ConnectionRefusedError:
    print("Servidor não encontrado. Encerrando.")
    exit()

# ------------------ IDENTIFICAÇÃO E LOOP PRINCIPAL ------------------
try:
    # 1. Identifica como ATENDENTE
    atendente_socket.send("ATENDENTE".encode())

    # 2. Envia o nome do atendente
    dados_servidor = atendente_socket.recv(1024).decode()
    if dados_servidor == "NOME:":
        meu_nome = input("Digite seu nome de atendente: ")
        atendente_socket.send(meu_nome.encode())
        print("\nVocê está online e aguardando clientes.")
    else:
        raise Exception("Protocolo quebrado")

    # 3. Inicia thread para ouvir o servidor
    thread_escuta = threading.Thread(target=ouvir_servidor, args=(atendente_socket,))
    thread_escuta.start()

    # 4. Loop para envio de mensagens durante o chat
    while thread_escuta.is_alive():
        mensagem = input()
        if atendente_socket.fileno() == -1 or not thread_escuta.is_alive():
            break
        atendente_socket.send(mensagem.encode())

except KeyboardInterrupt:
    print("\nSaindo... (Ctrl+C pressionado). Fechando conexão.")
except Exception as e:
    print(f"\nErro no loop principal: {e}")

# ------------------ LIMPEZA E ENCERRAMENTO ------------------
finally:
    print("Limpando e encerrando conexão...")
    if atendente_socket.fileno() != -1:
        atendente_socket.close()  # Isso força o término da thread de escuta
    thread_escuta.join()  # Aguarda o fim da thread
    print("Aplicação encerrada.")
