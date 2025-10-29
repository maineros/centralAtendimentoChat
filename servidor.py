import socket
import threading

fila_clientes = []
fila_atendentes = []
lock_das_filas = threading.Lock()

servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.bind(('0.0.0.0', 12345))
servidor_socket.listen(5)
print("Servidor ouvindo na porta 12345...")

def tentar_formar_par():
    with lock_das_filas:
        if len(fila_clientes) > 0 and len(fila_atendentes) > 0:
            print("[MATCHMAKER] Formando um par!")
            (cliente_conn, nome_cliente) = fila_clientes.pop(0)
            (atendente_conn, nome_atendente) = fila_atendentes.pop(0)
            
            # Avisos iniciais
            cliente_conn.send(f"CONECTADO: Você está falando com o atendente {nome_atendente}.".encode())
            atendente_conn.send(f"CONECTADO: Você está falando com o cliente {nome_cliente}.".encode())

            # Threads de chat bidirecional
            threading.Thread(target=repassar_chat, args=(cliente_conn, atendente_conn, nome_cliente, "CLIENTE")).start()
            threading.Thread(target=repassar_chat, args=(atendente_conn, cliente_conn, nome_atendente, "ATENDENTE")).start()

def repassar_chat(origem, destino, nome, tipo_origem):
    while True:
        try:
            dados = origem.recv(1024)
            if not dados:
                break
            destino.send(dados)
        except:
            break

    print(f"[CHAT] {tipo_origem} ({nome}) desconectou.")
    try:
        if tipo_origem == "CLIENTE":
            destino.send(f"FIM: O cliente {nome} desconectou.".encode())
        else:
            destino.send(f"FIM: O atendente {nome} desconectou.".encode())
    except:
        pass
    origem.close()
    destino.close()

def handle_convidado(conn, addr):
    print(f"Conexão de {addr}")
    try:
        tipo = conn.recv(1024).decode()
        nome = conn.recv(1024).decode()

        with lock_das_filas:
            if tipo == "CLIENTE":
                print(f"[{addr}] é um CLIENTE chamado {nome}. Adicionando à fila.")
                fila_clientes.append((conn, nome))
                conn.send("FILA: Você está na fila de clientes. Aguarde...".encode())
            elif tipo == "ATENDENTE":
                print(f"[{addr}] é um ATENDENTE chamado {nome}. Adicionando à fila.")
                fila_atendentes.append((conn, nome))
                conn.send("FILA: Você está na fila de atendentes. Aguarde...".encode())
            else:
                conn.send("ERRO: Identifique-se corretamente.".encode())
                conn.close()
                return

        tentar_formar_par()

    except Exception as e:
        print(f"[{addr}] erro: {e}")
        conn.close()

while True:
    conn, addr = servidor_socket.accept()
    threading.Thread(target=handle_convidado, args=(conn, addr)).start()
