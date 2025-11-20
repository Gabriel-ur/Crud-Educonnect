import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from database import *

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ===================== LOGIN =====================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(container, text="Educonnect Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30)
        self.username_entry = ctk.CTkEntry(container, placeholder_text="Nome de Usuário", width=250)
        self.username_entry.pack(pady=12)
        self.password_entry = ctk.CTkEntry(container, placeholder_text="Senha", show="*", width=250)
        self.password_entry.pack(pady=12)
        ctk.CTkButton(container, text="Entrar", command=self.perform_login, width=250).pack(pady=20)
        self.message_label = ctk.CTkLabel(container, text="", text_color="red")
        self.message_label.pack(pady=5)

        inserir_primeiro_usuario("admin", "admin123")

    def perform_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if verificar_credenciais(username, password):
            self.message_label.configure(text="", text_color="green")
            self.app_controller.show_crud_screen()
        else:
            self.message_label.configure(text="Nome de usuário ou senha incorretos.", text_color="red")

# ===================== CRUD =====================
class CRUDFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.aluno_selecionado_id = None
        self.dado_selecionado_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Painel Alunos
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.left_panel, text="📚 Alunos", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)
        self.alunos_list_frame = ctk.CTkScrollableFrame(self.left_panel, label_text="Lista de Alunos")
        self.alunos_list_frame.grid(row=1, column=0, sticky="nsew")

        # Painel Dados
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.right_panel.grid_rowconfigure(1, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.right_panel, text="📊 Dados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)
        self.dados_list_frame = ctk.CTkScrollableFrame(self.right_panel, label_text="Lista de Dados")
        self.dados_list_frame.grid(row=1, column=0, sticky="nsew")

        self.carregar_alunos()
        self.carregar_dados()

    def carregar_alunos(self):
        for w in self.alunos_list_frame.winfo_children(): w.destroy()
        alunos = buscar_alunos()
        for aluno in alunos:
            aluno_id, RA, Nome, DataNascimento, Endereco = aluno
            row = ctk.CTkFrame(self.alunos_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            label = ctk.CTkLabel(row, text=f"{aluno_id} | {Nome} | {RA} | {DataNascimento} | {Endereco}", anchor="w")
            label.pack(fill="x", padx=5)
            row.bind("<Button-1>", lambda e, id=aluno_id: self.editar_aluno(id))

    def carregar_dados(self):
        for w in self.dados_list_frame.winfo_children(): w.destroy()
        dados_list = buscar_dados()
        for dado in dados_list:
            idDADOS, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = dado
            row = ctk.CTkFrame(self.dados_list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            label = ctk.CTkLabel(row, text=f"{Nota} | {Frequencia} | {Comportamento} | {Engajamento} | {ALUNOS_idALUNOS}", anchor="w")
            label.pack(fill="x", padx=5)
            row.bind("<Button-1>", lambda e, id=idDADOS: self.editar_dado(id))

    def editar_aluno(self, idALUNOS):
        aluno = buscar_aluno_por_id(idALUNOS)
        if aluno:
            idALUNOS, RA, Nome, DataNascimento, Endereco = aluno
            novo_nome = tk.simpledialog.askstring("Editar Nome", "Nome:", initialvalue=Nome)
            if novo_nome:
                atualizar_aluno(idALUNOS, RA, novo_nome, DataNascimento, Endereco)
                self.carregar_alunos()
                self.carregar_dados()  # Atualiza dados caso algo dependa do aluno

    def editar_dado(self, idDADOS):
        dados = buscar_dados()
        for d in dados:
            if d[0] == idDADOS:
                _, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = d
                break
        else:
            return

        # Atualiza campos
        novo_nota = tk.simpledialog.askinteger("Editar Nota", "Nota:", initialvalue=Nota)
        novo_freq = tk.simpledialog.askstring("Editar Frequencia", "Frequencia:", initialvalue=Frequencia)
        novo_comp = tk.simpledialog.askstring("Editar Comportamento", "Comportamento:", initialvalue=Comportamento)
        novo_eng = tk.simpledialog.askstring("Editar Engajamento", "Engajamento:", initialvalue=Engajamento)
        novo_aluno_id = tk.simpledialog.askinteger("ID do Aluno", "ALUNOS_idALUNOS:", initialvalue=ALUNOS_idALUNOS)

        if novo_nota is None or novo_freq is None or novo_comp is None or novo_eng is None or novo_aluno_id is None:
            return

        if buscar_aluno_por_id(novo_aluno_id) is None:
            messagebox.showerror("Erro", "O ID do aluno informado não existe!")
            return

        atualizar_dado(idDADOS, novo_nota, novo_freq, novo_comp, novo_eng, novo_aluno_id)
        self.carregar_dados()

# ===================== APP =====================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Educonnect")
        self.geometry("1000x600")
        criar_tabelas()
        self.container = ctk.CTkFrame(self)
        self.container.pack(expand=True, fill="both")
        self.frames = {}
        self.show_login_screen()

    def show_login_screen(self):
        for w in self.container.winfo_children(): w.destroy()
        frame = LoginFrame(self.container, self)
        frame.pack(expand=True, fill="both")
        self.frames["Login"] = frame

    def show_crud_screen(self):
        for w in self.container.winfo_children(): w.destroy()
        frame = CRUDFrame(self.container, self)
        frame.pack(expand=True, fill="both")
        self.frames["CRUD"] = frame

if __name__ == "__main__":
    app = App()
    app.mainloop()
