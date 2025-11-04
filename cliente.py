import socket
import threading

# funcao para ouvir o servidor
def ouvir_servidor(sock):    
    while True:
        try:
            # recebe os dados do servidor continuamente
            dados = sock.recv(1024).decode()
            if not dados:
                print("\n*** Desconectado do servidor. ***")
                break
            
            # mensagem de posicao na fila
            if dados.startswith("FILA:"):
                posicao = dados.split(":", 1)[1]
                print(f"\r{' ' * 70}\r(Você é o número {posicao} na fila. Por favor, aguarde...)\nSua mensagem: ", end="", flush=True)

            # quando o cliente e conectado a um atendente
            elif dados.startswith("CONECTADO:"):
                mensagem_limpa = dados.split("CONECTADO: ")[1] 
                print(f"\r{' ' * 70}\r*** Conectado! {mensagem_limpa} ***\nSua mensagem: ", end="", flush=True)

            # Quando a sessão termina
            elif dados.startswith("FIM:"):
                mensagem_limpa = dados.split("FIM:")[1]
                print(f"\r{' ' * 70}\r*** {mensagem_limpa} ***\n*** Sessão encerrada. ***\n", end="", flush=True)
                break  # Sai do loop e encerra o cliente

            # mensagens comuns no chat
            else:
                print(f"\r{' ' * 70}\r{dados}\nSua mensagem: ", end="", flush=True)

        except:
            # se der erro na conexao, encerra
            break
            
    print("Pressione Enter para sair.")
    sock.close()


# inicio da conexao com o servidor
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    cliente_socket.connect(('172.172.22.79', 12345))
except ConnectionRefusedError:
    print("Não foi possível conectar ao servidor. Verifique se ele está online.")
    exit()

# 1. identifica o tipo de usuario (cliente)
cliente_socket.send("CLIENTE".encode())

# 2. envia o nome do cliente quando o servidor pedir
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

# cria uma thread separada para ouvir o servidor
threading.Thread(target=ouvir_servidor, args=(cliente_socket,)).start()

# loop principal de envio de mensagens (chat ativo)
try:
    while True:
        mensagem = input()
        if cliente_socket.fileno() != -1:
            cliente_socket.send(mensagem.encode())
        else:
            break
except:
    print("Saindo...")

# fecha o socket ao terminar
cliente_socket.close()
