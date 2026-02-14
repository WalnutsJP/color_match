#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Color Matchのアプリケーション
"""

import sys
from pathlib import Path

# リポジトリ直下から実行した場合に color_match を import できるようにする
_src = Path(__file__).resolve().parent / "source"
if _src.exists() and str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

try:
    from PIL import Image, ImageTk
    import numpy as np
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from tkinterdnd2 import DND_FILES, TkinterDnD
    import color_match
except Exception as e:
    print("必要なライブラリが見つかりません")
    raise


class ColorMatchApp(TkinterDnD.Tk):
    """
    Color Matchのアプリケーションクラス
    """

    def __init__(self):
        super().__init__()
        self.title("Color Match")
        self.geometry("1000x400")

        self._padding = 2

        # color_match の method / mode 選択肢（__init__.py の match() に合わせる）
        self._methods = ("hm", "reinhard", "mvgd", "mkl", "hm-mvgd-hm", "hm-mkl-hm")
        self._modes = ("rgb", "lab")

        # 上部: Method / Mode / Strength 用フレーム
        self.top_frame = ttk.Frame(self, padding=4)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        # Method コンボボックス
        ttk.Label(self.top_frame, text="Method:").pack(side=tk.LEFT, padx=(0, 4))
        self.method_var = tk.StringVar(value="mkl")
        self.method_combo = ttk.Combobox(
            self.top_frame,
            textvariable=self.method_var,
            values=self._methods,
            state="readonly",
            width=14,
        )
        self.method_combo.pack(side=tk.LEFT, padx=(0, 16))
        self.method_var.trace_add("write", lambda *a: self._update_center_preview())

        # Mode コンボボックス
        ttk.Label(self.top_frame, text="Mode:").pack(side=tk.LEFT, padx=(0, 4))
        self.mode_var = tk.StringVar(value=self._modes[0])
        self.mode_combo = ttk.Combobox(
            self.top_frame,
            textvariable=self.mode_var,
            values=self._modes,
            state="readonly",
            width=6,
        )
        self.mode_combo.pack(side=tk.LEFT, padx=(0, 16))
        self.mode_var.trace_add("write", lambda *a: self._update_center_preview())

        # Sterength スライダー
        ttk.Label(self.top_frame, text="Strength:").pack(side=tk.LEFT, padx=(0, 4))
        self.strength_var = tk.DoubleVar(value=100.0)
        self.strength_scale = ttk.Scale(
            self.top_frame,
            from_=0.0,
            to=100.0,
            variable=self.strength_var,
            orient=tk.HORIZONTAL,
            length=120,
        )
        self.strength_scale.pack(side=tk.LEFT, padx=(0, 4))
        self.strength_var.trace_add("write", self._on_strength_changed)
        self.strength_entry = ttk.Entry(self.top_frame, width=5, justify=tk.RIGHT)
        self.strength_entry.pack(side=tk.LEFT, padx=(0, 4))
        self.strength_entry.insert(0, "100.0")
        self.strength_entry.bind("<Return>", lambda e: self._apply_strength_entry())
        self.strength_entry.bind("<FocusOut>", lambda e: self._apply_strength_entry())

        # プレビュー用フレーム（左・中央・右の画像エリア）
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        for col in (0, 1, 2):
            self.main_frame.columnconfigure(col, weight=1, uniform="panels")
        self.main_frame.rowconfigure(0, weight=1)

        # --- 左パネル ---
        self.left_frame = ttk.LabelFrame(self.main_frame, text="入力画像")
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.left_frame.columnconfigure(0, weight=1)
        self.left_frame.rowconfigure(0, weight=1)

        self.left_image_label = ttk.Label(
            self.left_frame,
            text="ここに画像をドラッグ＆ドロップ",
            anchor=tk.CENTER,
        )
        self.left_image_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.left_image_label.bind("<Button-3>", lambda e: self._on_preview_context_menu(e, "left"))

        self.left_image_label.drop_target_register(DND_FILES)
        self.left_image_label.dnd_bind("<<Drop>>", lambda e: self._on_drop(e, "left"))

        self.left_original_image = None
        self.left_image_path = None  # ドロップした画像のパス（保存ダイアログの初期フォルダ用）
        self.left_tkimage = None
        self._left_resize_job = None
        self._left_hq_job = None
        self._left_last_size = (0, 0)

        # --- 中央パネル: Color Match 結果プレビュー ---
        self.center_frame = ttk.LabelFrame(self.main_frame, text="結果画像")
        self.center_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        self.center_frame.columnconfigure(0, weight=1)
        self.center_frame.rowconfigure(0, weight=1)

        self.center_image_label = ttk.Label(
            self.center_frame,
            text="結果を表示",
            anchor=tk.CENTER,
        )
        self.center_image_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.center_image_label.bind("<Button-3>", self._on_center_context_menu)

        self.center_original_image = None  # PIL Image (RGB)
        self.center_tkimage = None
        self._center_resize_job = None
        self._center_hq_job = None
        self._center_last_size = (0, 0)

        self._matched_image_cache = {}  # カラーマッチング結果のキャッシュ (method, mode) -> ndarray

        # --- 右パネル ---
        self.right_frame = ttk.LabelFrame(self.main_frame, text="参照画像")
        self.right_frame.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        self.right_image_label = ttk.Label(
            self.right_frame,
            text="ここに画像をドラッグ＆ドロップ",
            anchor=tk.CENTER,
        )
        self.right_image_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.right_image_label.bind("<Button-3>", lambda e: self._on_preview_context_menu(e, "right"))

        self.right_image_label.drop_target_register(DND_FILES)
        self.right_image_label.dnd_bind("<<Drop>>", lambda e: self._on_drop(e, "right"))

        self.right_original_image = None
        self.right_image_path = None  # ドロップした画像のパス（保存ダイアログの初期フォルダ用）
        self.right_tkimage = None
        self._right_resize_job = None
        self._right_hq_job = None
        self._right_last_size = (0, 0)

        # ウィンドウリサイズ時のイベントをバインド
        self.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        """ウィンドウリサイズ時のイベントハンドラ"""
        # 左・中央・右の画像サイズを更新
        self._schedule_resize_updates("left")
        self._schedule_resize_updates("center")
        self._schedule_resize_updates("right")

    def _on_strength_changed(self, *args):
        """Strength 数値入力ボックスの値更新時のコールバック"""
        try:
            # 数値入力ボックスの値を取得
            v = self.strength_var.get()
            # 数値入力ボックスの値を Strength スライダーに反映
            self.strength_entry.delete(0, tk.END)
            self.strength_entry.insert(0, f"{v:.1f}")
        except (tk.TclError, ValueError):
            pass
        # プレビューを更新
        self._update_center_preview(True)

    def _apply_strength_entry(self):
        """Strength スライダーの値更新時のコールバック"""
        try:
            s = self.strength_entry.get().strip()
            v = float(s) if s else 100.0
            v = max(0.0, min(100.0, v))
            self.strength_var.set(v)
        except ValueError:
            try:
                v = self.strength_var.get()
                self.strength_entry.delete(0, tk.END)
                self.strength_entry.insert(0, f"{v:.1f}")
            except (tk.TclError, ValueError):
                pass

    def _on_drop(self, event, side: str):
        """
        ファイルドラッグアンドドロップ時のコールバック
        
        引数:
            side: 対象がどちらか(left / right)
        """
        # ドロップされたファイルのパスを取得
        data = event.data
        # 複数ファイルがドロップされた場合を考慮してパスを分割
        if data.startswith("{"):
            # ドロップされたファイルパスがスペースを含む場合、パスが {} で囲まれる為、{} を取り除く
            data = data[1:]
            path_parts = data.split("}")
        else:
            # 複数ファイルがドロップされた場合、スペース区切りで複数のパスが渡される
            path_parts = data.split()
        if not path_parts:
            return
        # 指定パスの画像を読み込み、プレビューを更新
        self._load_image_for_side(path_parts[0], side)

    def _on_preview_context_menu(self, event, side: str):
        """左右プレビューを右クリック時のコールバック"""
        # コンテキストメニューを表示
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="ファイルを開く", command=lambda: self._open_file_for_side(side))
        menu.add_command(label="画像を入替", command=self._swap_left_right_images)
        menu.tk_popup(event.x_root, event.y_root)

    def _on_center_context_menu(self, event):
        """中央プレビューを右クリック時のコールバック"""
        # コンテキストメニューを表示
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="画像を保存", command=self._save_center_image)
        menu.tk_popup(event.x_root, event.y_root)

    def _open_file_for_side(self, side: str):
        """
        ファイルを開くダイアログを表示し、選択した画像でプレビューを更新
        
        引数:
            side: 対象がどちらか(left / right)
        """
        # ファイルダイアログ起動時の初期ディレクトリを設定(最後に開いた画像のディレクトリを優先)
        initialdir = None
        if side == "left" and self.left_image_path:
            initialdir = str(Path(self.left_image_path).parent)
        elif side == "right" and self.right_image_path:
            initialdir = str(Path(self.right_image_path).parent)
        elif self.left_image_path:
            initialdir = str(Path(self.left_image_path).parent)
        elif self.right_image_path:
            initialdir = str(Path(self.right_image_path).parent)
        # ファイルダイアログを開いて画像ファイルを選択
        path = filedialog.askopenfilename(
            title="画像を開く",
            initialdir=initialdir,
            filetypes=[
                ("画像", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.webp;*.tif;*.tiff"),
                ("すべて", "*"),
            ],
        )
        if path:
            # 指定パスの画像を読み込み、プレビューを更新
            self._load_image_for_side(path, side)

    def _load_image_for_side(self, path: str, side: str):
        """
        指定パスの画像を読み込み、プレビューを更新
        
        引数:
            path: 画像ファイルのパス
            side: 対象がどちらか(left / right)
        """
        path = path.replace("\\", "/")
        # 画像ファイルでない場合は無視
        is_image_file = Path(path).suffix.lower() in (
            ".png",
            ".jpg",
            ".jpeg",
            ".bmp",
            ".gif",
            ".webp",
            ".tif",
            ".tiff",
        )
        if not is_image_file:
            return
        # 画像を読み込み
        try:
            img = Image.open(path)
        except Exception:
            return
        img_rgba = img.convert("RGBA")
        if side == "left":
            self.left_original_image = img_rgba
            self.left_image_path = path
            self._left_last_size = (0, 0)
        else:
            self.right_original_image = img_rgba
            self.right_image_path = path
            self._right_last_size = (0, 0)
        # プレビューを更新
        self._update_image(side)
        self._schedule_resize_updates(side)
        self._update_center_preview()

    def _swap_left_right_images(self):
        """左右のプレビュー画像を入れ替え"""

        # 画像とパスを入れ替え
        self.left_original_image, self.right_original_image = (
            self.right_original_image,
            self.left_original_image,
        )
        self.left_image_path, self.right_image_path = (
            self.right_image_path,
            self.left_image_path,
        )
        self._left_last_size = (0, 0)
        self._right_last_size = (0, 0)
        self.update_idletasks()  # レイアウト確定後に幅・高さを取得するため
        # プレビューを更新
        self._update_image("left")
        self._update_image("right")
        self._schedule_resize_updates("left")
        self._schedule_resize_updates("right")
        self._update_center_preview()

    def _save_center_image(self):
        """適応画像をファイルに保存"""
        if self.center_original_image is None:
            messagebox.showinfo("保存", "保存する画像がありません。")
            return
        # ファイルダイアログ起動時の初期ディレクトリを設定(最後に開いた画像のディレクトリを優先)
        initialdir = None
        if self.left_image_path:
            initialdir = str(Path(self.left_image_path).parent)
        elif self.right_image_path:
            initialdir = str(Path(self.right_image_path).parent)
        # ファイルダイアログを開いて画像ファイルを選択
        path = filedialog.asksaveasfilename(
            initialdir=initialdir,
            initialfile="output.png",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("すべて", "*")],
        )
        if not path:
            return
        # 画像を保存
        try:
            self.center_original_image.save(path)
        except Exception as e:
            messagebox.showerror("エラー", str(e))
    
    def _update_image(self, side: str, low_quality: bool = False):
        """指定側のラベルに現在の元画像をリサイズして表示"""
        if side == "left":
            original = self.left_original_image
            label = self.left_image_label
            tkimage_attr = "left_tkimage"
        elif side == "center":
            original = self.center_original_image
            label = self.center_image_label
            tkimage_attr = "center_tkimage"
        else:
            original = self.right_original_image
            label = self.right_image_label
            tkimage_attr = "right_tkimage"

        if original is None:
            if side in ("left", "right"):
                setattr(self, tkimage_attr, None)
                label.config(image="", text="ここに画像をドラッグ＆ドロップ")
            return
        w, h = label.winfo_width(), label.winfo_height()
        if w <= 1 or h <= 1:
            return

        resample = Image.NEAREST if low_quality else Image.LANCZOS
        try:
            img = original.copy()
            img.thumbnail((w, h), resample)
            photo = ImageTk.PhotoImage(img)
            setattr(self, tkimage_attr, photo)
            label.config(image=photo, text="")
        finally:
            if side == "left":
                if low_quality:
                    self._left_resize_job = None
                else:
                    self._left_hq_job = None
            elif side == "center":
                if low_quality:
                    self._center_resize_job = None
                else:
                    self._center_hq_job = None
            else:
                if low_quality:
                    self._right_resize_job = None
                else:
                    self._right_hq_job = None

    def _update_center_preview(self, use_cached_image: bool = False):
        """中央プレビューを更新"""
        self.center_original_image = None
        self.center_image_label.config(image="", text="結果を表示")

        if self.left_original_image is None or self.right_original_image is None:
            return

        try:
            src_rgb = self.left_original_image.convert("RGB")
            ref_rgb = self.right_original_image.convert("RGB")
            src_arr = np.array(src_rgb)
            ref_arr = np.array(ref_rgb)
            method = self.method_var.get()
            mode = self.mode_var.get()
            # カラーマッチング
            if use_cached_image:
                matched = self._matched_image_cache
            else:
                matched = color_match.match(src_arr, ref_arr, method, mode)
                self._matched_image_cache = matched
            # Strength値に応じて元画像とマッチング結果をブレンド
            strength = self.strength_var.get() / 100.0
            blended = (1.0 - strength) * src_arr.astype(np.float64) + strength * matched.astype(np.float64)
            blended_uint8 = np.clip(blended, 0, 255).astype(np.uint8)
            # プレビュー画像を更新
            self.center_original_image = Image.fromarray(blended_uint8)
            self._center_last_size = (0, 0)
            self._update_image("center")
            self._schedule_resize_updates("center")
        except Exception as e:
            self.center_image_label.config(text=f"エラー: {e}")

    def _schedule_resize_updates(self, side: str):
        """プレビュー画像の表示サイズ更新をスケジュール"""
        if side == "left":
            label = self.left_image_label
            last_size = self._left_last_size
        elif side == "center":
            label = self.center_image_label
            last_size = self._center_last_size
        else:
            label = self.right_image_label
            last_size = self._right_last_size

        w, h = label.winfo_width(), label.winfo_height()
        size = (w, h)
        if size == last_size:
            return

        if side == "left":
            self._left_last_size = size
            if self._left_resize_job is not None:
                try:
                    self.after_cancel(self._left_resize_job)
                except Exception:
                    pass
                self._left_resize_job = None
            if self._left_hq_job is not None:
                try:
                    self.after_cancel(self._left_hq_job)
                except Exception:
                    pass
                self._left_hq_job = None
            self._left_resize_job = self.after(
                30, lambda: self._update_image("left", low_quality=True)
            )
            self._left_hq_job = self.after(
                300, lambda: self._update_image("left", low_quality=False)
            )
        elif side == "center":
            self._center_last_size = size
            if self._center_resize_job is not None:
                try:
                    self.after_cancel(self._center_resize_job)
                except Exception:
                    pass
                self._center_resize_job = None
            if self._center_hq_job is not None:
                try:
                    self.after_cancel(self._center_hq_job)
                except Exception:
                    pass
                self._center_hq_job = None
            self._center_resize_job = self.after(
                30, lambda: self._update_image("center", low_quality=True)
            )
            self._center_hq_job = self.after(
                300, lambda: self._update_image("center", low_quality=False)
            )
        else:
            self._right_last_size = size
            if self._right_resize_job is not None:
                try:
                    self.after_cancel(self._right_resize_job)
                except Exception:
                    pass
                self._right_resize_job = None
            if self._right_hq_job is not None:
                try:
                    self.after_cancel(self._right_hq_job)
                except Exception:
                    pass
                self._right_hq_job = None
            self._right_resize_job = self.after(
                30, lambda: self._update_image("right", low_quality=True)
            )
            self._right_hq_job = self.after(
                300, lambda: self._update_image("right", low_quality=False)
            )


def main():
    app = ColorMatchApp()
    app.mainloop()


if __name__ == "__main__":
    main()
