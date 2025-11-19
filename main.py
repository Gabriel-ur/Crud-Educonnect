import customtkinter as ctk
import tkinter as tk # Ainda precisamos do tkinter padrão para Messagebox
from database import criar_tabelas # Para garantir o DB no primeiro uso
from tkinter import messagebox
from database import (inserir_aluno, buscar_alunos, atualizar_aluno, deletar_aluno, buscar_aluno_por_id) # Importa o CRUD

# --- CONFIGURAÇÕES GLOBAIS DO CTK ---
# Define a aparência global da aplicação
ctk.set_appearance_mode("System")  # Pode ser "Light", "Dark", ou "System"
ctk.set_default_color_theme("blue") # Escolha a cor principal: "blue", "green", ou "dark-blue"

# main.py - ADICIONE ESTA CLASSE ACIMA DE 'class App(ctk.CTk):'

from database import verificar_credenciais, inserir_primeiro_usuario # Importa funções de DB

class LoginFrame(ctk.CTkFrame):
    """Tela de Login da Aplicação Educonnect."""
    def __init__(self, master, app_controller):
        super().__init__(master)
        
        self.app_controller = app_controller # Referência à classe App para trocar de tela
        
        # Configuração do Grid para centralizar o formulário
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # ------------------- WIDGETS DO FORMULÁRIO -------------------
        
        # Frame central para agrupar os campos
        self.login_container = ctk.CTkFrame(self)
        self.login_container.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        # Título
        self.title_label = ctk.CTkLabel(self.login_container, 
                                        text="Educonnect Login", 
                                        font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=30, padx=60)
        
        # Campo Usuário
        self.username_entry = ctk.CTkEntry(self.login_container, 
                                           placeholder_text="Nome de Usuário", 
                                           width=250)
        self.username_entry.pack(pady=12, padx=10)
        
        # Campo Senha
        self.password_entry = ctk.CTkEntry(self.login_container, 
                                           placeholder_text="Senha", 
                                           show="*", # Esconde o texto da senha
                                           width=250)
        self.password_entry.pack(pady=12, padx=10)
        
        # Botão Login
        self.login_button = ctk.CTkButton(self.login_container, 
                                          text="Entrar", 
                                          command=self.perform_login,
                                          width=250)
        self.login_button.pack(pady=20, padx=10)
        
        # Label de Mensagem (para feedback de erro)
        self.message_label = ctk.CTkLabel(self.login_container, text="", text_color="red")
        self.message_label.pack(pady=5, padx=10)

        # Garante a criação do usuário admin na primeira vez (apenas para teste)
        inserir_primeiro_usuario('admin', 'admin123')
        
    def perform_login(self):
        """Lógica executada ao clicar no botão Entrar."""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if verificar_credenciais(username, password):
            # Login bem-sucedido
            self.message_label.configure(text="", text_color="green")
            self.app_controller.show_crud_screen() # Chama a próxima tela
        else:
            # Login falhou
            self.message_label.configure(text="Nome de usuário ou senha incorretos.", text_color="red")

# FIM da classe LoginFrame

# main.py - ADICIONE ESTA CLASSE ABAIXO DA LoginFrame

from database import (inserir_aluno, buscar_alunos, atualizar_aluno, deletar_aluno) # Importa o CRUD

