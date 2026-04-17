from adblockparser import AdblockRules
import json
import requests

def splitWWW(host):
    try:
        host_split = host.split("www.")[1] # tinha "www."
    except IndexError:
        host_split = host.split("www.")[0] # não tem "www."
    return host_split

def getEasyPrivacy():
    try:
        r = requests.get("https://easylist.to/easylist/easyprivacy.txt").text
        with open("easyprivacy.txt", "w") as easyprivacy:
            easyprivacy.writelines(r)
    finally:
        with open("easyprivacy.txt", "r") as easyprivacy:
            easyp = easyprivacy.readlines()
            easyp = [linha.strip() for linha in easyp]

    regras = {}
    regras["script"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["script", "domain", "subdocument"], skip_unsupported_rules=False)
    regras["script-third"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["third-party", "script", "domain", "subdocument"], skip_unsupported_rules=False)
    regras["image"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["image", "domain", "subdocument"], skip_unsupported_rules=False)
    regras["image-third"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["third-party", "image", "domain", "subdocument"], skip_unsupported_rules=False)
    regras["third"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["third-party", "xmlhttprequest", "domain", "subdocument"], skip_unsupported_rules=False)
    regras["domain"] = AdblockRules(easyp, use_re2=True, max_mem=512*1024*1024, supported_options=["xmlhttprequest", "domain", "subdocument"], skip_unsupported_rules=False)
    
    return regras

def getDisconnect():
    lista_disc = []
    disc = json.loads(requests.get("https://raw.githubusercontent.com/disconnectme/disconnect-tracking-protection/refs/heads/master/services-relay.json").text)
    for cat in disc["categories"]:
        for i in range(len(disc["categories"][cat])):
            lista_disc.append(disc["categories"][cat][i])
    return lista_disc

def alteraCSP(csp, script_hash):
    diretivas = []
    script_src = None
    default_src = None
    for diretiva in csp.split(';'):
        if (diretiva): # pode vir '' se houver um ; final
            diretiva = diretiva.strip()
            if (diretiva.startswith("script-src")):
                script_src = diretiva
            elif (diretiva.startswith("default-src")):
                default_src = diretiva.split("default-src")[1].strip()
                diretivas.append(diretiva)
            else:
                diretivas.append(diretiva)
    if (script_src):
        script_src = f"script-src 'sha256-{script_hash}' {script_src.split("script-src ")[1].strip()}"
    elif (default_src) and (default_src != "'none'"):
        script_src = f"script-src 'sha256-{script_hash}' {default_src}"
    else:
        script_src = f"script-src 'sha256-{script_hash}'"
    diretivas.append(script_src)
    return diretivas
