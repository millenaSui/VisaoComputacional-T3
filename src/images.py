"""
Módulo para processar imagens. Ele carrega uma imagem, verifica se foi carregada corretamente
e imprime informações sobre o processo. Para cada imagem, ele encontra o melhor quadro/frame,
retifica a perspectiva e salva o resultado em um diretório de saída.
"""

import os
import cv2
import numpy as np

from src.utils import (
    auto_canny,
    calculate_inner_texture,
    sort_points,
    get_corners,
    calculate_area_quad,
    inner
)

def process_images(path_img, path_output):
    """
    Processa uma imagem, detecta o melhor quadro, retifica a perspectiva e salva o resultado.

    :param path_img: Caminho da imagem a ser processada.
    """
    img = cv2.imread(path_img)
    if img is None:
        print(f"[ERRO] Não foi possível carregar a imagem {path_img} usando OpenCV")
        return

    file_name = os.path.basename(path_img)
    print(f"\n[INFO] Processando {file_name}...")

    points = find_best_frame(img) # encontra o melhor candidato de quadro na imagem

    if points is None:
        print(f"[ERRO] Quadro não identificado em {file_name}. Ignorada.")
        return

    # alinha perspectiva do quadro
    pts_src = sort_points(points)
    (tl, tr, br, bl) = pts_src

    # calcula a largura do novo quadro
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    max_w = max(int(widthA), int(widthB))

    # calcula a altura do novo quadro
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    max_h = max(int(heightA), int(heightB))

    pts_dst = np.float32([ # destino dos pontos
        [0, 0],
        [max_w - 1, 0],
        [max_w - 1, max_h - 1],
        [0, max_h - 1]
    ])

    # calcula a matriz de transformação e aplica a retificação
    matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
    img_retificada = cv2.warpPerspective(img, matrix, (max_w, max_h))

    # garantie corte de eventuais reflexos de moldura
    margin_w = int(max_w * 0.03)
    margin_h = int(max_h * 0.03)

    if max_w > 2 * margin_w and max_h > 2 * margin_h:
        img_final = img_retificada[margin_h:max_h - margin_h, margin_w:max_w - margin_w]
    else:
        img_final = img_retificada

    out_path = os.path.join(path_output, f"{file_name}")
    cv2.imwrite(out_path, img_final)
    print(f"Salvo com sucesso: {out_path}")


def find_best_frame(img):
    """
    Encontra o melhor quadro na imagem.

    :param img: Imagem a ser processada.
    :return: Pontos do melhor quadro encontrado, ou None se nenhum for encontrado.
    """
    ratio = img.shape[0] / 800.0
    width = int(img.shape[1] / ratio)
    img_resized = cv2.resize(img, (width, 800))

    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    borders_map = []

    # auto canny adaptado à luz da foto
    borders_map.append(auto_canny(blur))

    # relevos físicos de molduras complexas
    kernel_grad = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    grad = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, kernel_grad)
    _, grad_thresh = cv2.threshold(grad, 50, 255, cv2.THRESH_BINARY)
    borders_map.append(grad_thresh)

    # contraste local adaptado a variações de iluminação
    thresh_adapt = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5
        )
    borders_map.append(thresh_adapt)

    candidates = []
    area_img = width * 800

    for border in borders_map:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        fechado = cv2.morphologyEx(border, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(fechado, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            contour_a = cv2.contourArea(c)

            # quadro sem recortes
            hull = cv2.convexHull(c)
            area_hull = cv2.contourArea(hull)
            if area_hull == 0:
                continue

            solidez = contour_a / float(area_hull)
            if solidez < 0.85:
                continue

            if area_img * 0.10 < contour_a < area_img * 0.99:
                peri = cv2.arcLength(c, True)
                aprox = cv2.approxPolyDP(c, 0.04 * peri, True)

                if len(aprox) == 4: # quatro pontos, candidato a quadro
                    pts = aprox.reshape(4, 2)
                else: # não é um quadrilátero (pode ser um quadro com recortes)
                    pts = get_corners(c)

                area_quad = calculate_area_quad(pts)
                if area_img * 0.10 < area_quad < area_img * 0.99:
                    _, _, w, h = cv2.boundingRect(pts)
                    if w > 50 and h > 50:
                        textura = calculate_inner_texture(gray, pts)
                        candidates.append({"pts": pts, "area": area_quad, "textura": textura})

    if not candidates:
        return None

    # maior área p/ menor
    candidates = sorted(candidates, key=lambda x: x["area"], reverse=True)
    unique_candidates = []

    # remove duplicatas
    for cand in candidates:
        duplicate = False
        cX, cY = np.mean(cand["pts"], axis=0)
        for u in unique_candidates:
            if abs(cand["area"] - u["area"]) / u["area"] < 0.15:
                uX, uY = np.mean(u["pts"], axis=0)
                dist = np.sqrt((cX - uX)**2 + (cY - uY)**2)
                if dist < 80:
                    duplicate = True
                    break
        if not duplicate:
            unique_candidates.append(cand)

    if not unique_candidates:
        return None

    target = unique_candidates[0]

    # se existe um retângulo menor que tenha uma textura de pintura
    # assume que a parte de fora é a moldura e descarta
    for cand in unique_candidates[1:]:
        if 0.20 * target["area"] < cand["area"] < 0.95 * target["area"]:
            if inner(cand["pts"], target["pts"]):
                if cand["textura"] > 50: 
                    target = cand

    return target["pts"] * ratio
