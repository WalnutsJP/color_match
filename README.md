# color_match

Pythonスクリプトによる画像の色合わせ(Color MatchingもしくはColor Transfer)を行います

<img width="1000" src="images/image_top.png">

**※本リポジトリは自習目的で作成されており、尚且つコーディングやドキュメント作成にはAIが活用されています**  
**実装やドキュメントには誤りがある可能性があるのでご注意ください**

ツールとして利用したい方は[color-matcher](https://github.com/hahnec/color-matcher)等の既存のPythonモジュールの利用を推奨します

--------------------------------------------------

## ■主な機能

本ツールは以下の手法が利用可能です

- **[Histogram Matching (HM)](./document/hm.md)**:  
  ヒストグラムマッチングによる古典的なカラーマッチング手法
- **[Reinhard](./document/reinhard.md)**:  
  参照画像の色の統計的特性(平均と標準偏差)に合わせて入力画像を変換する手法
- **[Multivariate Gaussian Distribution (MVGD)](./document/mvgd.md)**:  
  参照画像の平均と共分散による多変量正規分布(Multivariate Gaussian Distribution)に合わせて入力画像を色変換する手法
- **[Monge-Kantorovich Linearization (MKL)](./document/mkl.md)**:  
  最適輸送理論(Monge-Kantorovich理論)を応用したカラーマッチング手法
- **HM-MVGD-HM**:  
  HM -> MVGD -> HM を連鎖させた複合手法
- **HM-MKL-HM**:  
  HM -> MKL -> HM を連鎖させた複合手法

各手法の品質と速度の比較は以下の通りです

| 手法       | 品質     | 速度    |
|------------|:-------:|:-------:|
| HM         | ★☆☆☆ | ★★★★ |
| Reinhard   | ★★☆☆ | ★★★★ |
| MVGD       | ★★★☆ | ★★★☆ |
| MKL        | ★★★☆ | ★★★☆ |
| HM-MVGD-HM | ★★★★ | ★☆☆☆ |
| HM-MKL-HM  | ★★★★ | ★☆☆☆ |

本ツールでは品質と速度のバランスの観点からMKLをデフォルト手法として採用しています

**※注意点**

現状の実装では画像のアルファチャンネルは考慮していません

---------------------------------------------------

## ■ファイル構成  

```
📂 color_match/
 ├── 📂 document/ : ドキュメントフォルダ
 |    ├── 📄hm.md : HM技術詳細ドキュメント
 |    ├── 📄reinhard.md : Reinhard技術詳細ドキュメント
 |    ├── 📄mvgd.md : MVGD技術詳細ドキュメント
 |    ├── 📄mkl.md : MKL技術詳細ドキュメント
 ├── 📂 images/ : 画像フォルダ
 ├── 📂 source/ : ソースコードフォルダ
 |    ├── 📂 color_match/
 |    |    ├── 📄__init__.py
 |    |    ├── 📄__main__.py
 |    |    ├── 📄hm.py : HM実装
 |    |    ├── 📄reinhard.py : Reinhard実装
 |    |    ├── 📄mvgd.py : MVGD実装
 |    |    ├── 📄mkl.py : MKL実装
 |    |    └── 📄utils.py : ユーティリティ関数
 |    └── 📄color_match_app.py : アプリケーション起動用
 ├── 📄match_app.bat : GUIによるカラーマッチング
 ├── 📄match_hm_rgb.bat : コマンドラインによるHM(RGB)カラーマッチング
 ├── 📄match_hm_lab.bat : コマンドラインによるHM(LAB)カラーマッチング
 ├── 📄match_reinhard_rgb.bat : コマンドラインによるReinhard(RGB)カラーマッチング
 ├── 📄match_reinhard_lab.bat : コマンドラインによるReinhard(LAB)カラーマッチング
 ├── 📄match_mvgd_rgb.bat : コマンドラインによるMVGD(RGB)カラーマッチング
 ├── 📄match_mvgd_lab.bat : コマンドラインによるMVGD(LAB)カラーマッチング
 ├── 📄match_mkl_rgb.bat : コマンドラインによるMKL(RGB)カラーマッチング
 ├── 📄match_mkl_lab.bat : コマンドラインによるMKL(LAB)カラーマッチング
 ├── 📄pyproject.toml : Pythonモジュールセットアップファイル
 └── 📄README.md : 本ドキュメントファイル
```

--------------------------------------------------

## ■利用手順

**アプリケーションから利用**

1. match_app.bat を実行  
  ※初回起動時はPython仮想環境の構築に時間がかかります

**コマンドラインから利用**
  
1. 色変換したい画像とリファレンス画像の2枚を選択し、match_〇〇.bat のいずれかにドラッグアンドドロップ  
  ※初回起動時はPython仮想環境の構築に時間がかかります
2. output.pngにカラーマッチ画像が出力されます

.bat から `python -m color_match` を呼び出してカラーマッチングを行いますが、渡される引数は以下の通りです

- **第1引数** : カラーマッチングを行う画像のパス
- **第2引数** : リファレンス画像のパス
- **--output もしくは -o** : 出力画像のパス
- **--method もしくは -m** : カラーマッチング手法
  - **hm** : Histogram Matching
  - **reinhard** : Reinhard
  - **mvgd** : Multivariate Gaussian Distribution (MVGD)
  - **mkl** : Monge-Kantorovich Linearization (MKL)
  - **hm-mvgd-hm** : HM-MVGD-HM複合法
  - **hm-mkl-hm** : HM-MKL-HM複合法
- **--mode** : モード
  - **rgb** : RGBチャンネルごとに独立してカラーマッチング
  - **lab** : RGBをLAB色空間に変換し、L(輝度)のみカラーマッチング

**Pythonから利用**

1. 以下のコマンドでPythonにcolor_matchモジュールをインストール
  
  ```bash
  pip install .
  ```

2. color_matchモジュールの `color_match.match()` を呼び出してカラーマッチング

使用例：

```python
import color_match

# 画像読み込み
src_img = np.array(Image.open('input.png').convert('RGB'))
ref_img = np.array(Image.open('reference.png').convert('RGB'))

# カラーマッチング
matched_img = color_match.match(src_img, ref_img, 'mkl', 'rgb')

# 画像保存
Image.fromarray(matched_img).save('output.png')
```

--------------------------------------------------

## ■ライセンス

[Apache 2.0 License](https://github.com/apache/.github/blob/main/LICENSE)