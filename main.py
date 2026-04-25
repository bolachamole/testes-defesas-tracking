from bd import BancoDeDados
from Browser import Browser
from subprocess import Popen, run
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

    deu_erro = False
    try:
        proc = Popen([f"{path_mitm}/mitmdump", "-s", "PegaMensagens.py", "--set", "confdir=configs/", "--set", f"navegador={args.navegador}", "--set", f"nivel={args.nivel}"])
        sleep(10) # espera um pouco pro mitmproxy iniciar
        browser = Browser(args.navegador, args.nivel, args.path_perfil, args.path_navegador)
        try:
            with open("sites.txt", 'r') as sites:
                for site in sites:
                    with open("configs/config.yaml", "w") as c:
                        c.writelines(f"site: {site}")
                    browser.get(f"https://{site}")
                    sleep(60)
                    browser.coleta(site)
        except KeyboardInterrupt:
            print("Programa interrompido!")
        except Exception as erro:
            print("Erro ao tentar abrir os sites:", erro)
            deu_erro = True
        finally:
            browser.quit()
            if (sys.platform != "win32"):
                proc.terminate()
            else: # no windows o terminate() chama o TerminateProcess(), o que não ativa o done() do mitmproxy
                run(["taskkill", "/PID", str(proc.pid)], capture_output=True)
            proc.wait()
            bancodedados = BancoDeDados(args.navegador, args.nivel)
            n = bancodedados.conta_cookies_1p()
            print("N° de possíveis cookies de rastreamento (primeiros):", n)
            n = bancodedados.conta_cookies_3p()
            print("N° de possíveis cookies de rastreamento (terceiros):", n)
            n = bancodedados.conta_supercookies()
            print(f"N° de supercookies:", n)
    except Exception as erro:
        print("Erro ao tentar iniciar os testes:", erro)
        deu_erro = True

    if (deu_erro):
        sys.exit(1)

main()
sys.exit(0)
