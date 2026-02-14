"""
Multivariate Gaussian Distribution (MVGD)実装
"""

import numpy as np
from . import utils

def match_rgb(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """RGB色空間でMVGDによるカラーマッチング"""
    
    h, w, c = src.shape
    
    # ピクセルを行ベクトルとして展開
    s = src.reshape(-1, 3).astype(np.float64)
    r = ref.reshape(-1, 3).astype(np.float64)
    
    # 平均色を計算
    mu_s = np.mean(s, axis=0)
    mu_r = np.mean(r, axis=0)
    
    # 3x3の共分散行列を計算
    cov_s = np.cov(s, rowvar=False, bias=True)
    cov_r = np.cov(r, rowvar=False, bias=True)
    
    # 共分散行列の平方根と逆平方根を計算
    S_r_sqrt, _ = utils.cov_sqrt_and_inv(cov_r)
    _, S_s_inv_sqrt = utils.cov_sqrt_and_inv(cov_s)
    
    # MVGDの変換行列Aを計算
    A = S_r_sqrt @ S_s_inv_sqrt
    
    # 色変換を適用
    mapped = ((s - mu_s) @ A.T) + mu_r
    
    # 元の画像形状に戻す
    out = mapped.reshape(h, w, 3)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out


def match_lab_l(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Lab色空間でLチャネルのみMVGDによるマッチング"""
    
    # RGB -> Lab色空間に変換
    src_lab = utils.rgb2lab(src.astype(np.float64))
    ref_lab = utils.rgb2lab(ref.astype(np.float64))
    
    # Lチャネルを1次元配列に展開
    s = src_lab[..., 0].ravel().astype(np.float64)
    r = ref_lab[..., 0].ravel().astype(np.float64)
    
    # 平均と分散を計算
    mu_s = np.mean(s)
    mu_r = np.mean(r)
    var_s = np.var(s)
    var_r = np.var(r)
    
    # 1次元ガウス分布のマップを適用
    # 標準偏差がゼロの場合の処理
    std_s = np.sqrt(var_s) if var_s > 0 else 1.0
    std_r = np.sqrt(var_r)
    
    scale = std_r / std_s
    mapped_L = (s - mu_s) * scale + mu_r
    
    # 結果をLチャネルに設定
    out_lab = src_lab.copy()
    out_lab[..., 0] = mapped_L.reshape(src_lab.shape[0], src_lab.shape[1])
    
    # Lab -> RGB色空間に変換
    out_rgb = utils.lab2rgb(out_lab)
    
    return out_rgb