class CRUDFrame(ctk.CTkFrame):
    """Tela Principal: Exibe a lista de alunos e o formulário CRUD."""
    
    def __init__(self, master, app_controller):
        super().__init__(master)
        self.app_controller = app_controller
        self.aluno_selecionado_id = None # Armazena o ID do aluno para edição/exclusão

        # 1. Configuração do Grid principal (2 colunas)
        self.grid_columnconfigure(0, weight=3) # Coluna 0: Tabela de Alunos (maior)
        self.grid_columnconfigure(1, weight=1) # Coluna 1: Formulário (menor)
        self.grid_rowconfigure(0, weight=1)

        # ------------------- COLUNA 0: VISUALIZAÇÃO DE DADOS (READ) -------------------
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=1)

        # Título da Tabela
        ctk.CTkLabel(self.left_panel, text="📚 Alunos Cadastrados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # Container para a lista de alunos (usaremos um CTkScrollableFrame para a lista)
        self.alunos_list_frame = ctk.CTkScrollableFrame(self.left_panel, label_text="Lista de Alunos (Clique para Editar)")
        self.alunos_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.alunos_list_frame.grid_columnconfigure(0, weight=1)

        # Botões de Ação da Tabela (Delete e Logout)
        action_buttons_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        action_buttons_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        action_buttons_frame.grid_columnconfigure((0, 1), weight=1)

        self.delete_button = ctk.CTkButton(action_buttons_frame, text="🗑️ Deletar Selecionado", fg_color="red", hover_color="darkred", command=self.deletar_aluno_selecionado)
        self.delete_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.logout_button = ctk.CTkButton(action_buttons_frame, text="🚪 Logout", command=lambda: self.app_controller.transition_to_login(True)) # Retorna ao login
        self.logout_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")


        # ------------------- COLUNA 1: FORMULÁRIO CRUD (CREATE/UPDATE) -------------------
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.right_panel, text="✏️ Cadastro / Edição", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 15))

        # Campos de Entrada
        self.entries = {}
        campos = [("Nome", "text"), ("Data de Nasc.", "text"), ("Série", "int"), ("Escola", "text"), ("Faltas", "int"), ("Renda Familiar (R$)", "float")]
        
        for idx, (label_text, type) in enumerate(campos):
            ctk.CTkLabel(self.right_panel, text=label_text + ":", anchor="w").pack(fill="x", padx=20, pady=(5, 0))
            entry = ctk.CTkEntry(self.right_panel, placeholder_text=label_text)
            entry.pack(fill="x", padx=20, pady=(0, 5))
            self.entries[label_text] = (entry, type)

        # Botão Salvar/Atualizar
        self.save_button = ctk.CTkButton(self.right_panel, text="➕ Salvar Novo Aluno", command=self.salvar_aluno)
        self.save_button.pack(fill="x", padx=20, pady=(20, 10))
        
        # Botão Limpar Formulário
        self.clear_button = ctk.CTkButton(self.right_panel, text="Limpar Formulário", command=self.limpar_formulario, fg_color="gray", hover_color="darkgray")
        self.clear_button.pack(fill="x", padx=20, pady=(0, 20))
        
        # Carrega os dados na inicialização
        self.carregar_alunos()

    # (Os métodos de lógica serão implementados a seguir)
    # main.py - DENTRO DA CLASSE CRUDFrame (CONTINUAÇÃO)

    def carregar_alunos(self):
        """R (Read): Busca alunos no DB e popula a lista na interface."""
        # Limpa o frame de lista anterior
        for widget in self.alunos_list_frame.winfo_children():
            widget.destroy()

        alunos = buscar_alunos()
        
        # Cria cabeçalhos da lista
        headers = ["ID", "Nome", "Série", "Faltas", "Renda"]
        
        # Usa um frame para os cabeçalhos fixos (não scrollável)
        header_frame = ctk.CTkFrame(self.alunos_list_frame, fg_color=("gray80", "gray25"))
        header_frame.pack(fill="x", padx=0, pady=(0, 5))
        header_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        for col, text in enumerate(headers):
             ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Popula a lista com os dados dos alunos
        for i, aluno in enumerate(alunos):
            aluno_id = aluno[0]
            nome = aluno[1]
            serie = aluno[3]
            faltas = aluno[5]
            renda = aluno[6]
            
            # Frame clicável para cada aluno
            aluno_row = ctk.CTkFrame(self.alunos_list_frame, fg_color="transparent")
            aluno_row.pack(fill="x", padx=0, pady=2)
            aluno_row.columnconfigure((0, 1, 2, 3, 4), weight=1)

            # Usamos uma lambda para passar o ID para a função de edição
            aluno_row.bind("<Button-1>", lambda event, id=aluno_id: self.carregar_aluno_para_edicao(id))
            
            # Criação das células (IDs são internos, os índices referem-se à tupla do DB)
            data_points = [aluno_id, nome, serie, faltas, f"R$ {renda:.2f}"]
            
            for col, data in enumerate(data_points):
                label = ctk.CTkLabel(aluno_row, text=str(data), anchor="w", cursor="hand2")
                label.grid(row=0, column=col, padx=5, sticky="w")
                label.bind("<Button-1>", lambda event, id=aluno_id: self.carregar_aluno_para_edicao(id))

    def carregar_aluno_para_edicao(self, aluno_id):
        """Carrega os dados de um aluno no formulário para edição (Update)."""
        aluno = buscar_aluno_por_id(aluno_id)
        if aluno:
            self.aluno_selecionado_id = aluno_id
            
            # Os índices 1 a 6 correspondem aos campos do formulário
            dados = aluno[1:]
            
            for i, key in enumerate(self.entries.keys()):
                entry_widget, _ = self.entries[key]
                entry_widget.delete(0, tk.END)
                
                valor = str(dados[i])
                if key == "Renda Familiar (R$)":
                    valor = f"{dados[i]:.2f}"
                    
                entry_widget.insert(0, valor)

            self.save_button.configure(text="💾 Atualizar Aluno Existente", fg_color="orange", hover_color="#cc8800")
        
    def limpar_formulario(self):
        """Reseta o formulário para cadastro de um novo aluno (Create)."""
        self.aluno_selecionado_id = None
        for entry_widget, _ in self.entries.values():
            entry_widget.delete(0, tk.END)
        self.save_button.configure(text="➕ Salvar Novo Aluno", fg_color="green", hover_color="darkgreen")

    def validar_dados(self, dados):
        """Valida os tipos de dados antes de enviar ao DB."""
        try:
            dados_tipados = []
            for (entry, type), valor in zip(self.entries.values(), dados):
                if type == "int":
                    dados_tipados.append(int(valor))
                elif type == "float":
                    dados_tipados.append(float(valor))
                else:
                    dados_tipados.append(valor)
            return dados_tipados
        except ValueError:
            messagebox.showerror("Erro de Validação", "Série, Faltas e Renda Familiar devem ser números válidos.")
            return None

    def salvar_aluno(self):
        """C/U (Create/Update): Salva ou atualiza os dados do aluno no DB."""
        
        dados_raw = [entry_widget.get() for entry_widget, _ in self.entries.values()]
        dados_validados = self.validar_dados(dados_raw)
        
        if not dados_validados:
            return

        if self.aluno_selecionado_id:
            # Operação UPDATE
            sucesso = atualizar_aluno(self.aluno_selecionado_id, *dados_validados)
            acao = "atualizado"
        else:
            # Operação CREATE
            sucesso = inserir_aluno(*dados_validados)
            acao = "cadastrado"

        if sucesso:
            messagebox.showinfo("Sucesso", f"Aluno {acao} com sucesso!")
            self.limpar_formulario()
            self.carregar_alunos()
        else:
            messagebox.showerror("Erro", f"Falha ao {acao} o aluno. Verifique os dados.")
            
    def deletar_aluno_selecionado(self):
        """D (Delete): Deleta o aluno selecionado após confirmação."""
        if not self.aluno_selecionado_id:
            messagebox.showwarning("Aviso", "Selecione um aluno na lista para deletar.")
            return

        if messagebox.askyesno("Confirmação de Exclusão", f"Tem certeza que deseja deletar o aluno ID {self.aluno_selecionado_id}?"):
            if deletar_aluno(self.aluno_selecionado_id):
                messagebox.showinfo("Sucesso", "Aluno deletado com sucesso!")
                self.limpar_formulario()
                self.carregar_alunos()
            else:
                messagebox.showerror("Erro", "Falha ao deletar aluno.")

