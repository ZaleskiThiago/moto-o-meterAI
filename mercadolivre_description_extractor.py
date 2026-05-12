import json
import time
import random
import os
from playwright.sync_api import sync_playwright

def description_extractor():
    input_file = 'json/bronze_motos_mercadolivre_20260506.json'
    output_file = 'json/bronze_motos_com_descricao.json'
    
    # 1. Carregar ou Inicializar o progresso
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            motos = json.load(f)
        print(f"🔄 Retomando progresso do arquivo existente ({len(motos)} registros).")
    else:
        with open(input_file, 'r', encoding='utf-8') as f:
            motos = json.load(f)
        print(f"🆕 Iniciando nova coleta para {len(motos)} motos.")

    with sync_playwright() as p:
        user_data_dir = "./playwright_profile"
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.pages[0]

        for i, moto in enumerate(motos):
            # LÓGICA DE PULO: Se já tem descrição, não gasta banda nem tempo
            if moto.get('descricao') and moto['descricao'] != "Descrição não capturada":
                continue

            print(f"[{i+1}/{len(motos)}] Coletando: {moto['titulo'][:30]}...")
            
            try:
                page.goto(moto['link'], wait_until="domcontentloaded", timeout=60000)
            
                # print("🔑 PAUSA PARA LOGIN: Se não estiver logado, faça isso agora na janela do navegador.")
                # print("Pressione ENTER no terminal quando estiver pronto para continuar...")
                # input() # O script fica parado aqui esperando você logar
                # Simular interação humana inicial
                page.mouse.wheel(0, 300)
                time.sleep(random.uniform(1.5, 3.0))

                descricao = ""
                if "mercadolivre" in moto['link']:
                    page.wait_for_selector('.ui-pdp-description__content', timeout=10000)
                    descricao = page.locator('.ui-pdp-description__content').inner_text()
                
                elif "webmotors" in moto['link']:
                    page.wait_for_selector('p.AdvertiserDescription__description', timeout=7000)
                    descricao = page.locator('p.AdvertiserDescription__description').inner_text()

                moto['descricao'] = descricao.strip()
                
            except Exception as e:
                print(f"⚠️ Falha no link {i+1}: {e}")
                moto['descricao'] = "Descrição não capturada"

            # SALVAMENTO INCREMENTAL: Salva a cada 1 registro
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(motos, f, ensure_ascii=False, indent=4)

            # Delay aleatório para evitar o próximo CAPTCHA
            time.sleep(random.uniform(5, 10))

        context.close()
    
    print("✅ Processo finalizado ou pausado. Progresso salvo em:", output_file)

if __name__ == "__main__":
    description_extractor()