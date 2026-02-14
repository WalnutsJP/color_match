"""
カラーマッチング用ユーティリティ関数
"""

import numpy as np

try:
    # scikit-imageを利用
    import skimage.color

    def rgb2lab(rgb: np.ndarray) -> np.ndarray:
        """sRGB (uint8, 0-255) -> Lab"""

        # 入力を float に正規化 (0-1)
        rgb_f = rgb.astype(np.float64)
        rgb_f = rgb_f / 255.0

        # sRGB -> Lab
        return skimage.color.rgb2lab(rgb_f).astype(np.float64)

    def lab2rgb(lab: np.ndarray) -> np.ndarray:
        """Lab -> sRGB (uint8, 0-255)"""
        
        # Lab -> sRGB
        rgb_f = skimage.color.lab2rgb(lab)

        # uint8 に変換
        rgb_f = np.clip(rgb_f, 0.0, 1.0)
        rgb_u8 = (rgb_f * 255.0).astype(np.uint8)
        return rgb_u8
    
except ImportError:
    try:
        # OpenCV2を利用
        import cv2
        
        def rgb2lab(rgb: np.ndarray) -> np.ndarray:
            """sRGB (uint8, 0-255) -> Lab"""

            # convert RGB -> Lab (OpenCVの出力するLabの範囲はL:0-255, a:0-255, b:0-255)
            lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float64)
            return lab
        
        def lab2rgb(lab: np.ndarray) -> np.ndarray:
            """Lab -> sRGB (uint8, 0-255)"""

            rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            return rgb
        
    except ImportError:
        # NumPy のみで RGB <-> Lab 変換を実装

        def rgb2lab(rgb: np.ndarray) -> np.ndarray:
            """sRGB (uint8, 0-255) -> Lab"""
            
            # 入力を float に正規化 (0-1)
            rgb_f = rgb.astype(np.float64)
            rgb_f = rgb_f / 255.0

            # sRGB -> linear RGB
            rgb_linear = sRGBtoRGB(rgb_f)
            
            # RGB -> XYZ
            xyz = RGBtoXYZ(rgb_linear)

            # XYZ -> Lab(L:0-100, a:-128~127, b:-128~127)
            L, a, b = XYZtoLab(xyz)

            # Labの範囲を0～255にリスケール
            L = L * (255.0 / 100.0)
            a = a + 128.0
            b = b + 128.0
            
            return np.stack([L, a, b], axis=-1)
        
        def lab2rgb(lab: np.ndarray) -> np.ndarray:
            """Lab -> sRGB (uint8, 0-255)"""

            # Lab(L:0-100, a:-128~127, b:-128~127)
            lab = lab.astype(np.float64)
            L = lab[..., 0] * (100.0 / 255.0)
            a = lab[..., 1] - 128.0
            b = lab[..., 2] - 128.0

            # Lab -> XYZ
            xyz = LabtoXYZ(L, a, b)
            
            # XYZ -> RGB
            rgb_linear = XYZtoRGB(xyz)

            # linear RGB -> sRGB
            rgb_f = RGBtosRGB(rgb_linear)
            
            # uint8 に変換 (0-255)
            rgb_u8 = np.clip(rgb_f * 255.0, 0, 255).astype(np.uint8)
            return rgb_u8


def sRGBtoRGB(rgb_f):
    """sRGB(0-1) -> linear RGB(0-1)"""

    mask = rgb_f > 0.04045
    rgb_linear = np.where(
        mask,
        np.power((rgb_f + 0.055) / 1.055, 2.4),
        rgb_f / 12.92
    )
    return rgb_linear


def RGBtosRGB(rgb_linear):
    """linear RGB(0-1) -> sRGB(0-1)"""

    mask = rgb_linear > 0.0031308
    rgb_f = np.where(
        mask,
        1.055 * np.power(rgb_linear, 1.0 / 2.4) - 0.055,
        12.92 * rgb_linear
    )
    return rgb_f


def RGBtoXYZ(rgb_f):
    """RGB -> XYZ (D65標準光源)"""

    transform_matrix = np.array([
        [0.412391, 0.357584, 0.180481],
        [0.212639, 0.715169, 0.072192],
        [0.019331, 0.119195, 0.950532]
    ])
    xyz = np.dot(rgb_f, transform_matrix.T)
    return xyz


