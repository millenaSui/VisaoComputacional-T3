"""
Módulo principal para processar imagens em um diretório específico. Ele verifica 
a existência de imagens com extensões válidas, processa cada imagem encontrada e 
salva os resultados em um diretório de saída.
"""

import os

from src.images import process_images

INPUT_DIR = './dataset'
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    ext = ('.jpg', '.jpeg', '.png', '.bmp')
    imagens = []

    if os.path.exists(INPUT_DIR):
        for arquivo in os.listdir(INPUT_DIR):
            if arquivo.lower().endswith(ext):
                imagens.append(os.path.join(INPUT_DIR, arquivo))

    if not imagens:
        print(f"[ERRO] Nenhuma imagem encontrada na pasta {INPUT_DIR}.")
        return

    print(f"[INFO] Encontradas {len(imagens)} imagens.")
    for img_path in sorted(imagens):
        print(f"[INFO] Processando {os.path.basename(img_path)}...")
        process_images(img_path)

if __name__ == "__main__":
    main()
