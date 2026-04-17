import sqlite3

DB_ARQ = "stateful.db"

class BancoDeDados:
    def __init__(self, navegador, nivel):
        self.nome_db = f"{navegador}_{nivel}"

    def conecta(self):
        conexao = None
        try:
            conexao = sqlite3.connect(DB_ARQ)
            return conexao
        except Exception as erro:
            print("Não foi possível conectar-se.", erro)    
        return None

    def cria_tabela_cookie(self, conexao):
        try:
            cursor = conexao.cursor()
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.nome_db}_cookies(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT,
                        name TEXT,
                        value TEXT,
                        third_party INTEGER,
                        expires TEXT
                        );""")
            conexao.commit()
            cursor.close()
        except Exception as erro:
            print("Não foi possível criar tabela.", erro)

    def insere_cookie(self, conexao, domain, name, value, tp, expires):
        if (tp):
            third_party = 1
        else:
            third_party = 0

        try:
            cursor = conexao.cursor()
            tupla = (domain, name, value, third_party, expires)
            cursor.execute(f"INSERT INTO {self.nome_db}_cookies (domain, name, value, third_party, expires) VALUES (?, ?, ?, ?, ?);", tupla)
            conexao.commit()
            cursor.close()
        except Exception as erro:
            print("Não foi possível inserir na tabela.", erro)

    def cria_tabela_storage(self, conexao):
        try:
            cursor = conexao.cursor()
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.nome_db}_storage(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        domain TEXT,
                        name TEXT,
                        value TEXT
                        );""")
            conexao.commit()
            cursor.close()
            return 0
        except Exception as erro:
            print("Não foi possível criar tabela.", erro)
        return 1

    def insere_storage(self, conexao, domain, name, value):
        try:
            cursor = conexao.cursor()
            tupla = (domain, name, value)
            cursor.execute(f"INSERT INTO {self.nome_db}_storage (domain, name, value) VALUES (?, ?, ?);", tupla)
            conexao.commit()
            cursor.close()
        except Exception as erro:
            print("Não foi possível inserir na tabela.", erro)

    def conta_supercookies(self, conexao):
        quant = -1
        try:
            cursor = conexao.cursor()
            consulta = cursor.execute(f"SELECT * FROM {self.nome_db}_cookies INNER JOIN {self.nome_db}_storage ON {self.nome_db}_cookies.domain={self.nome_db}_storage.domain AND {self.nome_db}_cookies.name={self.nome_db}_storage.name AND {self.nome_db}_cookies.value={self.nome_db}_storage.value;")
            quant = len(consulta.fetchall())
            cursor.close()
        except Exception as erro:
            print("Não foi possível procurar supercookies.", erro)
        return quant

    def desconecta(self, conexao):
        try:
            conexao.close()
            print("Conexão encerrada.")
        except Exception as erro:
            print("Não foi possível encerrar a conexão.", erro)
