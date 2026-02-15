# Multivariate Gaussian Distribution (MVGD)

--------------------------------------------------

## ■概要

参照画像の平均と共分散による **多変量正規分布(Multivariate Gaussian Distribution)** に合わせて入力画像を色変換する手法

公開元論文: [Transformation of the Multivariate Generalized Gaussian Distribution for Image Editing](https://www.researchgate.net/publication/320827643_Transformation_of_the_Multivariate_Generalized_Gaussian_Distribution_for_Image_Editing)
by Hristina Hristova, Olivier Le Meur, Rémi Cozot, Kadi Bouatouch (2001)

--------------------------------------------------

## ■基本原理

Multivariate Gaussian Distribution (MVGD)は、以下の考え方に基づいています：

1. 入力画像と参照画像の平均・共分散行列を計算
  - 平均 $\boldsymbol{\mu}$ は色の重心を表す
  - 共分散行列 $\boldsymbol{\Sigma}$ は色の広がりとチャネル間の相関を表す

2. 共分散行列の平方根・逆平方根を計算

3. 平均・共分散行列を利用して以下の計算で色変換  
  変換行列 $A$ は以下のように定義される：  
  $$A = \Sigma_{\text{ref}}^{1/2} \Sigma_{\text{src}}^{-1/2}$$  
  色変換は以下の式で行われる：  
  $$I_{\text{out}} = (I_{\text{src}} - \mu_{\text{src}}) \times A + \mu_{\text{ref}}$$

- $I_{\text{src}}$ : 入力画像の色ベクトル
- $\boldsymbol{\mu}_{\text{src}}$ : 入力画像の平均
- $\boldsymbol{\mu}_{\text{ref}}$ : 参照画像の平均
- $\boldsymbol{\Sigma}_{\text{src}}$ : 入力画像の共分散行列
- $\boldsymbol{\Sigma}_{\text{ref}}$ : 参照画像の共分散行列
- $\boldsymbol{\Sigma}_{\text{src}}^{-1/2}$ : 入力画像の共分散行列の逆平方根
- $\boldsymbol{\Sigma}_{\text{ref}}^{1/2}$ : 参照画像の共分散行列の平方根

**1次元の場合（Lチャネルのみなど）**

- 共分散行列 $\boldsymbol{\Sigma}$ の代わりに標準偏差 $\sigma$ を利用  
  $$I_{\text{out}} = (I_{\text{src}} - \mu_{\text{src}}) \frac{\sigma_{\text{ref}}}{\sigma_{\text{src}}} + \mu_{\text{ref}}$$
- 分散を利用した計算は Reinhard による色変換と同じの為、1チャンネルによる色変換の場合は Reinhard と実装上の違いはない

--------------------------------------------------

## ■実装上の詳細

1. **ピクセルを行ベクトルに展開**

```python
s = src.reshape(-1, 3).astype(np.float64)
r = ref.reshape(-1, 3).astype(np.float64)
```

- 各行が1ピクセル、列がチャネル

2. **平均ベクトルの計算**

```python
mu_s = np.mean(s, axis=0)
mu_r = np.mean(r, axis=0)
```

3. **共分散行列の計算**

```python
cov_s = np.cov(s, rowvar=False, bias=True)
cov_r = np.cov(r, rowvar=False, bias=True)
```

4. **共分散行列の平方根と逆平方根の計算**

```python
S_r_sqrt, _ = utils.cov_sqrt_and_inv(cov_r)
_, S_s_inv_sqrt = utils.cov_sqrt_and_inv(cov_s)
```

5. **MVGDの変換行列Aを計算**

```python
A = S_r_sqrt @ S_s_inv_sqrt
```

6. **色変換を適用**

```python
mapped = ((s - mu_s) @ A.T) + mu_r
```

7. **形状の復元とクリップ**

```python
out = mapped.reshape(h, w, 3)
out = np.clip(out, 0, 255).astype(np.uint8)
```

--------------------------------------------------

## ■特徴とトレードオフ

### 利点

- 標準偏差の代わりに共分散行列を用いている為、色の広がりだけではなくチャンネル間の相関まで考慮されている

### 欠点

- 統計量(平均と標準偏差)のみに基づいており、ヒストグラムマッチングのように全体の色分布を考慮しない
- 色分布が非正規分布の場合、無理に平均・共分散に合わせることで不自然な色になることがある
- 参照や入力の色がほぼ1色に近いと共分散がランク落ちし、逆平方根が不安定になる
  - 実装では `eps` を加えて安定化している
- 共分散の計算が $O(H \times W)$、固有値分解が $O(d^3)$（$d=3$）となり、ヒストグラムマッチングより計算コストがやや重い
