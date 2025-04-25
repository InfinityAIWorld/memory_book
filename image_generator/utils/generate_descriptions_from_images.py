import openai
import base64
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def gerar_descricao_por_imagem(img_path):
    base64_image = encode_image(img_path)
    file_name = os.path.basename(img_path)

    print(f"🧠 Gerando descrição para: {file_name}")

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "Você é um especialista em estilo visual e composição artística."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Descreva com detalhes o estilo visual e traço artístico dessa imagem. Foque em como alguém poderia desenhar algo semelhante para uma página de livro de colorir infantil."},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }}
                ]
            }
        ],
        max_tokens=300
    )

    descricao = response["choices"][0]["message"]["content"]
    return file_name, descricao
