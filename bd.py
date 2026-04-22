import sqlite3

DB_ARQ = "stateful.db"

class BancoDeDados:
    def __init__(self, navegador, nivel):
        self.nome_db = f"{navegador}_{nivel}"

    def cria_tabela_cookie(self):
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
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
            conexao.close()
        except Exception as erro:
            print("Não foi possível criar tabela {self.nome_db}_cookies.", erro)

    def insere_cookie(self, domain, name, value, tp, expires):
        if (tp):
            third_party = 1
        else:
            third_party = 0

        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                tupla = (domain, name, value, third_party, expires)
                cursor.execute(f"INSERT INTO {self.nome_db}_cookies (domain, name, value, third_party, expires) VALUES (?, ?, ?, ?, ?);", tupla)
                conexao.commit()
                cursor.close()
            conexao.close
        except Exception as erro:
            print("Não foi possível inserir na tabela {self.nome_db}_cookies.", erro)

    def conta_cookies_1p(self):
        quant = -1
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                consulta = cursor.execute(f"SELECT * FROM {self.nome_db}_cookies WHERE third_party=0;")
                quant = len(consulta.fetchall())
                cursor.close()
            conexao.close()
        except Exception as erro:
            print("Não foi possível procurar cookies de primeiros.", erro)
        return quant

    def conta_cookies_3p(self):
        quant = -1
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                consulta = cursor.execute(f"SELECT * FROM {self.nome_db}_cookies WHERE third_party=1;")
                quant = len(consulta.fetchall())
                cursor.close()
            conexao.close()
        except Exception as erro:
            print("Não foi possível procurar cookies de terceiros.", erro)
        return quant

    def cria_tabela_storage(self):
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.nome_db}_storage(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            domain TEXT,
                            name TEXT,
                            value TEXT
                            );""")
                conexao.commit()
                cursor.close()
            conexao.close()
            return 0
        except Exception as erro:
            print("Não foi possível criar tabela {self.nome_db}_storage.", erro)
        return 1

    def insere_storage(self, domain, name, value):
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                tupla = (domain, name, value)
                cursor.execute(f"INSERT INTO {self.nome_db}_storage (domain, name, value) VALUES (?, ?, ?);", tupla)
                conexao.commit()
                cursor.close()
            conexao.close()
        except Exception as erro:
            print("Não foi possível inserir na tabela {self.nome_db}_storage.", erro)

    def conta_supercookies(self):
        quant = -1
        try:
            with sqlite3.connect(DB_ARQ) as conexao:
                cursor = conexao.cursor()
                consulta = cursor.execute(f"SELECT * FROM {self.nome_db}_cookies INNER JOIN {self.nome_db}_storage ON {self.nome_db}_cookies.domain={self.nome_db}_storage.domain AND {self.nome_db}_cookies.name={self.nome_db}_storage.name AND {self.nome_db}_cookies.value={self.nome_db}_storage.value;")
                quant = len(consulta.fetchall())
                cursor.close()
            conexao.close()
        except Exception as erro:
            print("Não foi possível procurar supercookies.", erro)
        return quant
