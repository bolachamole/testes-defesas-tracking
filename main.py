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
    return parser.parse_args()

def main():
    args = parse_args()
    browsers = ["chrome", "firefox", "edge", "opera", "brave", "safari"]
    if (sys.platform != "darwin"): # só tem safari pra macOS
        browsers = browsers[:5]
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

    try:
        proc = Popen([f"{os.environ["VIRTUAL_ENV"]}/bin/mitmdump", "-s PegaMensagens.py", "--set", "confdir=configs/", "--set", f"navegador={args.navegador}", "--set", f"nivel={args.nivel}"])
        sleep(10) # espera um pouco pro mitmproxy iniciar
        browser = Browser(args.navegador, args.nivel, args.path_perfil, args.path_navegador)
        try:
            with open("sites.txt", 'r') as sites:
                for site in sites:
                    with open("configs/config.yaml", "r") as c:
                        config = c.readlines()
                    config[1] = f"  site: {site}"
                    with open("configs/config.yaml", "w") as c:
                        c.writelines(config)
                    browser.get(f"https://{site}")
                    sleep(60)
                    browser.coleta(site)
                bancodedados = BancoDeDados(args.navegador, args.nivel)
                conexao = bancodedados.conecta()
                if (conexao):
                    supercookies = bancodedados.conta_supercookies(conexao)
                    print(f"N° de supercookies:", supercookies)
        except Exception as erro:
            print("Erro ao tentar abrir os sites:", erro)
        finally:
            browser.quit()
            proc.terminate()
            proc.wait()
    except Exception as erro:
        print("Erro ao tentar iniciar os testes:", erro)

main()
sys.exit(0)
