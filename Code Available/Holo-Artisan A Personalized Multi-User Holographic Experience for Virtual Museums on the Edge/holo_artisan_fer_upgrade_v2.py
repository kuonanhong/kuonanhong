"""
Holo‑Artisan · FER‑2013 Pipeline Upgrade (v1.1 – class‑weight bug fix)
====================================================================
*Change log (2025‑07‑28)*
• 修正 `_make_dataflows()` 在計算 `class_weights` 時將 one‑hot 向量展平成 1‑D
  造成 `counts` 變成 scalar → `TypeError: numpy.float32 object is not iterable`。
• 以 `np.vstack` 保留 `(N,7)` 形狀後 `sum(axis=0)` 取得每類樣本數。
• 另外加上 `--no_gpu` 旗標，可強制使用 CPU 以避免 macOS On‑chip GPU 相容性問題。

原始 CLI 與功能維持完全相容。
"""

# ────────────────────────────────────────────────────────────────────────────────
# Standard library
# ────────────────────────────────────────────────────────────────────────────────
import argparse, os, sys, shutil, tempfile, math, itertools, textwrap
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# ────────────────────────────────────────────────────────────────────────────────
# Third‑party
# ────────────────────────────────────────────────────────────────────────────────
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2

# ────────────────────────────────────────────────────────────────────────────────
# Globals & metadata
# ────────────────────────────────────────────────────────────────────────────────
EMOTIONS: List[str] = [
    "angry", "disgust", "fear", "happy", "sad", "surprise", "neutral",
]
DEFAULT_IMG_SIZE = 224
MONA_FILES: Dict[str, str] = {e: f"mona_{e}.png" for e in EMOTIONS}

# ----------------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------------

def _verbose(msg: str):
    print(f"[▶] {msg}")


def _make_dataflows(data_root: Path,
                    img_size: int = DEFAULT_IMG_SIZE,
                    batch: int = 32,
                    val_split: float = 0.1,
                    enable_class_weights: bool = True):
    """Return train/val/test datasets + per‑class weights (or None)."""
    from tensorflow.keras.preprocessing import image_dataset_from_directory

    train_dir, test_dir = data_root / "train", data_root / "test"
    if not train_dir.is_dir() or not test_dir.is_dir():
        raise FileNotFoundError("Expect FER‑2013 split into train/ test sub‑folders.")

    common = dict(image_size=(img_size, img_size), color_mode="grayscale",
                  seed=123, label_mode="categorical")

    train_ds = image_dataset_from_directory(train_dir, validation_split=val_split,
                                            subset="training", batch_size=batch,
                                            shuffle=True, **common)
    val_ds   = image_dataset_from_directory(train_dir, validation_split=val_split,
                                            subset="validation", batch_size=batch,
                                            shuffle=True, **common)
    test_ds  = image_dataset_from_directory(test_dir, batch_size=batch,
                                            shuffle=False, **common)

    # Compute inverse‑frequency weights
    if enable_class_weights:
        y_train = np.vstack([y.numpy() for _, y in train_ds.unbatch()])  # (N,7)
        counts  = y_train.sum(axis=0)                                   # (7,)
        weights = {i: float(counts.max() / counts[i]) for i in range(len(counts))}
    else:
        weights = None

    # Augmentation pipeline
    aug = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.1),
        tf.keras.layers.RandomTranslation(0.1, 0.1),
        tf.keras.layers.RandomZoom(0.1),
    ], name="augment")

    def _aug(x, y):
        return aug(x, training=True), y

    train_ds = train_ds.map(_aug, num_parallel_calls=tf.data.AUTOTUNE)
    return train_ds.prefetch(tf.data.AUTOTUNE), val_ds.prefetch(tf.data.AUTOTUNE), test_ds, weights

# ----------------------------------------------------------------------------
# Model factory
# ----------------------------------------------------------------------------

def build_classifier(backbone: str = "efficientnetb0", img_size: int = DEFAULT_IMG_SIZE,
                     freeze_layers: int = 100):
    inputs = tf.keras.Input(shape=(img_size, img_size, 1))
    x = tf.keras.layers.Concatenate()([inputs, inputs, inputs])  # 1‑>3ch

    if backbone.startswith("efficientnet"):
        base = tf.keras.applications.EfficientNetB0(include_top=False, weights="imagenet",
                                                   input_tensor=x, pooling="avg")
    elif backbone == "resnet50":
        base = tf.keras.applications.ResNet50(include_top=False, weights="imagenet",
                                             input_tensor=x, pooling="avg")
    else:
        raise ValueError("Unsupported backbone")

    for layer in base.layers[:freeze_layers]:
        layer.trainable = False

    y = tf.keras.layers.Dense(256, activation="relu")(base.output)
    y = tf.keras.layers.Dropout(0.4)(y)
    outputs = tf.keras.layers.Dense(len(EMOTIONS), activation="softmax")(y)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                  loss="categorical_crossentropy", metrics=["accuracy"])
    return model

# ----------------------------------------------------------------------------
# Training command
# ----------------------------------------------------------------------------

