from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from database import (
    criar_tabelas,
    inserir_primeiro_usuario,
    verificar_credenciais,
    inserir_aluno,
    buscar_alunos,
    atualizar_aluno,
    deletar_aluno,
    buscar_aluno_por_id
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ============================================================
# LOGIN FRAME
# ============================================================
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.login_container = ctk.CTkFrame(self)
        self.login_container.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.login_container, text="Educonnect Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30, padx=60)
        self.username_entry = ctk.CTkEntry(self.login_container, placeholder_text="Nome de Usuário", width=250)
        self.username_entry.pack(pady=12, padx=10)
        self.password_entry = ctk.CTkEntry(self.login_container, placeholder_text="Senha", show="*", width=250)
        self.password_entry.pack(pady=12, padx=10)

        ctk.CTkButton(self.login_container, text="Entrar", command=self.perform_login, width=250).pack(pady=20, padx=10)
        self.message_label = ctk.CTkLabel(self.login_container, text="", text_color="red")
        self.message_label.pack(pady=5, padx=10)

        inserir_primeiro_usuario("admin", "admin123")

    def perform_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if verificar_credenciais(username, password):
            self.message_label.configure(text="", text_color="green")
            self.app_controller.show_crud_screen()
        else:
            self.message_label.configure(text="Nome de usuário ou senha incorretos.", text_color="red")


# ============================================================
# CRUD FRAME
# ============================================================
class CRUDFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.aluno_selecionado_id = None

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, padx=(20,10), pady=20, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.left_panel, text="📚 Alunos Cadastrados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.alunos_list_frame = ctk.CTkScrollableFrame(self.left_panel, label_text="Lista de Alunos (Clique para Editar)")
        self.alunos_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.alunos_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1), weight=1)

        self.delete_button = ctk.CTkButton(action_buttons_frame, text="🗑️ Deletar Selecionado", fg_color="red", hover_color="darkred", command=self.deletar_aluno_selecionado)
        self.delete_button.grid(row=0, column=0, padx=(0,5), sticky="ew")

        self.logout_button = ctk.CTkButton(action_buttons_frame, text="🚪 Logout", command=lambda: self.app_controller.transition_to_login(True))
        self.logout_button.grid(row=0, column=1, padx=(5,0), sticky="ew")

        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=(10,20), pady=20, sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="✏️ Cadastro / Edição", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10,15))

        self.entries = {}
        campos = [
            ("RA", "int"),
            ("Nome", "text"),
            ("Data de Nasc.", "date"),
            ("Endereco", "text")
        ]

        for label_text, tipo in campos:
            ctk.CTkLabel(self.right_panel, text=label_text + ":").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(self.right_panel, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.entries[label_text] = (entry, tipo)

        self.save_button = ctk.CTkButton(self.right_panel, text="➕ Salvar Novo Aluno", command=self.salvar_aluno)
        self.save_button.pack(fill="x", padx=20, pady=(20,10))

        self.clear_button = ctk.CTkButton(self.right_panel, text="Limpar Formulário", command=self.limpar_formulario, fg_color="gray", hover_color="darkgray")
        self.clear_button.pack(fill="x", padx=20, pady=(0,20))

        self.carregar_alunos()

    # --- Funções ---
    def carregar_alunos(self):
        for widget in self.alunos_list_frame.winfo_children():
            widget.destroy()

        alunos = buscar_alunos()
        headers = ["ID", "RA", "Nome", "Data Nasc.", "Endereco"]

        header_frame = ctk.CTkFrame(self.alunos_list_frame, fg_color=("gray80","gray25"))
        header_frame.pack(fill="x", padx=0, pady=(0,5))
        header_frame.columnconfigure(tuple(range(len(headers))), weight=1)

        for col, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        for aluno in alunos:
            aluno_id, RA, Nome, DataNascimento, Endereco = aluno
            DataNascimento_str = DataNascimento.strftime("%d/%m/%Y") if DataNascimento else ""

            row = ctk.CTkFrame(self.alunos_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=0, pady=2)
            row.columnconfigure(tuple(range(len(headers))), weight=1)
            row.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

            valores = [aluno_id, RA, Nome, DataNascimento_str, Endereco]
            for col, val in enumerate(valores):
                label = ctk.CTkLabel(row, text=str(val), anchor="w", cursor="hand2")
                label.grid(row=0, column=col, padx=5, sticky="w")
                label.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

    def carregar_aluno_para_edicao(self, aluno_id):
        aluno = buscar_aluno_por_id(aluno_id)
        if aluno:
            self.aluno_selecionado_id = aluno_id
            RA, Nome, DataNascimento, Endereco = aluno[1:]

            for key, (entry, tipo) in self.entries.items():
                entry.delete(0, tk.END)
                if key == "RA":
                    entry.insert(0, RA)
                elif key == "Nome":
                    entry.insert(0, Nome)
                elif key == "Data de Nasc.":
                    entry.insert(0, DataNascimento.strftime("%d%m%Y") if DataNascimento else "")
                elif key == "Endereco":
                    entry.insert(0, Endereco)

            self.save_button.configure(text="💾 Atualizar Aluno Existente", fg_color="orange", hover_color="#cc8800")

    def limpar_formulario(self):
        self.aluno_selecionado_id = None
        for entry, _ in self.entries.values():
            entry.delete(0, tk.END)
        self.save_button.configure(text="➕ Salvar Novo Aluno", fg_color="green", hover_color="darkgreen")

    def validar_dados(self, dados):
        try:
            dados_tipados = []
            for (entry, tipo), valor in zip(self.entries.values(), dados):
                if tipo == "int":
                    dados_tipados.append(int(valor))
                elif tipo == "date":
                    # converte ddmmyyyy -> yyyy-mm-dd
                    dt = datetime.strptime(valor, "%d%m%Y")
                    dados_tipados.append(dt.date())
                else:
                    dados_tipados.append(valor)
            return dados_tipados
        except ValueError:
            messagebox.showerror("Erro", "RA deve ser número e Data de Nasc. deve estar no formato ddmmyyyy.")
            return None

    def salvar_aluno(self):
        dados_raw = [entry.get() for entry, _ in self.entries.values()]
        dados_validados = self.validar_dados(dados_raw)
        if not dados_validados:
            return

        RA, Nome, DataNascimento, Endereco = dados_validados

        if self.aluno_selecionado_id:
            sucesso = atualizar_aluno(self.aluno_selecionado_id, RA, Nome, DataNascimento, Endereco)
            acao = "atualizado"
        else:
            sucesso = inserir_aluno(RA, Nome, DataNascimento, Endereco)
            acao = "cadastrado"

        if sucesso:
            messagebox.showinfo("Sucesso", f"Aluno {acao} com sucesso!")
            self.limpar_fo_
