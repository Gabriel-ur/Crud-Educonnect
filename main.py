import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# Importações do banco de dados (inclui as novas funções de dados)
from database import (
    criar_tabelas,
    inserir_primeiro_usuario,
    verificar_credenciais,
    inserir_aluno,
    buscar_alunos,
    atualizar_aluno,
    deletar_aluno,
    buscar_aluno_por_id,
    # dados
    buscar_dados,
    buscar_dado_por_id,
    buscar_dado_por_aluno,
    atualizar_dado
)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


# --------------------------- FUNÇÃO AUXILIAR (Data)
def converter_data_para_mysql(valor):
    """
    Recebe 'ddmmyyyy' ou 'dd/mm/yyyy' ou 'dd-mm-yyyy' e retorna 'YYYY-MM-DD' (string).
    Lança ValueError se inválido.
    """
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

        ctk.CTkLabel(
            self.login_container,
            text="Educonnect Login",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=30, padx=60)

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
# CRUD FRAME (agora com duas abas: Alunos | Dados)
# ============================================================
class CRUDFrame(ctk.CTkFrame):
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller

        # armazenadores de seleção
        self.aluno_selecionado_id = None
        self.dado_selecionado_id = None

        # tabview
        self.tabview = ctk.CTkTabview(self, width=1100)
        self.tabview.add("Alunos")
        self.tabview.add("Dados")
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # === Aba ALUNOS ===
        self.tab_alunos = self.tabview.tab("Alunos")
        self._build_alunos_tab(self.tab_alunos)

        # === Aba DADOS ===
        self.tab_dados = self.tabview.tab("Dados")
        self._build_dados_tab(self.tab_dados)

    # ----------------- construção da aba Alunos (mantém comportamentos anteriores) ------------
    def _build_alunos_tab(self, container):
        # layout semelhante ao anterior: left list, right form
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # left panel (lista)
        self.left_panel = ctk.CTkFrame(container)
        self.left_panel.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.left_panel, text="📚 Alunos Cadastrados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        self.alunos_list_frame = ctk.CTkScrollableFrame(self.left_panel, label_text="Lista de Alunos (Clique para Editar)")
        self.alunos_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.alunos_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.delete_button = ctk.CTkButton(action_buttons_frame, text="🗑️ Deletar Aluno", fg_color="red", hover_color="darkred", command=self.deletar_aluno_selecionado)
        self.delete_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # botão para recarregar dados (alunos + dados)
        self.refresh_button = ctk.CTkButton(action_buttons_frame, text="🔄 Recarregar", command=self.carregar_alunos)
        self.refresh_button.grid(row=0, column=1, padx=5, sticky="ew")

        # botão para trocar para aba Dados
        self.abrir_dados_button = ctk.CTkButton(action_buttons_frame, text="📊 Abrir Dados", command=lambda: self.tabview.set("Dados"))
        self.abrir_dados_button.grid(row=0, column=2, padx=(5,0), sticky="ew")

        # right panel (form aluno)
        self.right_panel = ctk.CTkFrame(container)
        self.right_panel.grid(row=0, column=1, padx=(10, 20), pady=10, sticky="nsew")

        ctk.CTkLabel(self.right_panel, text="✏️ Cadastro / Edição (Alunos)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10,15))

        # campos de aluno (mantidos)
        self.entries_aluno = {}
        campos = [("RA", "text"), ("Nome", "text"), ("DataNascimento", "date"), ("Endereco", "text")]

        for label_text, tipo in campos:
            ctk.CTkLabel(self.right_panel, text=label_text + ":", anchor="w").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(self.right_panel, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0,5))
            self.entries_aluno[label_text] = (entry, tipo)

        self.save_button_aluno = ctk.CTkButton(self.right_panel, text="➕ Salvar Novo Aluno", command=self.salvar_aluno)
        self.save_button_aluno.pack(fill="x", padx=20, pady=(20,10))

        self.clear_button_aluno = ctk.CTkButton(self.right_panel, text="Limpar Formulário", command=self.limpar_formulario_aluno, fg_color="gray", hover_color="darkgray")
        self.clear_button_aluno.pack(fill="x", padx=20, pady=(0,20))

        # carrega lista inicial
        self.carregar_alunos()

    # ----------------- construção da aba Dados ------------
    def _build_dados_tab(self, container):
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # left: lista de dados
        self.left_dados = ctk.CTkFrame(container)
        self.left_dados.grid(row=0, column=0, padx=(20,10), pady=10, sticky="nsew")
        self.left_dados.grid_columnconfigure(0, weight=1)
        self.left_dados.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.left_dados, text="📊 Dados (avaliações)", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")

        self.dados_list_frame = ctk.CTkScrollableFrame(self.left_dados, label_text="Lista de Dados (Clique para Editar)")
        self.dados_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.dados_list_frame.grid_columnconfigure(0, weight=1)

        action_buttons_frame = ctk.CTkFrame(self.left_dados, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0,1), weight=1)

        # botão recarregar dados
        ctk.CTkButton(action_buttons_frame, text="🔄 Recarregar Dados", command=self.carregar_dados).grid(row=0, column=0, padx=(0,5), sticky="ew")
        # botão voltar para alunos
        ctk.CTkButton(action_buttons_frame, text="⬅️ Voltar para Alunos", command=lambda: self.tabview.set("Alunos")).grid(row=0, column=1, padx=(5,0), sticky="ew")

        # right: formulário para editar dados (não permite criar novos registros)
        self.right_dados = ctk.CTkFrame(container)
        self.right_dados.grid(row=0, column=1, padx=(10,20), pady=10, sticky="nsew")

        ctk.CTkLabel(self.right_dados, text="✏️ Editar Dados (apenas atualizar existente)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10,12))

        # campos dados
        self.entries_dado = {}
        campos_dado = [
            ("Nota", "int"),
            ("Frequencia", "text"),
            ("Comportamento", "text"),
            ("Engajamento", "text"),
            ("ALUNOS_idALUNOS", "int")
        ]
        for label_text, tipo in campos_dado:
            ctk.CTkLabel(self.right_dados, text=label_text + ":").pack(fill="x", padx=12, pady=(6,0))
            entry = ctk.CTkEntry(self.right_dados, placeholder_text=label_text)
            entry.pack(fill="x", padx=12, pady=(0,4))
            self.entries_dado[label_text] = (entry, tipo)

        # botão atualizar (apenas se selecionou um registro)
        self.save_button_dado = ctk.CTkButton(self.right_dados, text="💾 Atualizar Dado Selecionado", command=self.atualizar_dado_selecionado)
        self.save_button_dado.pack(fill="x", padx=12, pady=(10,6))

        # botão limpar formulário de dados
        self.clear_button_dado = ctk.CTkButton(self.right_dados, text="Limpar Formulário", command=self.limpar_formulario_dado, fg_color="gray", hover_color="darkgray")
        self.clear_button_dado.pack(fill="x", padx=12, pady=(0,10))

        # carrega lista inicial de dados
        self.carregar_dados()

    # ---------------- ALUNOS: funções (mantidas/adaptadas) ----------------
    def carregar_alunos(self):
        # limpa
        for widget in self.alunos_list_frame.winfo_children():
            widget.destroy()

        alunos = buscar_alunos()

        headers = ["ID", "RA", "Nome", "Data Nasc.", "Endereco"]
        # cabeçalho
        header_frame = ctk.CTkFrame(self.alunos_list_frame, fg_color=("gray80","gray25"))
        header_frame.pack(fill="x", padx=0, pady=(0,5))
        header_frame.columnconfigure(tuple(range(len(headers))), weight=1)

        for col, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # linhas
        for aluno in alunos:
            # aluno: (idALUNOS, RA, Nome, DataNascimento, Endereco)
            aluno_id, RA, Nome, DataNascimento, Endereco = aluno
            # formata data para exibição
            try:
                data_str = DataNascimento.strftime("%d/%m/%Y") if DataNascimento else ""
            except Exception:
                data_str = str(DataNascimento) if DataNascimento else ""

            row = ctk.CTkFrame(self.alunos_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=0, pady=2)
            row.columnconfigure(tuple(range(len(headers))), weight=1)

            # seleção ao clicar
            row.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

            valores = [aluno_id, RA, Nome, data_str, Endereco]
            for col, val in enumerate(valores):
                label = ctk.CTkLabel(row, text=str(val), anchor="w", cursor="hand2")
                label.grid(row=0, column=col, padx=5, sticky="w")
                label.bind("<Button-1>", lambda e, id=aluno_id: self.carregar_aluno_para_edicao(id))

    def carregar_aluno_para_edicao(self, aluno_id):
        aluno = buscar_aluno_por_id(aluno_id)
        if aluno:
            self.aluno_selecionado_id = aluno_id
            _, RA, Nome, DataNascimento, Endereco = aluno
            # preenche campos
            for key, (entry, tipo) in self.entries_aluno.items():
                entry.delete(0, tk.END)
                if key == "RA":
                    entry.insert(0, str(RA) if RA is not None else "")
                elif key == "Nome":
                    entry.insert(0, str(Nome) if Nome is not None else "")
                elif key == "DataNascimento":
                    if DataNascimento:
                        try:
                            entry.insert(0, DataNascimento.strftime("%d/%m/%Y"))
                        except Exception:
                            entry.insert(0, str(DataNascimento))
                    else:
                        entry.insert(0, "")
                elif key == "Endereco":
                    entry.insert(0, str(Endereco) if Endereco is not None else "")

            self.save_button_aluno.configure(text="💾 Atualizar Aluno Existente", fg_color="orange", hover_color="#cc8800")

    def limpar_formulario_aluno(self):
        self.aluno_selecionado_id = None
        for entry, _ in self.entries_aluno.values():
            entry.delete(0, tk.END)
        self.save_button_aluno.configure(text="➕ Salvar Novo Aluno", fg_color="green", hover_color="darkgreen")

    def validar_e_tratar_aluno(self):
        """Lê os campos do formulário do aluno, valida e retorna tupla (RA, Nome, DataNascimento, Endereco)"""
        try:
            RA = self.entries_aluno["RA"][0].get().strip()
            Nome = self.entries_aluno["Nome"][0].get().strip()
            DataNascimento_raw = self.entries_aluno["DataNascimento"][0].get().strip()
            Endereco = self.entries_aluno["Endereco"][0].get().strip()

            if not RA:
                raise ValueError("Campo 'RA' vazio.")
            if not Nome:
                raise ValueError("Campo 'Nome' vazio.")
            if not DataNascimento_raw:
                raise ValueError("Campo 'DataNascimento' vazio.")
            # converter DataNascimento
            DataNascimento = converter_data_para_mysql(DataNascimento_raw)
            if not Endereco:
                raise ValueError("Campo 'Endereco' vazio.")

            return (RA, Nome, DataNascimento, Endereco)
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e))
            return None

    def salvar_aluno(self):
        dados = self.validar_e_tratar_aluno()
        if not dados:
            return
        RA, Nome, DataNascimento, Endereco = dados

        if self.aluno_selecionado_id:
            sucesso = atualizar_aluno(self.aluno_selecionado_id, RA, Nome, DataNascimento, Endereco)
            acao = "atualizado"
        else:
            sucesso = inserir_aluno(RA, Nome, DataNascimento, Endereco)
            acao = "cadastrado"

        if sucesso:
            messagebox.showinfo("Sucesso", f"Aluno {acao} com sucesso!")
            self.limpar_formulario_aluno()
            # recarrega também a aba Dados para manter consistência
            self.carregar_alunos()
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", f"Falha ao {acao} o aluno.")

    def deletar_aluno_selecionado(self):
        if not self.aluno_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um aluno na lista para deletar.")
            return
        if messagebox.askyesno("Confirmação", f"Tem certeza que deseja deletar o aluno ID {self.aluno_selecionado_id}?"):
            if deletar_aluno(self.aluno_selecionado_id):
                messagebox.showinfo("Sucesso", "Aluno deletado com sucesso!")
                self.limpar_formulario_aluno()
                self.carregar_alunos()
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", "Falha ao deletar aluno.")


    # ---------------- DADOS: funções ----------------
    def carregar_dados(self):
        # limpa lista
        for widget in self.dados_list_frame.winfo_children():
            widget.destroy()

        dados = buscar_dados()

        headers = ["Nota", "Frequencia", "Comportamento", "Engajamento", "ALUNOS_idALUNOS"]
        header_frame = ctk.CTkFrame(self.dados_list_frame, fg_color=("gray80","gray25"))
        header_frame.pack(fill="x", padx=0, pady=(0,5))
        header_frame.columnconfigure(tuple(range(len(headers))), weight=1)

        for col, text in enumerate(headers):
            ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # cada dado: (idDADOS, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS)
        for dado in dados:
            idDADOS, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = dado
            row = ctk.CTkFrame(self.dados_list_frame, fg_color="transparent")
            row.pack(fill="x", padx=0, pady=2)
            row.columnconfigure(tuple(range(len(headers))), weight=1)

            # bind clique para editar esse dado
            row.bind("<Button-1>", lambda e, id=idDADOS: self.carregar_dado_para_edicao(id))

            valores = [Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS]
            for col, val in enumerate(valores):
                label = ctk.CTkLabel(row, text=str(val), anchor="w", cursor="hand2")
                label.grid(row=0, column=col, padx=5, sticky="w")
                label.bind("<Button-1>", lambda e, id=idDADOS: self.carregar_dado_para_edicao(id))

    def carregar_dado_para_edicao(self, idDADOS):
        dado = buscar_dado_por_id(idDADOS)
        if not dado:
            messagebox.showerror("Erro", "Registro de dados não encontrado.")
            return
        # dado: (idDADOS, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS)
        self.dado_selecionado_id = idDADOS
        _, Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS = dado

        # preenche o formulário de dados
        values = [Nota, Frequencia, Comportamento, Engajamento, ALUNOS_idALUNOS]
        for (key, (entry, tipo)), valor in zip(self.entries_dado.items(), values):
            entry.delete(0, tk.END)
            entry.insert(0, "" if valor is None else str(valor))

        self.save_button_dado.configure(text="💾 Atualizar Dado Selecionado", fg_color="orange", hover_color="#cc8800")

    def limpar_formulario_dado(self):
        self.dado_selecionado_id = None
        for entry, _ in self.entries_dado.values():
            entry.delete(0, tk.END)
        self.save_button_dado.configure(text="💾 Atualizar Dado Selecionado", fg_color=None)

    def validar_campos_dado(self):
        """
        Valida campos do formulário de dados.
        Retorna dicionário com valores convertidos:
            { 'Nota': int, 'Frequencia': str, 'Comportamento': str, 'Engajamento': str, 'ALUNOS_idALUNOS': int }
        Lança ValueError com mensagem específica se algo estiver errado.
        """
        try:
            Nota_raw = self.entries_dado["Nota"][0].get().strip()
            Frequencia = self.entries_dado["Frequencia"][0].get().strip()
            Comportamento = self.entries_dado["Comportamento"][0].get().strip()
            Engajamento = self.entries_dado["Engajamento"][0].get().strip()
            ALUNOS_id_raw = self.entries_dado["ALUNOS_idALUNOS"][0].get().strip()

            if Nota_raw == "":
                raise ValueError("Campo 'Nota' vazio.")
            try:
                Nota = int(Nota_raw)
            except Exception:
                raise ValueError("Campo 'Nota' inválido. Informe um número inteiro.")

            if not Frequencia:
                raise ValueError("Campo 'Frequencia' vazio.")
            if not Comportamento:
                raise ValueError("Campo 'Comportamento' vazio.")
            if not Engajamento:
                raise ValueError("Campo 'Engajamento' vazio.")
            if ALUNOS_id_raw == "":
                raise ValueError("Campo 'ALUNOS_idALUNOS' vazio.")
            try:
                ALUNOS_idALUNOS = int(ALUNOS_id_raw)
            except Exception:
                raise ValueError("Campo 'ALUNOS_idALUNOS' inválido. Informe um número inteiro correspondente a um aluno existente.")

            # verifica se aluno existe
            aluno = buscar_aluno_por_id(ALUNOS_idALUNOS)
            if not aluno:
                raise ValueError(f"Aluno com id {ALUNOS_idALUNOS} não encontrado. Informe um id de aluno existente.")

            return {
                "Nota": Nota,
                "Frequencia": Frequencia,
                "Comportamento": Comportamento,
                "Engajamento": Engajamento,
                "ALUNOS_idALUNOS": ALUNOS_idALUNOS
            }
        except ValueError as e:
            raise

    def atualizar_dado_selecionado(self):
        # Conforme pediu: NÃO criar novos registros nesta aba — apenas atualizar existentes
        if not self.dado_selecionado_id:
            messagebox.showerror("Operação proibida", "Selecione um registro existente de 'Dados' para atualizar. Não é permitido criar novos registros nesta aba.")
            return

        # valida campos
        try:
            campos = self.validar_campos_dado()
        except ValueError as e:
            messagebox.showerror("Erro de validação", str(e))
            return

        # chama update
        sucesso = atualizar_dado(self.dado_selecionado_id,
                                 campos["Nota"],
                                 campos["Frequencia"],
                                 campos["Comportamento"],
                                 campos["Engajamento"],
                                 campos["ALUNOS_idALUNOS"])
        if sucesso:
            messagebox.showinfo("Sucesso", "Registro de dados atualizado com sucesso.")
            self.limpar_formulario_dado()
            self.carregar_dados()
            # recarrega alunos também em caso de dependências
            self.carregar_alunos()
        else:
            messagebox.showerror("Erro", "Falha ao atualizar o registro de dados.")


# ============================================================
# APP
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
        ctk.CTkLabel(self.container, text="Educonnect", font=ctk.CTkFont(size=36, weight="bold")).pack(expand=True, pady=20)
        ctk.CTkLabel(self.container, text="Carregando sistema...", font=ctk.CTkFont(size=14)).pack(pady=20)
        self.after(1500, self.transition_to_login)

    def transition_to_login(self, from_logout=False):
        self.overrideredirect(False)
        self.title("Educonnect - Login")
        self.geometry("1100x650")
        self.center_window(1100,650)

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

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
