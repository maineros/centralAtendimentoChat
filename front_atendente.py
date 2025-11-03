import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class AtendenteGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Atendente - Sistema de Atendimento")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self.socket = None
        self.conectado = False
        self.nome = ""
        
        # Frame de conexão
        self.frame_conexao = tk.Frame(root, bg="#e3f2fd", padx=20, pady=20)
        self.frame_conexao.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.frame_conexao, text="Sistema de Atendimento", 
                font=("Arial", 18, "bold"), bg="#e3f2fd", fg="#1565C0").pack(pady=10)
        
        tk.Label(self.frame_conexao, text="PAINEL DO ATENDENTE", 
                font=("Arial", 14, "bold"), bg="#e3f2fd", fg="#0D47A1").pack(pady=5)
        
        tk.Label(self.frame_conexao, text="Digite seu nome:", 
                font=("Arial", 12), bg="#e3f2fd").pack(pady=5)
        
        self.entrada_nome = tk.Entry(self.frame_conexao, font=("Arial", 12), width=30)
        self.entrada_nome.pack(pady=5)
        self.entrada_nome.bind('<Return>', lambda e: self.conectar())
        
        self.btn_conectar = tk.Button(self.frame_conexao, text="Entrar Online", 
                                     font=("Arial", 12, "bold"), bg="#1976D2", 
                                     fg="white", width=15, command=self.conectar)
        self.btn_conectar.pack(pady=20)
        
        self.label_status = tk.Label(self.frame_conexao, text="", 
                                     font=("Arial", 10), bg="#e3f2fd", fg="#666")
        self.label_status.pack(pady=5)
        
        # Frame de chat (oculto inicialmente)
        self.frame_chat = tk.Frame(root, bg="#f5f5f5")
        
        # Frame superior com status
        frame_status = tk.Frame(self.frame_chat, bg="#1976D2", height=40)
        frame_status.pack(fill=tk.X)
        frame_status.pack_propagate(False)
        
        self.label_status_chat = tk.Label(frame_status, text="Aguardando clientes...", 
                                         font=("Arial", 11, "bold"), bg="#1976D2", 
                                         fg="white")
        self.label_status_chat.pack(pady=10)
        
        # Área de mensagens
        self.texto_chat = scrolledtext.ScrolledText(self.frame_chat, 
                                                    font=("Arial", 10), 
                                                    state=tk.DISABLED, 
                                                    wrap=tk.WORD,
                                                    bg="#ffffff")
        self.texto_chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Frame inferior para entrada de mensagem
        frame_inferior = tk.Frame(self.frame_chat, bg="#f5f5f5")
        frame_inferior.pack(fill=tk.X, padx=10, pady=5)
        
        self.entrada_mensagem = tk.Entry(frame_inferior, font=("Arial", 11))
        self.entrada_mensagem.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entrada_mensagem.bind('<Return>', lambda e: self.enviar_mensagem())
        
        self.btn_enviar = tk.Button(frame_inferior, text="Enviar", 
                                    font=("Arial", 10, "bold"), bg="#1976D2", 
                                    fg="white", width=10, command=self.enviar_mensagem)
        self.btn_enviar.pack(side=tk.RIGHT)
        
        # Protocolo de fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
    
    def conectar(self):
        self.nome = self.entrada_nome.get().strip()
        if not self.nome:
            messagebox.showwarning("Aviso", "Por favor, digite seu nome!")
            return
        
        self.btn_conectar.config(state=tk.DISABLED)
        self.entrada_nome.config(state=tk.DISABLED)
        self.label_status.config(text="Conectando ao servidor...")
        
        # Conecta em uma thread separada
        threading.Thread(target=self.conectar_servidor, daemon=True).start()
    
    def conectar_servidor(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('127.0.0.1', 12345))
            
            # Protocolo de identificação
            self.socket.send("ATENDENTE".encode())
            dados = self.socket.recv(1024).decode()
            
            if dados == "NOME:":
                self.socket.send(self.nome.encode())
                self.conectado = True
                
                # Muda para interface de chat
                self.root.after(0, self.mostrar_chat)
                
                # Inicia thread de escuta
                threading.Thread(target=self.ouvir_servidor, daemon=True).start()
            else:
                raise Exception("Protocolo inesperado")
                
        except ConnectionRefusedError:
            self.root.after(0, lambda: messagebox.showerror("Erro", 
                "Não foi possível conectar ao servidor.\nVerifique se ele está online."))
            self.root.after(0, lambda: self.btn_conectar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.entrada_nome.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.label_status.config(text=""))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao conectar: {e}"))
            self.root.after(0, lambda: self.btn_conectar.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.entrada_nome.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.label_status.config(text=""))
    
    def mostrar_chat(self):
        self.frame_conexao.pack_forget()
        self.frame_chat.pack(fill=tk.BOTH, expand=True)
        self.root.title(f"Atendente - {self.nome}")
        self.adicionar_mensagem_sistema("Você está online e aguardando clientes.", "#4CAF50")
        self.entrada_mensagem.focus()
    
    def ouvir_servidor(self):
        while self.conectado:
            try:
                dados = self.socket.recv(1024).decode()
                if not dados:
                    self.root.after(0, lambda: self.adicionar_mensagem_sistema(
                        "Desconectado do servidor.", "#f44336"))
                    self.root.after(0, lambda: self.label_status_chat.config(
                        text="DESCONECTADO", bg="#f44336"))
                    self.conectado = False
                    break
                
                if dados.startswith("FILA:"):
                    self.root.after(0, lambda: self.label_status_chat.config(
                        text="Aguardando clientes...", bg="#FF9800"))
                
                elif dados.startswith("CONECTADO:"):
                    mensagem = dados.split("CONECTADO: ")[1]
                    self.root.after(0, lambda m=mensagem: self.adicionar_mensagem_sistema(
                        f"✓ Cliente conectado! {m}", "#4CAF50"))
                    self.root.after(0, lambda m=mensagem: self.label_status_chat.config(
                        text=f"Em atendimento: {m.split('Você está falando com ')[1].rstrip('.')}", 
                        bg="#4CAF50"))
                
                elif dados.startswith("FIM:"):
                    mensagem = dados.split("FIM:")[1]
                    self.root.after(0, lambda m=mensagem: self.adicionar_mensagem_sistema(
                        f"{m}\nChat encerrado.", "#f44336"))
                    self.root.after(0, lambda: self.label_status_chat.config(
                        text="Aguardando próximo cliente...", bg="#FF9800"))
                
                else:
                    self.root.after(0, lambda m=dados: self.adicionar_mensagem_recebida(m))
                    
            except:
                self.conectado = False
                break
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def enviar_mensagem(self):
        if not self.conectado:
            return
        
        mensagem = self.entrada_mensagem.get().strip()
        if not mensagem:
            return
        
        try:
            self.socket.send(mensagem.encode())
            self.adicionar_mensagem_enviada(mensagem)
            self.entrada_mensagem.delete(0, tk.END)
        except:
            messagebox.showerror("Erro", "Não foi possível enviar a mensagem.")
            self.conectado = False
    
    def adicionar_mensagem_sistema(self, mensagem, cor="#666"):
        self.texto_chat.config(state=tk.NORMAL)
        self.texto_chat.insert(tk.END, f"[SISTEMA] {mensagem}\n", "sistema")
        self.texto_chat.tag_config("sistema", foreground=cor, font=("Arial", 9, "italic"))
        self.texto_chat.see(tk.END)
        self.texto_chat.config(state=tk.DISABLED)
    
    def adicionar_mensagem_enviada(self, mensagem):
        self.texto_chat.config(state=tk.NORMAL)
        self.texto_chat.insert(tk.END, f"Você: {mensagem}\n", "enviada")
        self.texto_chat.tag_config("enviada", foreground="#1565C0", font=("Arial", 10, "bold"))
        self.texto_chat.see(tk.END)
        self.texto_chat.config(state=tk.DISABLED)
    
    def adicionar_mensagem_recebida(self, mensagem):
        self.texto_chat.config(state=tk.NORMAL)
        self.texto_chat.insert(tk.END, f"{mensagem}\n", "recebida")
        self.texto_chat.tag_config("recebida", foreground="#000000", font=("Arial", 10))
        self.texto_chat.see(tk.END)
        self.texto_chat.config(state=tk.DISABLED)
    
    def fechar_aplicacao(self):
        self.conectado = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AtendenteGUI(root)
    root.mainloop()