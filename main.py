import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from database import (
    criar_tabelas,
    inserir_primeiro_usuario,
    verificar_credenciais,
    inserir_aluno,
    buscar_alunos,
    atualizar_aluno,
    deletar_aluno,
    buscar_aluno_por_id,
    buscar_dados,
    buscar_dado_por_id,
    atualizar_dado
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --------------------------- FUNÇÃO AUXILIAR (Data)
def converter_data_para_mysql(valor):
    if not valor:
        raise ValueError("Data de Nascimento vazia.")
    s = valor.replace("/", "").replace("-", "").strip()
    if len(s) != 8 or not s.isdigit():
        raise ValueError("Formato de data inválido. Use ddmmyyyy ou dd/mm/yyyy.")
    dia = int(s[0:2])
    mes = int(s[2:4])
    ano = int(s[4:8])
    try:
        d = datetime(ano, mes, dia)
        return d.strftime("%Y-%m-%d")
    except Exception:
        raise ValueError("Data inválida (valor impossível).")

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

        ctk.CTkLabel(self.login_container, text="Educonnect Login",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=30, padx=60)

        self.username_entry = ctk.CTkEntry(self.login_container, placeholder_text="Nome de Usuário", width=250)
        self.username_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(self.login_container, placeholder_text="Senha", show="*", width=250)
        self.password_entry.pack(pady=12, padx=10)

        self.login_button = ctk.CTkButton(self.login_container, text="Entrar", command=self.perform_login, width=250)
        self.login_button.pack(pady=20, padx=10)

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
# CRUD FRAME (Alunos + Dados)
# ============================================================
class CRUDFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.aluno_selecionado_id = None
        self.dado_selecionado_id = None

        self.tabview = ctk.CTkTabview(self, width=1100)
        self.tabview.add("Alunos")
        self.tabview.add("Dados")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_alunos_tab(self.tabview.tab("Alunos"))
        self._build_dados_tab(self.tabview.tab("Dados"))

    # ----------------- Aba Alunos -----------------
    def _build_alunos_tab(self, container):
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.left_panel = ctk.CTkFrame(container)
        self.left_panel.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.left_panel, text="📚 Alunos Cadastrados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        self.alunos_list_frame = ctk.CTkScrollableFrame(self.left_panel, label_text="Lista de Alunos (Clique para Editar)")
        self.alunos_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.alunos_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1,2), weight=1)

        self.delete_button = ctk.CTkButton(action_buttons_frame, text="🗑️ Deletar Aluno", fg_color="red", hover_color="darkred", command=self.deletar_aluno_selecionado)
        self.delete_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.refresh_button = ctk.CTkButton(action_buttons_frame, text="🔄 Recarregar", command=self.carregar_alunos)
        self.refresh_button.grid(row=0, column=1, padx=5, sticky="ew")
        self.abrir_dados_button = ctk.CTkButton(action_buttons_frame, text="📊 Abrir Dados", command=lambda: self.tabview.set("Dados"))
        self.abrir_dados_button.grid(row=0, column=2, padx=(5,0), sticky="ew")

        self.right_panel = ctk.CTkFrame(container)
        self.right_panel.grid(row=0, column=1, padx=(10,20), pady=10, sticky="nsew")
        ctk.CTkLabel(self.right_panel, text="✏️ Cadastro / Edição (Alunos)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10,15))

        self.entries_aluno = {}
        campos = [("RA","text"),("Nome","text"),("DataNascimento","date"),("Endereco","text")]
        for label_text, tipo in campos:
            ctk.CTkLabel(self.right_panel, text=label_text+":", anchor="w").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(self.right_panel, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.entries_aluno[label_text] = (entry, tipo)

        self.save_button_aluno = ctk.CTkButton(self.right_panel, text="➕ Salvar Novo Aluno", command=self.salvar_aluno)
        self.save_button_aluno.pack(fill="x", padx=20, pady=(20,10))
        self.clear_button_aluno = ctk.CTkButton(self.right_panel, text="Limpar Formulário", command=self.limpar_formulario_aluno, fg_color="gray", hover_color="darkgray")
        self.clear_button_aluno.pack(fill="x", padx=20, pady=(0,20))

        self.carregar_alunos()

    # ----------------- Aba Dados -----------------
    def _build_dados_tab(self, container):
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        self.left_dados = ctk.CTkFrame(container)
        self.left_dados.grid(row=0, column=0, padx=(20,10), pady=10, sticky="nsew")
        self.left_dados.grid_columnconfigure(0, weight=1)
        self.left_dados.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.left_dados, text="📊 Dados (avaliações)", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.dados_list_frame = ctk.CTkScrollableFrame(self.left_dados, label_text="Lista de Dados")
        self.dados_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.dados_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_dados, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1), weight=1)
        self.refresh_button_dados = ctk.CTkButton(action_buttons_frame, text="🔄 Recarregar", command=self.carregar_dados)
        self.refresh_button_dados.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.clear_button_dados = ctk.CTkButton(action_buttons_frame, text="Limpar Seleção", command=self.limpar_formulario_dados)
        self.clear_button_dados.grid(row=0, column=1, padx=(5,0), sticky="ew")

        self.right_dados = ctk.CTkFrame(container)
        self.right_dados.grid(row=0, column=1, padx=(10,20), pady=10, sticky="nsew")
        ctk.CTkLabel(self.right_dados, text="✏️ Cadastro / Edição (Dados)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10,15))

        self.entries_dado = {}
        campos = [("Nota","text"),("Frequencia","text"),("Comportamento","text"),("Engajamento","text"),("ALUNOS_idALUNOS","text")]
        for label_text, tipo in campos:
            ctk.CTkLabel(self.right_dados, text=label_text+":", anchor="w").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(self.right_dados, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.entries_dado[label_text] = (entry, tipo)

        self.save_button_dado = ctk.CTkButton(self.right_dados, text="💾 Salvar Dados", command=self.salvar_dado)
        self.save_button_dado.pack(fill="x", padx=20, pady=(20,10))

        self.carregar_dados()

    # ----------------- Funções CRUD Alunos -----------------
    def carregar_alunos(self):
        for widget in self.alunos_list_frame.winfo_children():
            widget.destroy()
        alunos = buscar_alunos()
        for aluno in alunos:
            idALUNOS, RA, Nome, DataNascimento, Endereco = aluno
            text = f"{idALUNOS} | {RA} | {Nome} | {DataNascimento} | {Endereco}"
            btn = ctk.CTkButton(self.alunos_list_frame, text=text, anchor="w", command=lambda a=idALUNOS: self.selecionar_aluno(a))
            btn.pack(fill="x", padx=5, pady=2)

    def salvar_aluno(self):
        try:
            dados = {}
            for key, (entry, tipo) in self.entries_aluno.items():
                val = entry.get().strip()
                if tipo == "date":
                    val = converter_data_para_mysql(val)
                dados[key] = val
            if self.aluno_selecionado_id:
                atualizar_aluno(self.aluno_selecionado_id, **dados)
                self.aluno_selecionado_id = None
            else:
                inserir_aluno(**dados)
            self.limpar_formulario_aluno()
            self.carregar_alunos()
            self.carregar_dados()  # atualiza aba dados
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def deletar_aluno_selecionado(self):
        if self.aluno_selecionado_id:
            deletar_aluno(self.aluno_selecionado_id)
            self.aluno_selecionado_id = None
            self.carregar_alunos()
            self.carregar_dados()  # atualiza aba dados
            self.limpar_formulario_aluno()

    def selecionar_aluno(self, idALUNOS):
        aluno = buscar_aluno_por_id(idALUNOS)
        if aluno:
            self.aluno_selecionado_id = idALUNOS
            _, RA, Nome, DataNascimento, Endereco = aluno
            for key, (entry, tipo) in self.entries_aluno.items():
                if tipo == "date":
                    DataNascimento = DataNascimento.strftime("%d/%m/%Y") if DataNascimento else ""
                    entry.delete(0, "end")
                    entry.insert(0, DataNascimento)
                else:
                    entry.delete(0, "end")
                    entry.insert(0, locals()[key])
            self.save_button_aluno.configure(text="💾 Atualizar Aluno")

    def limpar_formulario_aluno(self):
        for entry, tipo in self.entries_aluno.values():
            entry.delete(0, "end")
        self.save_button_aluno.configure(text="➕ Salvar Novo Aluno")
        self.aluno_selecionado_id = None

    # ----------------- Funções CRUD Dados -----------------
    def carregar_dados(self):
        for widget in self.dados_list_frame.winfo_children():
            widget.destroy()
        dados = buscar_dados()
        for dado in dados:
            idDADOS, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = dado
            text = f"{idDADOS} | {Nota} | {Frequencia} | {Comportamento} | {Engajamento} | {ALUNOS_idALUNOS}"
            btn = ctk.CTkButton(self.dados_list_frame, text=text, anchor="w",
                                command=lambda d=idDADOS: self.selecionar_dado(d))
            btn.pack(fill="x", padx=5, pady=2)

    def salvar_dado(self):
        try:
            dados = {}
            for key, (entry, tipo) in self.entries_dado.items():
                val = entry.get().strip()
                dados[key] = val
            if self.dado_selecionado_id:
                atualizar_dado(self.dado_selecionado_id, **dados)
                self.dado_selecionado_id = None
            self.limpar_formulario_dados()
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def selecionar_dado(self, idDADOS):
        dado = buscar_dado_por_id(idDADOS)
        if dado:
            self.dado_selecionado_id = idDADOS
            _, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = dado
            for key, (entry, tipo) in self.entries_dado.items():
                entry.delete(0, "end")
                entry.insert(0, locals()[key])
            self.save_button_dado.configure(text="💾 Atualizar Dado")

    def limpar_formulario_dados(self):
        for entry, tipo in self.entries_dado.values():
            entry.delete(0, "end")
        self.save_button_dado.configure(text="💾 Salvar Dados")
        self.dado_selecionado_id = None

# ============================================================
# APP CONTROLLER
# ============================================================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Educonnect")
        self.geometry("1200x700")
        self.login_frame = LoginFrame(self, self)
        self.crud_frame = CRUDFrame(self, self)
        self.login_frame.pack(fill="both", expand=True)

    def show_crud_screen(self):
        self.login_frame.pack_forget()
        self.crud_frame.pack(fill="both", expand=True)

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    criar_tabelas()
    app = App()
    app.mainloop()
