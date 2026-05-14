import json
import subprocess
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === CONFIGURAÇÕES ===
# Mude 'SEU_USUARIO' para o seu nome de usuário do Windows
CHROME_PROFILE_PATH = r'C:\Users\SEU_USUARIO\AppData\Local\Google\Chrome\User Data'
JSON_FILE = 'cupons.json'
STORES = ['nuuvem', 'rdc', 'bonoxs']

def get_driver():
    options = Options()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--profile-directory=Default") # Ou o nome do seu perfil
    # options.add_argument("--headless") # Descomente para rodar sem abrir a janela
    return webdriver.Chrome(options=options)

def buscar_cupons_pelando(driver, loja):
    print(f"Buscando cupons para {loja} no Pelando...")
    driver.get(f"https://www.pelando.com.br/busca?q={loja}")
    time.sleep(5) # Espera carregar a página
    
    encontrados = []
    # Busca por elementos que costumam conter códigos de cupom
    elementos = driver.find_elements(By.TAG_NAME, "span")
    for el in elementos:
        texto = el.text.strip()
        # Lógica simples: cupons costumam ser curtos, em maiúsculo e sem espaços
        if texto.isupper() and 3 <= len(texto) <= 15 and " " not in texto:
            encontrados.append(texto)
    
    return list(set(encontrados)) # Remove duplicatas da busca atual

def atualizar_repositorio():
    print("Enviando atualizações para o GitHub...")
    try:
        subprocess.run(["git", "add", JSON_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "🤖 Auto-update: Novos cupons encontrados"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("GitHub atualizado com sucesso!")
    except Exception as e:
        print(f"Erro no Git: {e}")

def main():
    if not os.path.exists(JSON_FILE):
        print(f"Erro: {JSON_FILE} não encontrado!")
        return

    driver = get_driver()
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        dados_vps = json.load(f)

    mudou = False
    for loja in STORES:
        novos = buscar_cupons_pelando(driver, loja)
        
        # Pega apenas os códigos que já existem para comparar
        codigos_atuais = [c['code'] for c in dados_vps.get(loja, [])]
        
        for n in novos:
            if n not in codigos_atuais:
                print(f"✨ Novo cupom detectado para {loja}: {n}")
                novo_obj = {
                    "code": n,
                    "desc": "Cupom encontrado automaticamente",
                    "value": 5, # Valor padrão para teste
                    "confidence": "média",
                    "method": None
                }
                dados_vps[loja].append(novo_obj)
                mudou = True

    driver.quit()

    if mudou:
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados_vps, f, indent=2, ensure_ascii=False)
        atualizar_repositorio()
    else:
        print("Nenhum cupom novo encontrado desta vez.")

if __name__ == "__main__":
    main()