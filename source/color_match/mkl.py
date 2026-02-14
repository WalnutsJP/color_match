"""
Monge-Kantorovich Linearization (MKL)実装
"""

import numpy as np
from . import utils

def match_rgb(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """RGB色空間でMKLによるカラー・マッチング"""

    h, w, c = src.shape

    # ピクセルを行ベクトルとして展開
    s = src.reshape(-1, 3).astype(np.float64)
    r = ref.reshape(-1, 3).astype(np.float64)

    # 列ごとの平均色を計算
    mu_s = np.mean(s, axis=0)
    mu_r = np.mean(r, axis=0)

    # 3x3の分散共分散行列を計算
    cov_s = np.cov(s, rowvar=False, bias=True)
    cov_r = np.cov(r, rowvar=False, bias=True)

    # 共分散行列の平方根と逆平方根を計算
    S_s_sqrt, S_s_inv_sqrt = utils.cov_sqrt_and_inv(cov_s)

    # MKLの変換行列Aを計算
    middle = utils.spd_mat_sqrt(S_s_sqrt @ cov_r @ S_s_sqrt)
    A = S_s_inv_sqrt @ middle @ S_s_inv_sqrt

    # 色変換を適用
    mapped = ((s - mu_s) @ A.T) + mu_r

    # 元の画像形状に戻す
    out = mapped.reshape(h, w, 3)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


def match_lab_l(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Lab色空間でLチャネルのみMKLによるカラー・マッチング"""
    
    # RGB -> Lab
    src_lab = utils.rgb2lab(src.astype(np.float64))
    ref_lab = utils.rgb2lab(ref.astype(np.float64))

    # Lチャンネルを1次元展開
    s = src_lab[..., 0].ravel().astype(np.float64)
    r = ref_lab[..., 0].ravel().astype(np.float64)

    # 列ごとの平均色を計算
    mu_s, mu_r = s.mean(), r.mean()

    # 標準偏差を計算
    std_s, std_r = s.std(), r.std()

    # Lチャネルに対してガウスOTを適用
    scale = std_r / max(std_s, 1e-6)
    mapped_L = (s - mu_s) * scale + mu_r

    out_lab = src_lab.copy()
    out_lab[..., 0] = mapped_L.reshape(src_lab.shape[0], src_lab.shape[1])

    # Lab -> RGB
    out_rgb = utils.lab2rgb(out_lab)

    # ここで out_rgb は 0..255 の範囲を想定してクリップ & uint8 化
    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
    return out_rgb
