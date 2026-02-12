"""
Reinhard実装
"""

import numpy as np
from . import utils

def match_channel(src_chan: np.ndarray, ref_chan: np.ndarray) -> np.ndarray:
    """単一チャンネルのReinhardマッチング"""
    
    # チャンネルデータを float に変換
    src = src_chan.astype(np.float64)
    ref = ref_chan.astype(np.float64)
    
    # 統計量を計算
    src_mean = np.mean(src)
    ref_mean = np.mean(ref)
    src_std = np.std(src)
    ref_std = np.std(ref)
    
    # 標準偏差がゼロの場合の処理
    if src_std == 0:
        return src_chan
    
    # Reinhard の色変換式を適用
    A = ref_std / src_std
    out = (src - src_mean) * A + ref_mean
    
    # 値を 0-255 にクリップ
    out = np.clip(out, 0, 255)
    return out.astype(src_chan.dtype)


def match_rgb(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """RGB色空間でReinhardマッチング"""
    
    out = np.empty_like(src, dtype=np.float64)
    for ch in range(src.shape[2]):
        out[..., ch] = match_channel(src[..., ch], ref[..., ch])
    
    return out


def match_lab_l(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """LAB色空間でLチャネルのみReinhardマッチング"""
    
    # RGB -> Lab(0-255)
    src_lab = utils.rgb2lab(src)
    ref_lab = utils.rgb2lab(ref)
    
    # L: 0-255
    src_L = src_lab[..., 0]
    ref_L = ref_lab[..., 0]
    
    # Reinhardマッチング
    src_lab[..., 0] = match_channel(src_L, ref_L)
    
    # Lab -> RGB
    return utils.lab2rgb(src_lab)
