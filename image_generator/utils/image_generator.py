import openai
import requests
import os
from datetime import datetime

def gerar_imagem(prompt: str, model="dall-e-3", size="1024x1024") -> str:
    response = openai.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size=size
    ) 
    return response.data[0].url

def salvar_imagem(url: str, nome_arquivo: str, pasta_destino: str):
    response = requests.get(url)
    if response.status_code == 200:
        caminho = os.path.join(pasta_destino, nome_arquivo)
        with open(caminho, 'wb') as f:
            f.write(response.content)
        return caminho
    else:
        raise RuntimeError("Erro ao baixar imagem da URL")