def cli_train(args):
    if args.no_gpu:
        tf.config.set_visible_devices([], "GPU")
        _verbose("GPU disabled – forcing CPU execution.")

    train_ds, val_ds, test_ds, weights = _make_dataflows(Path(args.data_dir),
                                                         args.img_size, args.batch,
                                                         args.val_split,
                                                         not args.no_class_weights)
    model = build_classifier(args.backbone, args.img_size, args.freeze_layers)
    _verbose(model.summary())

    cbs = [tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True),
           tf.keras.callbacks.ReduceLROnPlateau(patience=4, factor=0.3),
           tf.keras.callbacks.ModelCheckpoint(args.model_out, save_best_only=True)]

    model.fit(train_ds, epochs=args.epochs, validation_data=val_ds,
              class_weight=weights, callbacks=cbs)

    loss, acc = model.evaluate(test_ds, verbose=0)
    print(f"\n[✓] Test accuracy: {acc*100:.2f}% (loss={loss:.4f})")

    if args.pdf_out:
        y_true = np.vstack([y.numpy() for _, y in test_ds]).argmax(1)
        y_pred = model.predict(test_ds, verbose=0).argmax(1)
        cm = tf.math.confusion_matrix(y_true, y_pred, num_classes=len(EMOTIONS)).numpy()
        import seaborn as sns
        plt.figure(figsize=(8,6))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                    xticklabels=EMOTIONS, yticklabels=EMOTIONS)
        plt.title("FER‑2013 Confusion Matrix (v1.1)")
        plt.ylabel("True")
        plt.xlabel("Pred")
        plt.tight_layout()
        plt.savefig(args.pdf_out)
        _verbose(f"Saved confusion matrix → {args.pdf_out}")

# ----------------------------------------------------------------------------
# Mona‑Lisa rendering command (unchanged)
# ----------------------------------------------------------------------------

def _sample_faces_by_label(data_dir: Path, emotions: List[str], img_size: int = 48):
    samples = {}
    for emo in emotions:
        folder = data_dir / "test" / emo
        files  = [f for f in folder.iterdir() if f.suffix.lower() in {'.png','.jpg','.jpeg'}]
        if files:
            img = cv2.imread(str(files[0]), cv2.IMREAD_GRAYSCALE)
            if img.shape != (img_size, img_size):
                img = cv2.resize(img, (img_size, img_size))
            samples[emo] = img
    return samples


def cli_render(args):
    faces = _sample_faces_by_label(Path(args.data_dir), EMOTIONS)
    rows, cols = 3, 3
    fig, axes = plt.subplots(rows, cols, figsize=(12,12))
    fig.suptitle("Label‑Driven Mona‑Lisa Grid", fontsize=18)

    idx = 0
    for r in range(rows):
        for c in range(cols):
            ax = axes[r,c]
            if idx < len(EMOTIONS):
                emo = EMOTIONS[idx]
                face = faces.get(emo, np.zeros((48,48)))
                mona_path = MONA_FILES.get(emo)
                if Path(mona_path).exists():
                    mona = cv2.cvtColor(cv2.imread(mona_path), cv2.COLOR_BGR2RGB)
                else:
                    mona = np.full((200,150,3),(35,0,40),dtype=np.uint8)
                    cv2.putText(mona, emo,(5,100),cv2.FONT_HERSHEY_SIMPLEX,1,(200,50,200),2)
                combo = np.hstack([cv2.cvtColor(cv2.resize(face,(mona.shape[0],mona.shape[0])),cv2.COLOR_GRAY2RGB), mona])
                ax.imshow(combo)
                ax.set_title(emo)
            ax.axis('off')
            idx += 1
    plt.tight_layout(rect=[0,0,1,0.95])
    plt.savefig(args.out_pdf)
    print(f"[✓] Saved {args.out_pdf}")
    if not args.no_show:
        plt.show()

# ----------------------------------------------------------------------------
# CLI front‑end
# ----------------------------------------------------------------------------

def build_cli():
    p = argparse.ArgumentParser("Holo‑Artisan FER‑2013 Toolkit v1.1")
    sub = p.add_subparsers(dest="cmd", required=True)

    tr = sub.add_parser("train", help="Train FER‑2013 classifier")
    tr.add_argument("--data_dir", default="./archive")
    tr.add_argument("--epochs", type=int, default=50)
    tr.add_argument("--batch", type=int, default=64)
    tr.add_argument("--val_split", type=float, default=0.1)
    tr.add_argument("--img_size", type=int, default=DEFAULT_IMG_SIZE)
    tr.add_argument("--backbone", choices=["efficientnetb0","resnet50"], default="efficientnetb0")
    tr.add_argument("--freeze_layers", type=int, default=100)
    tr.add_argument("--model_out", default="fer_best.h5")
    tr.add_argument("--pdf_out", default="fer_confusion_matrix_v2.pdf")
    tr.add_argument("--no_class_weights", action="store_true")
    tr.add_argument("--no_gpu", action="store_true")
    tr.set_defaults(func=cli_train)

    rd = sub.add_parser("render", help="Generate Mona‑Lisa response grid")
    rd.add_argument("--data_dir", default="./archive")
    rd.add_argument("--out_pdf", default="generative_response_v3.pdf")
    rd.add_argument("--no_show", action="store_true")
    rd.set_defaults(func=cli_render)
    return p

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    ns = build_cli().parse_args()
    ns.func(ns)

"""
# 重新拉取最新版本 (若已在同目錄直接覆蓋即可)
# 接著執行：
python holo_artisan_fer_upgrade_v2.py train \
       --data_dir ./archive \
       --epochs 50 \
       --backbone efficientnetb0
"""