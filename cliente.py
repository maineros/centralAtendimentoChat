import socket
import threading

# ------------------ FUNÇÃO PARA OUVIR O SERVIDOR ------------------
def ouvir_servidor(sock):
    # Mostra o prompt inicial para digitar mensagens
    print("\nSua mensagem: ", end="", flush=True)
    
    while True:
        try:
            # Recebe dados do servidor continuamente
            dados = sock.recv(1024).decode()
            if not dados:
                print("\n*** Desconectado do servidor. ***")
                break
            
            # Mensagem de posição na fila
            if dados.startswith("FILA:"):
                posicao = dados.split(":", 1)[1]
                print(f"\r{' ' * 70}\r(Você é o número {posicao} na fila. Por favor, aguarde...)\nSua mensagem: ", end="", flush=True)

            # Quando o cliente é conectado a um atendente
            elif dados.startswith("CONECTADO:"):
                mensagem_limpa = dados.split("CONECTADO: ")[1] 
                print(f"\r{' ' * 70}\r*** Conectado! {mensagem_limpa} ***\nSua mensagem: ", end="", flush=True)

            # Quando a sessão termina
            elif dados.startswith("FIM:"):
                mensagem_limpa = dados.split("FIM:")[1]
                print(f"\r{' ' * 70}\r*** {mensagem_limpa} ***\n*** Sessão encerrada. ***\n", end="", flush=True)
                break  # Sai do loop e encerra o cliente

            # Mensagens comuns no chat
            else:
                print(f"\r{' ' * 70}\r{dados}\nSua mensagem: ", end="", flush=True)

        except:
            # Se der erro na conexão, encerra
            break
            
    print("Pressione Enter para sair.")
    sock.close()


# ------------------ INÍCIO DA CONEXÃO COM O SERVIDOR ------------------
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    cliente_socket.connect(('127.0.0.1', 12345))
except ConnectionRefusedError:
    print("Não foi possível conectar ao servidor. Verifique se ele está online.")
    exit()

# 1. Identifica o tipo de usuário (CLIENTE)
cliente_socket.send("CLIENTE".encode())

# 2. Envia o nome do cliente quando o servidor pedir
try:
    dados_servidor = cliente_socket.recv(1024).decode()
    if dados_servidor == "NOME:":
        meu_nome = input("Digite seu nome: ")
        cliente_socket.send(meu_nome.encode())
        print("\nProcurando um atendente...")
    else:
        print(f"Erro de protocolo inesperado: {dados_servidor}")
        cliente_socket.close()
        exit()
except Exception as e:
    print(f"Erro ao enviar nome: {e}")
    cliente_socket.close()
    exit()

# 3. Cria uma thread separada para ouvir o servidor
threading.Thread(target=ouvir_servidor, args=(cliente_socket,)).start()

# 4. Loop principal de envio de mensagens (chat ativo)
try:
    while True:
        mensagem = input()
        if cliente_socket.fileno() != -1:
            cliente_socket.send(mensagem.encode())
        else:
            break
except:
    print("Saindo...")

# 5. Fecha o socket ao terminar
cliente_socket.close()
