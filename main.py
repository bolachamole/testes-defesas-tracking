from bd import BancoDeDados
from Browser import Browser
from subprocess import Popen
from time import sleep
import argparse
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--navegador")
    parser.add_argument("--nivel", default="normal")
    parser.add_argument("--path-perfil", default=None)
    parser.add_argument("--path-navegador", default=None)
    parser.add_argument("--path-webdriver", default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    browsers = ["chrome", "firefox", "edge", "opera", "brave", "safari"]
    if (sys.platform != "darwin"): # só tem safari pra macOS
        browsers = browsers[:5]
    if (sys.platform == "win32"):
        path_mitm = f"{os.environ["VIRTUAL_ENV"]}/Scripts"
    else:
        path_mitm = f"{os.environ["VIRTUAL_ENV"]}/bin"
    niveis = ["normal", "rigoroso"]
    
    if (args.navegador not in browsers):
        print(f"Navegador não suportado. Valores aceitos: {browsers}.")
        sys.exit(1)
    if (args.nivel not in niveis):
        print("Nível de testes desconhecido. Valores aceitos: {niveis}")
        sys.exit(1)
    if (args.navegador in ["opera", "brave"]) and (args.path_navegador == None):
        print(f"É obrigatório especificar o caminho para o {args.navegador}.")
        sys.exit(1)
    if (args.navegador == "opera") and (args.path_webdriver == None):
        print(f"É obrigatório utilizar o webdriver do Opera (https://github.com/operasoftware/operachromiumdriver).")
        sys.exit(1)

    deu_erro = ""
    try:
        proc = Popen([f"{path_mitm}/mitmdump", "-s", "PegaMensagens.py", "--set", "confdir=configs/", "--set", f"navegador={args.navegador}", "--set", f"nivel={args.nivel}"])
        sleep(10) # espera um pouco pro mitmproxy iniciar
        browser = Browser(args.navegador, args.path_perfil, args.path_navegador, args.path_webdriver)
        with open("sites.txt", 'r') as sites:
            try:
                for site in sites:
                    site = site.strip()
                    with open("configs/config.yaml", "w") as c:
                        c.writelines(f"site: {site}")
                    status = browser.get(f"https://{site}")
                    if (status == 0):
                        sleep(60)
                    else:
                        continue
            except KeyboardInterrupt:
                print("Programa interrompido!")
            except Exception as erro:
                deu_erro = f"Erro ao tentar abrir os sites: {erro}"
            finally:
                browser.quit()
                proc.terminate()
                proc.wait()
                bancodedados = BancoDeDados(args.navegador, args.nivel)
                n = bancodedados.conta_cookies_1p()
                print("N° de possíveis cookies de rastreamento (primeiros):", n)
                n = bancodedados.conta_cookies_3p()
                print("N° de possíveis cookies de rastreamento (terceiros):", n)
                n = bancodedados.conta_csync()
                print("N° de instâncias de cookie syncing:", n)
                total = bancodedados.conta_trackers()
                print("N° de requisições a conteúdo de rastreamento:", total)
                if (total > 0):
                    blocks = bancodedados.conta_trackers_bloqueados()
                    print(f"N° de conteúdos de rastreamento bloqueados: {blocks} ({blocks * 100/total}%)")

    except Exception as erro:
        deu_erro = f"Erro ao tentar iniciar os testes: {erro}"

    if (len(deu_erro) > 0):
        print(deu_erro)
        sys.exit(1)

main()
sys.exit(0)
