import socket
import threading

# funcao para ouvir o servidor
def ouvir_servidor(sock):
    print("\nSua mensagem: ", end="", flush=True)
    while True:
        try:
            # recebe dados do servidor
            dados = sock.recv(1024).decode()
            if not dados:
                print(f"\r{' ' * 70}\r\n*** DESCONECTADO do servidor. ***")
                break
            
            # atendente esperando cliente
            if dados.startswith("FILA:"):
                print(f"\r{' ' * 70}\r(Aguardando clientes...)\nSua mensagem: ", end="", flush=True)
            
            # quando um cliente e conectado
            elif dados.startswith("CONECTADO:"):
                mensagem_limpa = dados.split("CONECTADO: ")[1] 
                print(f"\r{' ' * 70}\r*** Cliente conectado! {mensagem_limpa} ***\nSua mensagem: ", end="", flush=True)
            
            # quando a sessao termina
            elif dados.startswith("FIM:"):
                mensagem_limpa = dados.split("FIM:")[1]
                print(f"\r{' ' * 70}\r*** {mensagem_limpa} ***\n*** Chat encerrado. ***\nSua mensagem: ", end="", flush=True)
            
            # mensagens comuns no chat
            else:
                print(f"\r{' ' * 70}\r{dados}\nSua mensagem: ", end="", flush=True)
        except:
            print(f"\r{' ' * 70}\r\n*** Erro de conexão ou socket fechado. ***")
            break
            
    print("Encerrando thread de escuta...")

# conexao inicial com o servidor
try:
    atendente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    atendente_socket.connect(('172.172.22.79', 12345))
except ConnectionRefusedError:
    print("Servidor não encontrado. Encerrando.")
    exit()

# identificacao e loop principal
try:
    # identifica como atendente
    atendente_socket.send("ATENDENTE".encode())

    # envia o nome do atendente
    dados_servidor = atendente_socket.recv(1024).decode()
    if dados_servidor == "NOME:":
        meu_nome = input("Digite seu nome de atendente: ")
        atendente_socket.send(meu_nome.encode())
        print("\nVocê está online e aguardando clientes.")
    else:
        raise Exception("Protocolo quebrado")

    # inicia thread para ouvir o servidor
    thread_escuta = threading.Thread(target=ouvir_servidor, args=(atendente_socket,))
    thread_escuta.start()

    # loop para envio de mensagens durante o chat
    while thread_escuta.is_alive():
        mensagem = input()
        if atendente_socket.fileno() == -1 or not thread_escuta.is_alive():
            break
        atendente_socket.send(mensagem.encode())

except KeyboardInterrupt:
    print("\nSaindo... (Ctrl+C pressionado). Fechando conexão.")
except Exception as e:
    print(f"\nErro no loop principal: {e}")

# limpeza e encerramento
finally:
    print("Limpando e encerrando conexão...")
    if atendente_socket.fileno() != -1:
        atendente_socket.close()  # isso forca o termino da thread de escuta
    thread_escuta.join()  # aguarda o fim da thread
    print("Aplicação encerrada.")
