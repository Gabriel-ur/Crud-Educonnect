import mysql.connector
from mysql.connector import Error
import bcrypt

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "1234",
    "database": "Educonnect",
    "charset": "utf8mb4"
}

def get_conexao():
    return mysql.connector.connect(**DB_CONFIG)


# -------------------------------
# CRIAR TABELAS
# -------------------------------
def criar_tabelas():
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        conn.close()

        conn = get_conexao()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                idALUNOS INT PRIMARY KEY AUTO_INCREMENT,
                RA INT,
                Nome VARCHAR(45),
                DataNascimento DATE,
                Endereco VARCHAR(100),
                placeholder INT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Tabelas OK.")
    except Error as e:
        print("[ERRO] criar_tabelas:", e)


# -------------------------------
# FUNÇÕES DE LOGIN
# -------------------------------

def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

def inserir_primeiro_usuario(username, senha):
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]

        if count == 0:
            hashed = hash_senha(senha)
            cursor.execute(
                "INSERT INTO usuarios (username, password_hash) VALUES (%s, %s)",
                (username, hashed)
            )
            conn.commit()
            print("Usuário admin criado!")

        cursor.close()
        conn.close()
    except Error as e:
        print("[ERRO] inserir_primeiro_usuario:", e)

def verificar_credenciais(username, senha):
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM usuarios WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return False

        return bcrypt.checkpw(senha.encode(), row[0].encode())

    except Error as e:
        print("[ERRO] verificar_credenciais:", e)
        return False


# -------------------------------
# CRUD ALUNOS
# -------------------------------

def inserir_aluno(RA, Nome, DataNascimento, Endereco):
    """
    Insere um aluno. placeholder será sempre NULL.
    DataNascimento deve ser do tipo datetime.date
    """
    try:
        conn = get_conexao()
        cursor = conn.cursor()

        # Escrevemos NULL diretamente na query
        cursor.execute("""
            INSERT INTO alunos (RA, Nome, DataNascimento, Endereco, placeholder)
            VALUES (%s, %s, %s, %s, NULL)
        """, (RA, Nome, DataNascimento, Endereco))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("[ERRO] inserir_aluno:", e)
        return False


def buscar_alunos():
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idALUNOS, RA, Nome, DataNascimento, Endereco
            FROM alunos ORDER BY Nome
        """)
        dados = cursor.fetchall()
        cursor.close()
        conn.close()
        return dados
    except Error as e:
        print("[ERRO] buscar_alunos:", e)
        return []


def buscar_aluno_por_id(idAluno):
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT idALUNOS, RA, Nome, DataNascimento, Endereco
            FROM alunos WHERE idALUNOS = %s
        """, (idAluno,))
        dado = cursor.fetchone()
        cursor.close()
        conn.close()
        return dado
    except Error as e:
        print("[ERRO] buscar_aluno_por_id:", e)
        return None


def atualizar_aluno(idAluno, RA, Nome, DataNascimento, Endereco):
    try:
        conn = get_conexao()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE alunos SET
                RA = %s,
                Nome = %s,
                DataNascimento = %s,
                Endereco = %s
            WHERE idALUNOS = %s
        """, (RA, Nome, DataNascimento, Endereco, idAluno))

        conn.commit()
        ok = cursor.rowcount > 0
        cursor.close()
        conn.close()
        return ok

    except Error as e:
        print("[ERRO] atualizar_aluno:", e)
        return False


def deletar_aluno(idAluno):
    try:
        conn = get_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE idALUNOS = %s", (idAluno,))
        conn.commit()
        ok = cursor.rowcount > 0
        cursor.close()
        conn.close()
        return ok
    except Error as e:
        print("[ERRO] deletar_aluno:", e)
        return False
