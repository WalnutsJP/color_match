# Reinhard

--------------------------------------------------

## ■概要

参照画像の色の統計的特性(平均と標準偏差)に合わせて入力画像を色変換する手法

公開元論文: [Color transfer between images](https://www.cs.tau.ac.il/~turkel/imagepapers/ColorTransfer.pdf) by E.Reinhard, M.Adhikhmin, B.Gooch, P.Shirley (2001)

--------------------------------------------------

## ■基本原理

Reinhardの色変換は、以下の考え方に基づいています：

1. 対象画像と参照画像の**色の統計量**（平均値と標準偏差）を計算

2. 平均と標準偏差を利用して以下の計算で色変換：  
  $$I_{\text{out}} = (I_{\text{src}} - \mu_{\text{src}}) \times \frac{\sigma_{\text{ref}}}{\sigma_{\text{src}}} + \mu_{\text{ref}}$$

- $I_{\text{src}}$: 入力画像のピクセル値
- $\mu_{\text{src}}$: 入力画像の平均値
- $\mu_{\text{ref}}$: 参照画像の平均値
- $\sigma_{\text{src}}$: 入力画像の標準偏差
- $\sigma_{\text{ref}}$: 参照画像の標準偏差

--------------------------------------------------

## ■実装上の詳細

1. チャンネルデータをfloat型に変換

```python
src = src_chan.astype(np.float64)
ref = ref_chan.astype(np.float64)
```

1. 統計量を計算

```python
src_mean = np.mean(src) # 平均
ref_mean = np.mean(ref)
src_std = np.std(src)   # 標準偏差
ref_std = np.std(ref)
```

2. 標準偏差がゼロの場合の処理は0除算となる為、元の画像を返す

```python
if src_std == 0:
    return src_chan
```

3. Reinhardの色変換を適応

```python
out = (src - src_mean) * (ref_std / src_std) + ref_mean
```

4. 値を0-255にクリップ

```python
out = np.clip(out, 0, 255)
```

--------------------------------------------------

## ■特徴とトレードオフ

### 利点

- 計算が高速
  - **時間計算量**: $O(H \times W)$  
    H: 画像の幅  
    W: 画像の高さ
  - **空間計算量**: $O(1)$
- 数値的に安定(除算以外の複雑な操作がない)

### 欠点

- 統計量(平均と標準偏差)のみに基づいており、ヒストグラムマッチングのように全体の色分布を考慮しない
- 色分布が非正規分布の場合、無理に平均・標準偏差に合わせることで不自然な色になることがある
- チャンネル間で独立した計算の為、チャンネル間の相関は考慮されない
