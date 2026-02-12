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

def match(source: str, reference: str, output: str, method: str, mode: str):
    '''カラーマッチング'''

    # 画像読み込み
    src_img = np.array(Image.open(source).convert("RGB"))
    ref_img = np.array(Image.open(reference).convert("RGB"))

    # 色変換
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

    # 画像保存
    matched_img = np.clip(matched_img, 0, 255).astype(np.uint8)
    Image.fromarray(matched_img).save(output)


def main() -> int:
    """コマンドラインインターフェースのエントリポイント"""

    # 引数解析
    p = argparse.ArgumentParser(description="Color Matching")
    p.add_argument("source", help="入力画像パス")
    p.add_argument("reference", help="参照画像パス")
    p.add_argument("-o", "--output", help="出力画像パス", default="./output.png")
    p.add_argument("-m", "--method", choices=("hm", "reinhard", "mvgd", "mkl", "hm-mvgd-hm", "hm-mkl-hm"), default="mkl")
    p.add_argument("--mode", choices=("rgb", "lab"), default="rgb")
    args = p.parse_args()

    # カラーマッチング
    match(args.source, args.reference, args.output, args.method, args.mode)
    if os.path.exists(args.output):
        return 0
    else:
        print(f"保存に失敗しました: {args.output}")
        return 1