def XYZtoRGB(xyz):
    """XYZ -> RGB (D65標準光源)"""

    transform_matrix = np.array([
        [ 3.240970, -1.537383, -0.498611],
        [-0.969244,  1.875968,  0.041555],
        [ 0.055630, -0.203977,  1.056972]
    ])
    rgb_linear = np.dot(xyz, transform_matrix.T)
    return rgb_linear


def XYZtoLab(xyz):
    """XYZ -> Lab(L:0-100, a:-128~127, b:-128~127)"""

    # ホワイトポイントはD65光源とする
    ref_white = np.array([0.95047, 1.00000, 1.08883])
    xyz_normalized = xyz / ref_white
    
    # XYZ -> Lab (CIE標準)
    epsilon = (6.0 / 29.0) ** 3                 # ≈ 0.008856
    kappa = 1.0 / (3.0 * (6.0 / 29.0) ** 2.0)   # ≈ 7.787037
    
    mask_xyz = xyz_normalized > epsilon
    f = np.where(
        mask_xyz,
        np.power(xyz_normalized, 1.0 / 3.0),
        xyz_normalized * kappa + (16.0 / 116.0)
    )
    
    # Lab(L:0-100, a:-128~127, b:-128~127)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return L, a, b


def LabtoXYZ(L, a, b) -> np.ndarray:
    """Lab(L:0-100, a:-128~127, b:-128~127) -> XYZ"""

    # Lab -> XYZ
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    f = np.stack([fx, fy, fz], axis=-1)

    epsilon = (6.0 / 29.0)                      # ≈ 0.206897
    kappa = 1.0 / (3.0 * (6.0 / 29.0) ** 2.0)   # ≈ 7.787037
    mask_xyz = f > epsilon
    xyz_normalized = np.where(
        mask_xyz,
        np.power(f, 3.0),
        (f - 16.0 / 116.0) / kappa
    )

    # ホワイトポイントはD65光源とする
    ref_white = np.array([0.95047, 1.00000, 1.08883])
    xyz = xyz_normalized * ref_white
    return xyz


def cov_sqrt_and_inv(cov: np.ndarray, eps: float = 1e-6) -> tuple[np.ndarray, np.ndarray]:
    """共分散行列の平方根と逆平方根"""
    
    # 対称行列として扱う
    cov = cov.astype(np.float64)
    cov = cov + eps * np.eye(cov.shape[0])
    w, v = np.linalg.eigh(cov)
    
    # 数値的安定化
    w = np.clip(w, eps, None)
    sqrt_w = np.sqrt(w)
    
    sqrt = (v * sqrt_w) @ v.T
    inv_sqrt = (v * (1.0 / sqrt_w)) @ v.T
    return sqrt, inv_sqrt


def spd_mat_sqrt(A):
    """
    対称正定値(SPD)行列の平方根を固有値分解で求める

    A = V @ diag(λ) @ V.T
    A^{1/2} = V @ diag(√λ) @ V.T
    
    一般的には行列の平方根はscipy.linalg.sqrtm(A)で求めるが
    対称正定値行列の場合は固有値分解で求めた方が安定で高速
    """

    # 対称行列を V, diag(λ) に固有値分解
    # (eigh()は高速・安定だが対称行列専用)
    eigenvalues, V = np.linalg.eigh(A)

    # 数値誤差で負になるのを防ぐ
    eigenvalues = np.maximum(eigenvalues, 0)

    return V @ np.diag(np.sqrt(eigenvalues)) @ V.T


def spd_mat_sqrt_inv(A):
    """
    対称正定値(SPD)行列の逆平方根を固有値分解で求める

    A^{-1/2} = V @ diag(1/√λ) @ V.T

    一般的には行列の平方根はnp.linalg.inv(scipy.linalg.sqrtm(A))で求めるが
    対称正定値行列の場合は固有値分解で求めた方が安定で高速
    """

    # 対称行列を V, diag(λ) に固有値分解
    # (eigh()は高速・安定だが対称行列専用)
    eigenvalues, V = np.linalg.eigh(A)

    # 数値誤差で負になるのを防ぐ(0除算防止の為に eps を加える)
    eigenvalues = np.maximum(eigenvalues, 1e-10)

    return V @ np.diag(1.0 / np.sqrt(eigenvalues)) @ V.T
