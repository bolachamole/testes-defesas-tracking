from bd import BancoDeDados
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxDriver
from selenium.webdriver.edge.webdriver import WebDriver as EdgeDriver
from selenium.webdriver.safari.webdriver import WebDriver as SafariDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.safari.options import Options as SafariOptions

MEU_SCRIPT = """
let resultado = Object.create(null);
let chave;

resultado["localStorage"] = Object.create(null);
for(let i = 0; i < localStorage.length; i++){
    chave = localStorage.key(i);
    resultado.localStorage[chave] = localStorage.getItem(chave);
}

resultado["sessionStorage"] = Object.create(null);
for(let i = 0; i < sessionStorage.length; i++){
    chave = sessionStorage.key(i);
    resultado.sessionStorage[chave] = sessionStorage.getItem(chave);
}

return resultado;
"""

class Browser:
    def __init__(self, nav, nivel, profile=None, path=None):
        self.storage = BancoDeDados(nav, nivel)
        if (nav == "firefox"):
            options = FirefoxOptions()
            options.add_argument("-profile")
            if (profile):
                options.add_argument(profile)
            self.driver = FirefoxDriver(options=options)
        elif (nav == "edge"):
            options = EdgeOptions()
            if (profile):
                options.add_argument(profile)
                options.add_argument(f"--user-data-dir={profile}")
            self.driver = EdgeDriver(options=options)
        elif (nav == "safari"):
            options = SafariOptions()
            self.driver = SafariDriver(options=options)
        else:
            options = ChromeOptions()
            if (path):
                options.binary_location = path
            if (profile):
                options.add_argument(profile)
                options.add_argument(f"--user-data-dir={profile}")
            self.driver = ChromeDriver(options=options)

    def get(self, site):
        self.driver.get(site)

    def coleta(self, site):
        resultado = self.driver.execute_script(MEU_SCRIPT)
        if (resultado):
            conexao = self.storage.conecta()
            if (conexao):
                status = self.storage.cria_tabela_storage(conexao)
                if (status == 0):
                    if ("localStorage" in resultado.keys()):
                        local_dicio = resultado["localStorage"]
                        for item in local_dicio.items():
                            self.storage.insere_storage(conexao, site, item[0], item[1])
                    if ("sessionStorage" in resultado.keys()):
                        session_dicio = resultado["sessionStorage"]
                        for item in session_dicio.items():
                            self.storage.insere_storage(conexao, site, item[0], item[1])
                    self.storage.desconecta(conexao)

    def quit(self):
        self.driver.quit()
