"""
ヒストグラムマッチング実装
"""

import numpy as np
from . import utils

def match_channel(src_chan: np.ndarray, ref_chan: np.ndarray) -> np.ndarray:
    """単一チャンネルのヒストグラムマッチング"""

    # チャンネルデータを1次元配列に変換
    src = src_chan.ravel()
    ref = ref_chan.ravel()

    # 256段階のヒストグラムを計算
    src_hist = np.bincount(src, minlength=256).astype(np.float64)
    ref_hist = np.bincount(ref, minlength=256).astype(np.float64)

    # CDF(累積分布関数) == 累積ヒストグラム を計算
    src_cdf = np.cumsum(src_hist)   # 累積和を計算
    src_cdf /= src_cdf[-1]          # 正規化
    ref_cdf = np.cumsum(ref_hist)
    ref_cdf /= ref_cdf[-1]

    # ヒストグラムマッチングを適応
    lut = np.interp(src_cdf, ref_cdf, np.arange(256)).astype(np.uint8)
    return lut[src_chan]


def match_rgb(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """RGB色空間でヒストグラムマッチング"""

    out = np.empty_like(src)
    for ch in range(src.shape[2]):
        out[..., ch] = match_channel(src[..., ch], ref[..., ch])
    return out


def match_lab_l(src: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """LAB色空間でLチャネルのみヒストグラムマッチング"""

    # RGB -> Lab(0-255)
    src_lab = utils.rgb2lab(src)
    ref_lab = utils.rgb2lab(ref)
    
    # L: 0-255
    src_L = src_lab[..., 0].astype(np.uint8)
    ref_L = ref_lab[..., 0].astype(np.uint8)
    
    # ヒストグラムマッチング
    src_lab[..., 0] = match_channel(src_L, ref_L).astype(np.float64)
    
    # Lab -> RGB
    return utils.lab2rgb(src_lab)
