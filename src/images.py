"""
Módulo para processar imagens. Ele carrega uma imagem, verifica se foi carregada corretamente
e imprime informações sobre o processo.
"""

import os
import cv2

def process_images(path_img):
    img = cv2.imread(path_img)
    if img is None:
        print(f"[ERRO] Não foi possível carregar a imagem {path_img} usando OpenCV")
        return

    file_name = os.path.basename(path_img)
    print(f"\n[INFO] Processando {file_name}...")
