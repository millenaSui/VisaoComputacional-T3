"""
Módulo de funções utilitárias para processamento de imagens. Ele fornece 
funções para ordenar pontos, calcular áreas de quadriláteros, verificar
se um quadrilátero está contido dentro de outro e medir a complexidade
visual (textura) dentro de um quadrilátero.
"""

import cv2
import numpy as np

def sort_points(pts):
    """
    Ordena pontos colocando-os em ordem: topo-esquerdo, topo-direito, 
    base-direita, base-esquerda, para garantir consistência na retificação
    da perspectiva.

    :param pts: Array de pontos (4, 2).
    :return: Array de pontos ordenados (4, 2).
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect


def get_corners(contorno):
    """
    Seleciona os quatro cantos de um contorno aproximado, visando
    encontrar os pontos mais extremos de cada lado do contorno.

    :param contorno: Contorno aproximado (N, 1, 2).
    
    :return: Array de quatro pontos (4, 2).
    """
    pts = contorno.reshape(-1, 2)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(diff)]
    bl = pts[np.argmax(diff)]

    return np.array([tl, tr, br, bl], dtype="float32")


def calculate_area_quad(pts):
    """
    Calcula a área de um quadrilátero definido por quatro pontos
    usando a fórmula do polígono.

    :param pts: Array de pontos (4, 2).
    """

    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def inner(inner_pts, outer_pts):
    """
    Verifica se o candidato está fisicamente contido no alvo maior.
    Usa margens elásticas de 15% para suportar perspectivas distorcidas.
    
    :param inner_pts: Pontos do candidato (4, 2).
    :param outer_pts: Pontos do alvo maior (4, 2).

    :return: True se o candidato estiver dentro do alvo, False caso contrário.
    """
    ix, iy, iw, ih = cv2.boundingRect(inner_pts)
    ox, oy, ow, oh = cv2.boundingRect(outer_pts)

    margem_w = ow * 0.15
    margem_h = oh * 0.15

    reslt = (ix >= ox - margem_w and iy >= oy - margem_h and
             ix + iw <= ox + ow + margem_w and iy + ih <= oy + oh + margem_h)

    return reslt


def calculate_inner_texture(gray_img, pts):
    """
    Mede a complexidade visual (textura/tinta) dentro de um quadrilátero.
    
    :param gray_img: Imagem em escala de cinza.
    :param pts: Pontos do quadrilátero (4, 2).

    :return: Variância da Laplaciana da região interna.
    """
    x, y, w, h = cv2.boundingRect(np.int32(pts))
    x, y = max(0, x), max(0, y)
    crop = gray_img[y:y+h, x:x+w]

    if crop.size == 0:
        return 0
    return cv2.Laplacian(crop, cv2.CV_64F).var()


def auto_canny(image, sigma=0.33):
    """
    Calcula os limites das border dinamicamente com base na iluminação da própria imagem.
    
    :param image: Imagem em escala de cinza.
    :param sigma: Fator de ajuste para os limites.
    """
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    return cv2.Canny(image, lower, upper)
