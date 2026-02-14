"""color_match package"""

import argparse
import os
import numpy as np
from PIL import Image
from . import utils
from . import hm
from . import reinhard
from . import mkl
from . import mvgd

def match(src_img: np.ndarray, ref_img: np.ndarray, method: str, mode: str) -> np.ndarray:
    '''カラーマッチング'''

    if method == "hm":
        if mode == "rgb":
            matched_img = hm.match_rgb(src_img, ref_img)
        else:
            matched_img = hm.match_lab_l(src_img, ref_img)
    elif method == "reinhard":
        if mode == "rgb":
            matched_img = reinhard.match_rgb(src_img, ref_img)
        else:
            matched_img = reinhard.match_lab_l(src_img, ref_img)
    elif method == "mvgd":
        if mode == "rgb":
            matched_img = mvgd.match_rgb(src_img, ref_img)
        else:
            matched_img = mvgd.match_lab_l(src_img, ref_img)
    elif method == "mkl":
        if mode == "rgb":
            matched_img = mkl.match_rgb(src_img, ref_img)
        else:
            matched_img = mkl.match_lab_l(src_img, ref_img)
    elif method == 'hm-mvgd-hm':
        if mode == "rgb":
            matched_img = hm.match_rgb(src_img, ref_img)
            matched_img = mvgd.match_rgb(matched_img, ref_img)
            matched_img = hm.match_rgb(matched_img, ref_img)
        else:
            matched_img = hm.match_lab_l(src_img, ref_img)
            matched_img = mvgd.match_lab_l(matched_img, ref_img)
            matched_img = hm.match_lab_l(matched_img, ref_img)
    elif method == 'hm-mkl-hm':
        if mode == "rgb":
            matched_img = hm.match_rgb(src_img, ref_img)
            matched_img = mkl.match_rgb(matched_img, ref_img)
            matched_img = hm.match_rgb(matched_img, ref_img)
        else:
            matched_img = hm.match_lab_l(src_img, ref_img)
            matched_img = mkl.match_lab_l(matched_img, ref_img)
            matched_img = hm.match_lab_l(matched_img, ref_img)
    else:
        raise ValueError(f"不明な方法: {method}")
    
    matched_img = np.clip(matched_img, 0, 255).astype(np.uint8)
    return matched_img


def main() -> int:
    """コマンドラインインターフェースのエントリポイント"""

    # 引数解析
    p = argparse.ArgumentParser(description="Color Matching")
    p.add_argument("source", nargs='?', help="入力画像パス")
    p.add_argument("reference", nargs='?', help="参照画像パス")
    p.add_argument("-o", "--output", help="出力画像パス", default="./output.png")
    p.add_argument("-m", "--method", choices=("hm", "reinhard", "mvgd", "mkl", "hm-mvgd-hm", "hm-mkl-hm"), default="mkl")
    p.add_argument("--mode", choices=("rgb", "lab"), default="rgb")
    args = p.parse_args()

    if not args.source or not args.reference:
        p.error('source and reference are required')
        return 1

    # 画像読み込み
    src_img = np.array(Image.open(args.source).convert("RGB"))
    ref_img = np.array(Image.open(args.reference).convert("RGB"))

    # カラーマッチング
    matched_img = match(src_img, ref_img, args.method, args.mode)
    
    # 画像保存
    Image.fromarray(matched_img).save(args.output)
    if os.path.exists(args.output):
        return 0
    else:
        print(f"保存に失敗しました: {args.output}")
        return 1