# main.py - DENTRO DA CLASSE App

class App(ctk.CTk):
    """
    Classe principal que gerencia as diferentes telas (frames) da aplicação.
    """
    def __init__(self):
        super().__init__()
        
        # 1. Configuração da Janela Inicial (Splash Screen)
        self.title("Educonnect")
        self.geometry("400x300") # Tamanho adequado para o splash
        self.overrideredirect(True) # Remove barra de título (importante para splash)
        self.center_window(400, 300) # Centraliza a janela
        
        # 2. Garante que o banco de dados e tabelas existam
        # É bom fazer isso antes de carregar o resto da app
        criar_tabelas() 
        
        # 3. Container para gerenciar a troca de telas
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.user_logged_in = None 

        # Inicia a aplicação exibindo a Splash Screen
        self.show_splash_screen()

    def center_window(self, width, height):
        """Função auxiliar para centralizar a janela na tela."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f'{width}x{height}+{int(x)}+{int(y)}')
        
    def show_splash_screen(self):
        """Implementa a tela de Carregamento (Splash Screen)."""
        
        self.clear_container()
        
        # Design do Splash Screen
        splash_label = ctk.CTkLabel(self.container, 
                                    text="Educonnect", 
                                    font=ctk.CTkFont(size=36, weight="bold"))
        splash_label.pack(expand=True, padx=20, pady=20)
        
        loading_label = ctk.CTkLabel(self.container, 
                                     text="Carregando sistema...", 
                                     font=ctk.CTkFont(size=14))
        loading_label.pack(pady=(0, 20))

        # Configuração da transição: espera 3 segundos e chama a transição
        self.after(3000, self.transition_to_login) 

    def transition_to_login(self):
        """Remove as configurações de splash e carrega a tela de Login."""
        
        # 1. Resetar a janela principal para um estado normal
        self.overrideredirect(False) # Devolve a barra de título
        self.title("Educonnect - Login")
        self.geometry("800x600") # Novo tamanho padrão
        self.center_window(800, 600) # Centraliza o novo tamanho
        
        # 2. Chamar a tela de Login (Passo 2.2)
        self.show_login_screen()
        
    # (Os métodos show_login_screen, show_crud_screen e clear_container permanecem os mesmos)
    # main.py - DENTRO DA CLASSE App

    # ... (código anterior da classe App) ...
    
    def show_login_screen(self):
        """Inicializa a tela de Login."""
        print("Iniciando Tela de Login...")
        self.clear_container()
        
        # CRIA A INSTÂNCIA DA TELA DE LOGIN
        login_frame = LoginFrame(master=self.container, app_controller=self) 
        
        login_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["Login"] = login_frame
        
    # main.py - DENTRO DA CLASSE App (Atualização)
# ... (outros métodos da classe App) ...

    def show_crud_screen(self):
        """Inicializa a tela principal (CRUD de Alunos)."""
        
        print("Login bem-sucedido! Abrindo Tela CRUD.")
        self.clear_container()
        
        # CRIA A INSTÂNCIA DA TELA CRUD
        crud_frame = CRUDFrame(master=self.container, app_controller=self) 
        
        crud_frame.grid(row=0, column=0, sticky="nsew")
        self.frames["CRUD"] = crud_frame
        
    def transition_to_login(self, from_logout=False):
        # Usamos 'from_logout' para saber se é a primeira vez ou um logout
        
        # 1. Restaura a janela principal
        self.overrideredirect(False) 
        self.title("Educonnect - Login")
        self.geometry("800x600") 
        self.center_window(800, 600)
        
        # Se for um logout, destruímos e recriamos o app para limpar o estado:
        if from_logout:
            self.destroy()
            app = App()
            app.mainloop()
        else:
            self.show_login_screen()

# ... (Restante da classe App) ...

    def clear_container(self):
        """Limpa o container para a próxima tela ser exibida."""
        for frame in self.container.winfo_children():
            frame.destroy()
            
if __name__ == "__main__":
    app = App()
    app.mainloop()
