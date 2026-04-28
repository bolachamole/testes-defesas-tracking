from datetime import datetime
from urllib.parse import urlsplit, parse_qs, unquote
from whois import whois
from mitmproxy import ctx
from utils import *
from bd import BancoDeDados
import re2
import re

EXPIRES = [
    "%a, %d-%b-%Y %H:%M:%S %Z",
    "%a, %d %b %Y %H:%M:%S %Z",
    "%a, %d-%b-%y %H:%M:%S %Z",
    "%a, %d %b %y %H:%M:%S %Z",
    "%a, %d-%m-%Y %H:%M:%S %Z",
    "%a, %d %m %Y %H:%M:%S %Z",
    "%a, %d-%m-%y %H:%M:%S %Z",
    "%a, %d %m %y %H:%M:%S %Z",
]

class PegaMensagens:
    def __init__(self):
        self.site_ids = {}
        self.id_cookies = []
        self.lista_disc = []
        self.lista_easyp = getEasyPrivacy()
        self.lista_disc = getDisconnect()

    def load(self, loader):
        loader.add_option(
            name="navegador",
            typespec=str,
            default="",
            help="Navegador sendo utilizado."
        )
        loader.add_option(
            name="site",
            typespec=str,
            default="",
            help="Site sendo acessado via navegador."
        )
        loader.add_option(
            name="nivel",
            typespec=str,
            default="normal",
            help="Nível das defesas sendo testadas."
        )

    def configure(self, update):
        opt = ctx.options
        if ("site" in update):
            self.site_atual = opt.site

        self.cookie_db = BancoDeDados(opt.navegador, opt.nivel)
        self.cookie_db.cria_tabela_cookie()
        self.cookie_db.cria_tabela_csync()
        self.cookie_db.cria_tabela_trackers()

        ctx.log.info("Configurações alteradas!")

    def _checkIDs(self, site1, lista_valores):
        for valor in lista_valores:
            v = valor[0]
            if (len(v) > 8) and (re2.fullmatch(r"[a-zA-Z0-9_=-]+", v)):
                site2 = [k for k in self.site_ids.keys() if v in self.site_ids.get(k)]
                if (site2 == []):
                    self.site_ids.setdefault(site1, []).append(v)
                # verifica cookie syncing
                elif (site1 != site2[0]):
                    j = [i for i in range(len(self.id_cookies)) if v in self.id_cookies[i]]
                    if (j != []):
                        i = j[0]
                        mesmo_dono = False
                        try:
                            mesmo_dono = whois(site1).get("org") == whois(site2[0]).get("org")
                        finally:
                            if (mesmo_dono == False):
                                self.cookie_db.insere_csync(site1, site2[0], self.id_cookies[i][0], self.id_cookies[i][1])
                                ctx.log.info(f"Cookie syncing entre {site1} e {site2[0]}: {self.id_cookies[i][0]}={self.id_cookies[i][1]}")

    def _checkCookie(self, vals, nome, valor, host):
        expires = vals.get("expires")
        max_age = vals.get("max-age")
        dominio = vals.get("domain")
        idade = ""
        suspeita = False
        if (max_age):
            idade = f"{max_age}"
            if (int(max_age) > 0):
                suspeita = True
        elif (expires):
            for data in EXPIRES:
                try:
                    expira = datetime.strptime(expires, data)
                    idade = f"{expira}"
                    if ((expira - datetime.today()).days > 0):
                        suspeita = True                
                except ValueError:
                    continue

        if (dominio == None):
            dominio = host
        elif (dominio[0] == '.'):
            dominio = dominio[1:]
        terceiro = dominio != self.site_atual
        
        # pega possiveis cookies de tracking
        if (suspeita) and (len(valor) > 8):
            if (re2.fullmatch(r"[a-zA-Z0-9_=-]+", valor)) or (re2.findall(r"[a-zA-Z_]+:[a-zA-Z0-9_=-]+", valor)) or (re2.findall(r"[a-zA-Z0-9_]+=[a-zA-Z0-9_=-]+", valor)):
                self.id_cookies.append([nome,valor])
                self.cookie_db.insere_cookie(dominio, nome, valor, terceiro, idade)
                ctx.log.info(f"Possível cookie de tracking: {nome}={valor}")

    def request(self, flow):
        url_host = splitWWW(flow.request.host)

        terceiro = False
        if (self.site_atual != url_host):
            terceiro = True
        fetch_dest = flow.request.headers.get("sec-fetch-dest", '')
        subdocument = False
        if (fetch_dest == "iframe"):
            subdocument = True

        achou = 0
        if ("script" in flow.request.headers.get("accept", '')):
            if (terceiro):
                regras = self.lista_easyp["script-third"]
                options = {"third-party": True, "script": True, "domain": url_host, "subdocument": subdocument}
            else:
                regras = self.lista_easyp["script"]
                options = {"script": True, "domain": url_host, "subdocument": subdocument}
        elif ("image" in flow.request.headers.get("accept", '')):
            if (terceiro):
                regras = self.lista_easyp["image-third"]
                options = {"third-party": True, "image": True, "domain": url_host, "subdocument": subdocument}
            else:
                regras = self.lista_easyp["image"]
                options = {"image": True, "domain": url_host, "subdocument": subdocument}
        elif (terceiro):
            regras = self.lista_easyp["third"]
            options = {"third-party": True, "xmlhttprequest": True, "domain": url_host, "subdocument": subdocument}
        else:
            regras = self.lista_easyp["domain"]
            options = {"xmlhttprequest": True, "domain": url_host, "subdocument": subdocument}

        # verifica conteudo de tracking
        if (regras.should_block(flow.request.url, options) == True):
            status = self.cookie_db.insere_trackers(self.site_atual, flow.request.url, "easyprivacy")
            # se foi inserido com exito, sera possivel atualizar depois
            if (status == 0):
                achou = 1
                flow.marked = "easy"
        i = 0
        while (achou == 0) and (i < len(self.lista_disc)):
            if (terceiro) and (self.lista_disc[i] == url_host):
                status = self.cookie_db.insere_trackers(self.site_atual, flow.request.url, "disconnect")
                if (status == 0):
                    flow.marked = "disc"
            i += 1

    def response(self, flow):
        url_parsed = urlsplit(flow.request.url)
        url_params = parse_qs(url_parsed.query)
        referer_parsed = urlsplit(flow.request.headers.get("referer", ''))
        referer_params = parse_qs(referer_parsed.query)

        self._checkIDs(splitWWW(flow.request.host), url_params.values())
        self._checkIDs(splitWWW(referer_parsed.netloc), referer_params.values())

        # verifica cookies
        cookie_header = flow.response.cookies 
        if (cookie_header):
            for (nome, v) in cookie_header.items():
                vals = dict([[k.lower(), v[1].get(k)] for k in v[1]])
                self._checkCookie(vals, nome, unquote(v[0]), url_parsed.netloc)

        # pega scripts
        if ("script" in flow.response.headers.get("content-type", '')) or (flow.request.path.endswith(".js")):
            javascript = re.sub(r"\s*{\s*(?!};)", "{\n", flow.response.content.decode("utf-8"))
            javascript = re2.sub(r"\s*;\s*", ";\n", javascript)
            javascript = re.sub(r"(?<!{)\s*}(;)?\s*", "\n}\n", javascript)
            for linha in javascript.splitlines(True):
                # verifica cookies criados
                if (re2.match(r"\s*document\.cookie\s*=", linha)):
                    cookie = re.findall(r"([^\"\'=; ]+)(?:=([^\"\';]+))?", (re2.split(r"\s*document\.cookie\s*=\s*", linha))[1])
                    if (cookie):
                        vals = dict([[k.lower(), v] if v else [k, "true"] for (k,v) in cookie[1:]])
                        self._checkCookie(vals, cookie[0][0], unquote(cookie[0][1]), url_parsed.netloc)

        # verifica se a requisicao é de um tracker
        if (flow.marked == "easy"):
            self.cookie_db.atualiza_trackers(self.site_atual, flow.request.url, "easyprivacy")
            ctx.log.info(f"Tracker {flow.request.url} encontrado.")
        elif (flow.marked == "disc"):
            self.cookie_db.atualiza_trackers(self.site_atual, flow.request.url, "disconnect")
            ctx.log.info(f"Tracker {flow.request.url} encontrado.")

addons = [PegaMensagens()]
