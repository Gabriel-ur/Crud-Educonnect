import mysql.connector
from mysql.connector import Error
import bcrypt

# Configuração de conexão MySQL (use as credenciais que você forneceu)
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "Educonnect",  # nome do database solicitado
    "charset": "utf8mb4"
}

def get_conexao():
    """
    Retorna uma conexão com o banco de dados MySQL definido em DB_CONFIG.
    Assumimos que o database já existe; se não existir, criar_tabelas() tentará criá-lo.
    """
    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"],
        charset=DB_CONFIG.get("charset", "utf8mb4")
    )

def criar_database_se_nao_existir():
    """
    Conecta ao servidor MySQL sem especificar database e cria o database se não existir.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[ERRO] Não foi possível criar/verificar o database: {e}")
        raise

def hash_senha(senha):
    """Gera o hash da senha usando bcrypt e retorna string decodificada."""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

def criar_tabelas():
    """Cria as tabelas 'alunos' e 'usuarios' no MySQL se não existirem."""
    try:
        # Garante que o database exista
        criar_database_se_nao_existir()

        conn = get_conexao()
        cursor = conn.cursor()

        # Tabela de Alunos (CRUD Principal)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INT PRIMARY KEY AUTO_INCREMENT,
                nome VARCHAR(255) NOT NULL,
                data_nascimento VARCHAR(50),
                serie INT,
                escola VARCHAR(255),
                historico_faltas INT DEFAULT 0,
                renda_familiar DECIMAL(10,2)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Tabela de Usuários (Para o Login)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print(f"Database '{DB_CONFIG['database']}' e tabelas criadas/verificadas com sucesso.")
    except Error as e:
        print(f"[ERRO] Ao criar tabelas: {e}")
        raise

# --- FUNÇÕES DE AUTENTICAÇÃO ---

def verificar_credenciais(username, senha):
    """
    Verifica se o username e a senha correspondem ao registro no DB.
    Retorna True/False.
    """
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = %s", (username,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        if resultado:
            password_hash = resultado[0]
            if isinstance(password_hash, str):
                password_hash = password_hash.encode('utf-8')
            try:
                return bcrypt.checkpw(senha.encode('utf-8'), password_hash)
            except ValueError:
                return False
        return False
    except Error as e:
        print(f"[ERRO] verificar_credenciais: {e}")
        return False

def inserir_primeiro_usuario(username, senha):
    """
    Insere um usuário administrador inicial se a tabela estiver vazia.
    """
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        if count == 0:
            hashed_password = hash_senha(senha)
            try:
                cursor.execute("INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()
                print(f"Usuário administrador '{username}' criado com sucesso!")
            except Error as e:
                print(f"[ERRO] Ao inserir usuário inicial: {e}")
        cursor.close()
        conn.close()
    except Error as e:
        print(f"[ERRO] inserir_primeiro_usuario: {e}")

# --- FUNÇÕES CRUD DE ALUNOS ---

def inserir_aluno(nome, data_nascimento, serie, escola, historico_faltas, renda_familiar):
    """Insere um novo aluno no banco de dados."""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alunos (nome, data_nascimento, serie, escola, historico_faltas, renda_familiar)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, data_nascimento, serie, escola, historico_faltas, renda_familiar))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"[ERRO] inserir_aluno: {e}")
        return False

def buscar_alunos():
    """Retorna todos os alunos com seus IDs."""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data_nascimento, serie, escola, historico_faltas, renda_familiar FROM alunos ORDER BY nome")
        alunos = cursor.fetchall()
        cursor.close()
        conn.close()
        return alunos
    except Error as e:
        print(f"[ERRO] buscar_alunos: {e}")
        return []

def buscar_aluno_por_id(aluno_id):
    """Retorna os dados de um aluno específico pelo ID."""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data_nascimento, serie, escola, historico_faltas, renda_familiar FROM alunos WHERE id = %s", (aluno_id,))
        aluno = cursor.fetchone()
        cursor.close()
        conn.close()
        return aluno
    except Error as e:
        print(f"[ERRO] buscar_aluno_por_id: {e}")
        return None

def atualizar_aluno(aluno_id, nome, data_nascimento, serie, escola, historico_faltas, renda_familiar):
    """Atualiza os dados de um aluno existente."""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE alunos SET
                nome = %s, data_nascimento = %s, serie = %s, escola = %s,
                historico_faltas = %s, renda_familiar = %s
            WHERE id = %s
        """, (nome, data_nascimento, serie, escola, historico_faltas, renda_familiar, aluno_id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0
    except Error as e:
        print(f"[ERRO] atualizar_aluno: {e}")
        return False

def deletar_aluno(aluno_id):
    """Remove um aluno do banco de dados pelo ID."""
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id = %s", (aluno_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0
    except Error as e:
        print(f"[ERRO] deletar_aluno: {e}")
        return False

# Bloco de testes que será executado se rodar o arquivo diretamente
if __name__ == '__main__':
    criar_tabelas()

    # 1. TESTE DE AUTENTICAÇÃO: Cria um usuário admin/admin
    inserir_primeiro_usuario('admin', 'admin123')
    print("-" * 30)

    # 2. TESTE DE LOGIN
    if verificar_credenciais('admin', 'admin123'):
        print("Login com sucesso!")
    else:
        print("Falha no login.")

    if not verificar_credenciais('admin', 'senhaerrada'):
        print("Login recusado corretamente.")
    else:
        print("Falha na segurança.")

    print("-" * 30)

    # 3. TESTE CRUD: Insere e busca um aluno
    inserir_aluno('Maria da Silva', '2005-01-15', 3, 'Escola Pública A', 5, 1500.50)
    inserir_aluno('João Santos', '2006-05-20', 2, 'Escola Estadual B', 12, 900.00)

    alunos = buscar_alunos()
    print("Alunos cadastrados:")
    for aluno in alunos:
        print(aluno)

    # 4. TESTE CRUD: Atualização (Exemplo: João mudou de série)
    if alunos:
        joao_id = alunos[-1][0]  # Pega o ID do último inserido (João)
        atualizar_aluno(joao_id, 'João Santos', '2006-05-20', 3, 'Escola Estadual B', 15, 1200.00)
        print("\nJoão atualizado:", buscar_aluno_por_id(joao_id))

    print("-" * 30)
