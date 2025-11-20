import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Importações do banco de dados
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

# Configurações do CTK
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ============================================================
#                       LOGIN FRAME
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

        self.title_label = ctk.CTkLabel(
            self.login_container,
            text="Educonnect Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=30, padx=60)

        self.username_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Nome de Usuário",
            width=250
        )
        self.username_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(
            self.login_container,
            placeholder_text="Senha",
            show="*",
            width=250
        )
        self.password_entry.pack(pady=12, padx=10)

        self.login_button = ctk.CTkButton(
            self.login_container,
            text="Entrar",
            command=self.perform_login,
            width=250
        )
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
#                       CRUD FRAME
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

        ctk.CTkLabel(
            self.left_panel,
            text="📚 Alunos Cadastrados",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        self.alunos_list_frame = ctk.CTkScrollableFrame(
            self.left_panel,
            label_text="Lista de Alunos (Clique para Editar)"
        )
        self.alunos_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.alunos_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1), weight=1)

        self.delete_button = ctk.CTkButton(
            action_buttons_frame,
            text="🗑️ Deletar Selecionado",
            fg_color="red",
            hover_color="darkred",
            command=self.deletar_aluno_selecionado
        )
        self.delete_button.grid(row=0, column=0, padx=(0,5), sticky="ew")

        self.logout_button = ctk.CTkButton(
            action_buttons_frame,
            text="🚪 Logout",
            command=lambda: self.app_controller.transition_to_login(True)
        )
        self.logout_button.grid(row=0, column=1, padx=(5,0), sticky="ew")

        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=(10,20), pady=20, sticky="nsew")

        ctk.CTkLabel(
            self.right_panel,
            text="✏️ Cadastro / Edição",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10,15))

        self.entries = {}
        campos = [
            ("Nome", "text"),
            ("Data de Nasc.", "text"),
            ("Série", "int"),
            ("Escola", "text"),
            ("Faltas", "int"),
            ("Renda Familiar (R$)", "float")
        ]

        for label_text, tipo in campos:
            ctk.CTkLabel(self.right_panel, text=label_text + ":").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(self.right_panel, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.entries[label_text] = (entry, tipo)

        self.save_button = ctk.CTkButton(
            self.right_panel,
            text="➕ Salvar Novo Aluno",
            command=self.salvar_aluno
        )
        self.save_button.pack(fill="x", padx=20, pady=(20,10))

        self.clear_button = ctk.CTkButton(
            self.right_panel,
            text="Limpar Formulário",
            command=self.limpar_formulario,
            fg_color="gray",
            hover_color="darkgray"
        )
        self.clear_button.pack(fill="x", padx=20, pady=(0,20))

        # carregamento inicial da lista
        self.carregar_alunos()

    def carregar_alunos(self):
        for widget in self.alunos_list_frame.winfo_children():
            widget.destroy()

        alunos = buscar_alunos()

        headers = ["ID", "Nome", "Série", "Faltas", "Renda"]
        header_frame = ctk.CTkFrame(self.alunos_list_frame, fg_color=("gray80","gray25"))
        header_frame.pack(fill="x", padx=0, pady=(0,5))
        header_frame.columnconfigure((0,1,2,3,4), weight=1)

        for col, text in enumerate(headers):
            ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        for aluno in alunos:
            aluno_id = aluno[0]
            nome = aluno[1]
            serie = aluno[3]
            faltas = aluno[5]
            renda = aluno[6]

            row = ctk.CTkFrame(self.alunos_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=0, pady=2)
            row.columnconfigure((0,1,2,3,4), weight=1)

            row.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

            valores = [aluno_id, nome, serie, faltas, f"R$ {renda:.2f}"]

            for col, val in enumerate(valores):
                label = ctk.CTkLabel(row, text=str(val), anchor="w", cursor="hand2")
                label.grid(row=0, column=col, padx=5, sticky="w")
                label.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

    def carregar_aluno_para_edicao(self, aluno_id):
        aluno = buscar_aluno_por_id(aluno_id)
        if aluno:
            self.aluno_selecionado_id = aluno_id
            dados = aluno[1:]

            for i, key in enumerate(self.entries.keys()):
                entry, _ = self.entries[key]
                entry.delete(0, tk.END)

                valor = str(dados[i])
                if key == "Renda Familiar (R$)":
                    valor = f"{dados[i]:.2f}"

                entry.insert(0, valor)

            self.save_button.configure(
                text="💾 Atualizar Aluno Existente",
                fg_color="orange",
                hover_color="#cc8800"
            )

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
                elif tipo == "float":
                    dados_tipados.append(float(valor))
                else:
                    dados_tipados.append(valor)
            return dados_tipados
        except ValueError:
            messagebox.showerror("Erro", "Série, Faltas e Renda Familiar devem ser números válidos.")
            return None

    def salvar_aluno(self):
        dados_raw = [entry.get() for entry, _ in self.entries.values()]
        dados_validados = self.validar_dados(dados_raw)

        if not dados_validados:
            return

        if self.aluno_selecionado_id:
            sucesso = atualizar_aluno(self.aluno_selecionado_id, *dados_validados)
            acao = "atualizado"
        else:
            sucesso = inserir_aluno(*dados_validados)
            acao = "cadastrado"

        if sucesso:
            messagebox.showinfo("Sucesso", f"Aluno {acao} com sucesso!")
            self.limpar_formulario()
            self.carregar_alunos()
        else:
            messagebox.showerror("Erro", f"Falha ao {acao} o aluno.")

    def deletar_aluno_selecionado(self):
        if not self.aluno_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um aluno na lista para deletar.")
            return

        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o aluno ID {self.aluno_selecionado_id}?"):
            if deletar_aluno(self.aluno_selecionado_id):
                messagebox.showinfo("Sucesso", "Aluno deletado com sucesso!")
                self.limpar_formulario()
                self.carregar_alunos()
            else:
                messagebox.showerror("Erro", "Falha ao deletar aluno.")

# ============================================================
#                           APP
# ============================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Educonnect")
        self.geometry("400x300")
        self.overrideredirect(True)
        self.center_window(400,300)

        criar_tabelas()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        self.show_splash_screen()

    def center_window(self, w, h):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w)//2
        y = (sh - h)//2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def show_splash_screen(self):
        self.clear_container()

        title = ctk.CTkLabel(self.container, text="Educonnect", font=ctk.CTkFont(size=36, weight="bold"))
        title.pack(expand=True, pady=20)

        loading = ctk.CTkLabel(self.container, text="Carregando sistema...", font=ctk.CTkFont(size=14))
        loading.pack(pady=20)

        self.after(3000, self.transition_to_login)

    def transition_to_login(self, from_logout=False):
        self.overrideredirect(False)
        self.title("Educonnect - Login")
        self.geometry("800x600")
        self.center_window(800,600)

        if from_logout:
            self.destroy()
            App().mainloop()
        else:
            self.show_login_screen()

    def show_login_screen(self):
        print("Iniciando Tela de Login...")
        self.clear_container()

        frame = LoginFrame(self.container, self)
        frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Login"] = frame

    def show_crud_screen(self):
        print("Login bem-sucedido! Abrindo Tela CRUD.")
        self.clear_container()

        crud_frame = CRUDFrame(self.container, self)
        crud_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["CRUD"] = crud_frame

        # 🔥 Correção essencial: força o carregamento de alunos
        crud_frame.carregar_alunos()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
