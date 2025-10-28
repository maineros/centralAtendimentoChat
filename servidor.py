import socket
import threading

fila_clientes = []
fila_atendentes = []
lock_das_filas = threading.Lock()

servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.bind(('0.0.0.0', 12345))
servidor_socket.listen(5)
print("Servidor de FILA DE ATENDIMENTO ouvindo na porta 12345...")

def tentar_formar_par():
    lock_das_filas.acquire()
    if len(fila_clientes) > 0 and len(fila_atendentes) > 0:
        print("[MATCHMAKER] Formando um par!")
        cliente_conn = fila_clientes.pop(0)
        atendente_conn = fila_atendentes.pop(0)
        threading.Thread(target = repassar_chat, args = (cliente_conn, atendente_conn, "CLIENTE")).start()
        threading.Thread(target = repassar_chat, args = (atendente_conn, cliente_conn, "ATENDENTE")).start()
        cliente_conn.send("CONECTADO: Você está falando com um atendente.".encode())
        atendente_conn.send("CONECTADO: Você está falando com um cliente.".encode())
    lock_das_filas.release()

def repassar_chat(origem, destino, tipo_origem):
    while True:
        try:
            dados = origem.recv(1024)
            if not dados:
                break
            destino.send(dados)
        except:
            break
    
    print (f"[CHAT] {tipo_origem} desconectou.")
    try:
        if tipo_origem == "CLIENTE":
            destino.send("FIM: O Cliente desconectou.".encode())
        else:
            destino.send("FIM: O Atendente desconectou.".encode())
    except:
        pass
    
    origem.close()
    destino.close()

def handle_convidado(conn, addr):
    print(f"Conexão de {addr}. Perguntando quem é...")
    
    try:
        tipo = conn.recv(1024).decode()
        lock_das_filas.acquire()
        
        if tipo == "CLIENTE":
            print(f"[{addr}] é um CLIENTE. Colocando na fila.")
            fila_clientes.append(conn)
            conn.send("FILA: Você está na fila de clientes. Aguarde...".encode())
            
        elif tipo == "ATENDENTE":
            print(f"[{addr}] é um ATENDENTE. Colocando na fila.")
            fila_atendentes.append(conn)
            conn.send("FILA: Você está na fila de atendentes. Aguarde...".encode())
            
        else:
            print(f"[{addr}] não se identificou. Desconectando.")
            conn.send("ERRO: Identifique-se como CLIENTE ou ATENDENTE".encode())
            conn.close()
        
        lock_das_filas.release()
        tentar_formar_par()
        
    except:
        print(f"[{addr}] Erro ou desconexão antes de se identificar.")
        conn.close()

while True:
    conn, addr = servidor_socket.accept()
    threading.Thread(target=handle_convidado, args=(conn, addr)).start()