import socket
import threading

# variaveis globais
user_states = {}        # armazena informacoes sobre cada conexao (nome, tipo, estado, parceiro)
fila_clientes = []      # lista de clientes aguardando atendimento
fila_atendentes = []    # lista de atendentes aguardando cliente
ultima_posicao = {}     # guarda a última posicao conhecida de cada cliente na fila
global_lock = threading.Lock()  # garante acesso sincronizado entre threads

# funcao principal de pareamento
def tentar_formar_par():
    global_lock.acquire()

    # Remove conexões inválidas (por segurança)
    fila_clientes[:] = [c for c in fila_clientes if c in user_states]
    fila_atendentes[:] = [a for a in fila_atendentes if a in user_states]

    # se houver cliente e atendente livres -> forma um par
    if fila_clientes and fila_atendentes:
        print("[MATCHMAKER] Formando um par!")
        cliente_conn = fila_clientes.pop(0)
        atendente_conn = fila_atendentes.pop(0)

        cliente_name = user_states[cliente_conn]['name']
        atendente_name = user_states[atendente_conn]['name']

        # atualiza estados e define o parceiro de cada lado
        user_states[cliente_conn]['state'] = 'chat'
        user_states[cliente_conn]['partner'] = atendente_conn

        user_states[atendente_conn]['state'] = 'chat'
        user_states[atendente_conn]['partner'] = cliente_conn

        # envia mensagens de confirmacao para ambos
        try:
            cliente_conn.send(f"CONECTADO: Você está falando com {atendente_name}.".encode())
        except Exception:
            pass

        try:
            atendente_conn.send(f"CONECTADO: Você está falando com {cliente_name}.".encode())
        except Exception:
            pass

    else:
        # se ainda nao ha atendente disponivel -> atualiza posicoes na fila
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

        # apenas notifica atendentes que estao livres
        for conn in fila_atendentes:
            try:
                conn.send("FILA:OK".encode())
            except Exception:
                pass

    global_lock.release()

# desconectar usuario
def handle_disconnect(conn):
    global_lock.acquire()

    # ignora se o usuario ja foi removido
    if conn not in user_states:
        global_lock.release()
        return

    disconnected_user = user_states.pop(conn)
    print(f"[DISCONNECT] {disconnected_user['name']} ({disconnected_user['type']}) desconectou.")

    # remove da fila (se estiver)
    if conn in fila_clientes:
        fila_clientes.remove(conn)
    if conn in fila_atendentes:
        fila_atendentes.remove(conn)

    # remove registro de posicao se for cliente
    if conn in ultima_posicao:
        ultima_posicao.pop(conn)

    partner_conn = disconnected_user['partner']
    partner_to_close = None

    # se tinha parceiro ativo -> avisa ao outro lado
    if partner_conn and partner_conn in user_states:
        partner_state = user_states[partner_conn]
        print(f"[DISCONNECT] Parceiro {partner_state['name']} será notificado.")

        try:
            partner_conn.send(f"FIM:{disconnected_user['name']} desconectou.".encode())
        except Exception:
            pass

        # se cliente saiu -> atendente volta para a fila
        if disconnected_user['type'] == 'CLIENTE':
            print(f"[RE-QUEUE] {partner_state['name']} (Atendente) de volta à fila.")
            partner_state['state'] = 'queue'
            partner_state['partner'] = None
            fila_atendentes.append(partner_conn)

        # se atendente saiu -> cliente é desconectado tambem
        elif disconnected_user['type'] == 'ATENDENTE':
            print(f"[DISCONNECT] {partner_state['name']} (Cliente) será desconectado.")
            user_states.pop(partner_conn)
            if partner_conn in fila_clientes:
                fila_clientes.remove(partner_conn)
            partner_to_close = partner_conn

    global_lock.release()

    # fecha o socket do usuario desconectado
    try:
        conn.close()
    except Exception:
        pass

    # fecha tambem o parceiro, se necessario
    if partner_to_close:
        try:
            partner_to_close.close()
        except Exception:
            pass

    # atualiza o sistema apos a saida
    tentar_formar_par()

# lida com novas conexoes
def handle_connection(conn, addr):
    # identificacao do tipo e nome do usuario
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

    # registra o novo usuario e adiciona a fila correspondente
    global_lock.acquire()
    user_states[conn] = {'name': nome, 'type': tipo, 'state': 'queue', 'partner': None}
    if tipo == 'CLIENTE':
        fila_clientes.append(conn)
    else:
        fila_atendentes.append(conn)
    global_lock.release()

    # tenta formar um par
    tentar_formar_par()

    # loop de mensagens (chat ativo)
    while True:
        try:
            dados = conn.recv(1024)
            if not dados:
                break  # desconexao limpa

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

    # ao sair do loop -> desconecta o usuario
    handle_disconnect(conn)

# loop principal do servidor
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.bind(('0.0.0.0', 12345))
servidor_socket.listen(5)
print("Servidor (v.Fila Inteligente) ouvindo na porta 12345...")

while True:
    conn, addr = servidor_socket.accept()
    threading.Thread(target=handle_connection, args=(conn, addr)).start()
