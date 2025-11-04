#   Projeto Final – Redes de Computadores  
### Sistema de Fila de Atendimento via Socket TCP

**Disciplina:** Redes de Computadores  
**Instituição:** Universidade Federal de Alagoas (UFAL)  
**Período:** 2025.2  
**Linguagem:** Python 3  
**Integrantes:**
- Daniel Araújo  
- Pedro Cabral  
- Laura Mainero  
- Yuri Mota  

---

## Descrição do Projeto

Este projeto implementa um **sistema de atendimento em fila**, onde **clientes** aguardam para conversar com **atendentes**.  
A comunicação entre os participantes ocorre por meio de **sockets TCP** e **threads**, permitindo que múltiplas conversas ocorram simultaneamente.

O sistema é composto por três programas principais:

- **servidor.py** – Responsável por gerenciar as conexões, filas e o repasse das mensagens.  
- **cliente.py** – Representa um cliente que entra na fila de espera para atendimento.  
- *atendente.py** – Representa o atendente que recebe os clientes em ordem de chegada.

---

## Requisitos

- **Python 3.8+**
- Sistema operacional com suporte a terminal (Windows, Linux ou macOS)
- Todos os arquivos no mesmo diretório:
  ```
  servidor.py
  cliente.py
  atendente.py
  ```

---

##  Como Executar

### 1. Inicie o Servidor

Abra um terminal e execute:

```
python servidor.py
```

Você verá a mensagem:

```
Servidor de FILA DE ATENDIMENTO ouvindo na porta 12345...
```

---

### 2. Inicie um Atendente

Em outro terminal, execute:

```
python atendente.py
```

Aparecerá:

```
Digite seu nome de atendente: Ciclano

Você está online e aguardando clientes.
```

---

### 3. Inicie um Cliente

Em outro terminal, execute:

```
python cliente.py
```

Aparecerá:

```
Digite seu nome: Fulano

Procurando um atendente...

(Você é o número X na fila. Por favor, aguarde...)
```

---

### 4. Comunicação

Assim que o servidor formar um par (cliente ↔ atendente), o cliente receberá:

```
*** Conectado! Você está falando com Ciclano. ***
Sua mensagem:
```

E o atendente receberá:
```
*** Cliente conectado! Você está falando com Fulano. ***
Sua mensagem:
```

A partir daí, podem trocar mensagens livremente.  
Digite e pressione **Enter** para enviar.  

Para encerrar a conversa, basta **fechar o terminal** ou **interromper com Ctrl+C**.

---

## Estrutura Interna

- O servidor mantém duas listas (filas):  
  - `fila_clientes`  
  - `fila_atendentes`
- Quando há pelo menos um cliente e um atendente, o servidor cria duas threads:
  - Uma para repassar mensagens do cliente → atendente  
  - Outra para repassar mensagens do atendente → cliente  
- Caso um dos lados desconecte, a sessão é encerrada com uma mensagem do tipo:

  ```
  FIM: O Cliente/Atendente desconectou.
  ```

---

## Conceitos Utilizados

- Comunicação **cliente-servidor** usando **Sockets TCP**  
- **Programação concorrente** com **Threads**  
- Controle de **sincronização com Lock**  
- Manipulação de **mensagens e protocolos de texto**  
- **Tratamento de exceções e desconexões**

---

## Possíveis Melhorias

- Adicionar identificação (nome ou ID) nas mensagens.  
- Implementar uma interface gráfica (Tkinter).  
- Criar logs de conversas no servidor.  
- Adicionar suporte a múltiplos atendentes por cliente (chat em grupo).
