import socket
import threading

# ------------------ VARIÁVEIS GLOBAIS ------------------
user_states = {}        # Armazena informações sobre cada conexão (nome, tipo, estado, parceiro)
fila_clientes = []      # Lista de clientes aguardando atendimento
fila_atendentes = []    # Lista de atendentes aguardando cliente
ultima_posicao = {}     # Guarda a última posição conhecida de cada cliente na fila
global_lock = threading.Lock()  # Garante acesso sincronizado entre threads

# ------------------ FUNÇÃO PRINCIPAL DE PAREAMENTO ------------------
def tentar_formar_par():
    global_lock.acquire()

    # Remove conexões inválidas (por segurança)
    fila_clientes[:] = [c for c in fila_clientes if c in user_states]
    fila_atendentes[:] = [a for a in fila_atendentes if a in user_states]

    # Se houver cliente e atendente livres → forma um par
    if fila_clientes and fila_atendentes:
        print("[MATCHMAKER] Formando um par!")
        cliente_conn = fila_clientes.pop(0)
        atendente_conn = fila_atendentes.pop(0)

        cliente_name = user_states[cliente_conn]['name']
        atendente_name = user_states[atendente_conn]['name']

        # Atualiza estados e define o parceiro de cada lado
        user_states[cliente_conn]['state'] = 'chat'
        user_states[cliente_conn]['partner'] = atendente_conn

        user_states[atendente_conn]['state'] = 'chat'
        user_states[atendente_conn]['partner'] = cliente_conn

        # Envia mensagens de confirmação para ambos
        try:
            cliente_conn.send(f"CONECTADO: Você está falando com {atendente_name}.".encode())
        except Exception:
            pass

        try:
            atendente_conn.send(f"CONECTADO: Você está falando com {cliente_name}.".encode())
        except Exception:
            pass

    else:
        # Se ainda não há atendente disponível → atualiza posições na fila
        for i, conn in enumerate(fila_clientes):
            posicao_atual = i + 1
            ultima = ultima_posicao.get(conn)

            # Envia posição apenas se mudou
            if ultima != posicao_atual:
                try:
                    conn.send(f"FILA:{posicao_atual}".encode())
                    ultima_posicao[conn] = posicao_atual
                except Exception:
                    pass

        # Apenas notifica atendentes que estão livres
        for conn in fila_atendentes:
            try:
                conn.send("FILA:OK".encode())
            except Exception:
                pass

    global_lock.release()

# ------------------ DESCONECTAR USUÁRIO ------------------
def handle_disconnect(conn):
    global_lock.acquire()

    # Ignora se o usuário já foi removido
    if conn not in user_states:
        global_lock.release()
        return

    disconnected_user = user_states.pop(conn)
    print(f"[DISCONNECT] {disconnected_user['name']} ({disconnected_user['type']}) desconectou.")

    # Remove da fila (se estiver)
    if conn in fila_clientes:
        fila_clientes.remove(conn)
    if conn in fila_atendentes:
        fila_atendentes.remove(conn)

    # Remove registro de posição se for cliente
    if conn in ultima_posicao:
        ultima_posicao.pop(conn)

    partner_conn = disconnected_user['partner']
    partner_to_close = None

    # Se tinha parceiro ativo → avisa o outro lado
    if partner_conn and partner_conn in user_states:
        partner_state = user_states[partner_conn]
        print(f"[DISCONNECT] Parceiro {partner_state['name']} será notificado.")

        try:
            partner_conn.send(f"FIM:{disconnected_user['name']} desconectou.".encode())
        except Exception:
            pass

        # Se cliente saiu → atendente volta pra fila
        if disconnected_user['type'] == 'CLIENTE':
            print(f"[RE-QUEUE] {partner_state['name']} (Atendente) de volta à fila.")
            partner_state['state'] = 'queue'
            partner_state['partner'] = None
            fila_atendentes.append(partner_conn)

        # Se atendente saiu → cliente é desconectado também
        elif disconnected_user['type'] == 'ATENDENTE':
            print(f"[DISCONNECT] {partner_state['name']} (Cliente) será desconectado.")
            user_states.pop(partner_conn)
            if partner_conn in fila_clientes:
                fila_clientes.remove(partner_conn)
            partner_to_close = partner_conn

    global_lock.release()

    # Fecha o socket do usuário desconectado
    try:
        conn.close()
    except Exception:
        pass

    # Fecha também o parceiro, se necessário
    if partner_to_close:
        try:
            partner_to_close.close()
        except Exception:
            pass

    # Atualiza o sistema após a saída
    tentar_formar_par()

# ------------------ LIDA COM NOVAS CONEXÕES ------------------
def handle_connection(conn, addr):
    # Identificação do tipo e nome do usuário
    try:
        tipo = conn.recv(1024).decode()
        if tipo not in ["CLIENTE", "ATENDENTE"]:
            raise Exception("Tipo inválido")

        conn.send("NOME:".encode())
        nome = conn.recv(1024).decode()
        if not nome:
            raise Exception("Nome vazio")
    except Exception as e:
        print(f"[{addr}] falhou na identificação: {e}")
        conn.close()
        return

    print(f"[CONNECT] {nome} ({tipo}) conectou de {addr}.")

    # Registra o novo usuário e adiciona à fila correspondente
    global_lock.acquire()
    user_states[conn] = {'name': nome, 'type': tipo, 'state': 'queue', 'partner': None}
    if tipo == 'CLIENTE':
        fila_clientes.append(conn)
    else:
        fila_atendentes.append(conn)
    global_lock.release()

    # Tenta formar um par
    tentar_formar_par()

    # Loop de mensagens (chat ativo)
    while True:
        try:
            dados = conn.recv(1024)
            if not dados:
                break  # Desconexão limpa

            global_lock.acquire()
            if conn not in user_states:
                global_lock.release()
                break

            current_state = user_states[conn]
            if current_state['state'] == 'chat':
                partner_conn = current_state['partner']
                if partner_conn and partner_conn in user_states:
                    try:
                        partner_conn.send(f"[{current_state['name']}]: {dados.decode()}".encode())
                    except Exception:
                        pass
            global_lock.release()

        except Exception:
            break

    # Ao sair do loop → desconecta o usuário
    handle_disconnect(conn)

# ------------------ LOOP PRINCIPAL DO SERVIDOR ------------------
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.bind(('0.0.0.0', 12345))
servidor_socket.listen(5)
print("Servidor (v.Fila Inteligente) ouvindo na porta 12345...")

while True:
    conn, addr = servidor_socket.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
