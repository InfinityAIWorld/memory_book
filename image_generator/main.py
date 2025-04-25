import os
import pandas as pd
import openai
import logging
from dotenv import load_dotenv
from tqdm import tqdm
from datetime import datetime
import time
from utils.image_generator import gerar_imagem, salvar_imagem
from utils.generate_descriptions_from_images import gerar_descricao_por_imagem

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
DOCUMENTOS_DIR = os.path.expanduser("~/Documents/ImagensGeradas")
os.makedirs(DOCUMENTOS_DIR, exist_ok=True)

logging.basicConfig(filename="logs/generation.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Carrega prompts + descrição de estilo
df = pd.read_csv("prompts.csv")
if "estilo" not in df.columns:
    df["estilo"] = ""

IMAGENS_POR_MINUTO = 1
INTERVALO = 60 / IMAGENS_POR_MINUTO
total_prompts = len(df)

print(f"🚀 Iniciando geração de {total_prompts} imagem(ns), com {IMAGENS_POR_MINUTO}/minuto...\n")

for index in tqdm(range(total_prompts), desc="Gerando imagens"):
    row = df.iloc[index]
    prompt_id = row["id"]
    prompt = row["prompt"]
    estilo = row.get("estilo", "")

    # Geração de descrição de estilo se estiver vazia
    if pd.isna(estilo) or estilo.strip() == "":
        ref_image_path = os.path.join("referencias", f"{prompt_id}.png")
        if os.path.exists(ref_image_path):
            _, estilo = gerar_descricao_por_imagem(ref_image_path)
            df.at[index, "estilo"] = estilo
            print(f"🖼️ Estilo gerado a partir da imagem {ref_image_path}")
        else:
            estilo = ""
            print(f"⚠️ Imagem de referência não encontrada para o ID {prompt_id}")

    prompt_final = f"{prompt} – estilo visual: {estilo}" if estilo else prompt

    print(f"⏳ [{index+1}/{total_prompts}] Gerando: \"{prompt[:40]}...\"")

    count = 0
    success = False
    while count < 3:
        try:
            url = gerar_imagem(prompt_final)
            nome = f"{prompt_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            caminho = salvar_imagem(url, nome, DOCUMENTOS_DIR)
            logging.info(f"[{prompt_id}] Imagem gerada e salva em: {caminho}")
            print(f"✅ [{index+1}/{total_prompts}] Imagem gerada com sucesso")
            print(f"💾 Imagem salva em: {caminho}\n")
            success = True
            break
        except Exception as e:
            count += 1
            print(f"⚠️ [{index+1}/{total_prompts}] Tentativa {count} falhou: {e}")
            logging.warning(f"[{prompt_id}] Tentativa {count} falhou: {e}")
            time.sleep(1)

    if not success:
        print(f"❌ [{index+1}/{total_prompts}] Erro após 3 tentativas\n")
        logging.error(f"[{prompt_id}] Erro definitivo após 3 tentativas")

    for remaining in range(int(INTERVALO), 0, -1):
        print(f"⏳ Aguardando próximo prompt em {remaining} segundos...", end="\r")
        time.sleep(1)
    print(" " * 60, end="\r")  # limpa a linha

# Atualiza o CSV com os estilos gerados
df.to_csv("prompts.csv", index=False)

print("🏁 Geração finalizada.")
