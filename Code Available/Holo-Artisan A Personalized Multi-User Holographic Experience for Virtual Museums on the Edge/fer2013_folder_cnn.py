# =========================================
# fer2013_folder_cnn_improved_fixed.py
# =========================================
#!/usr/bin/env python3
"""
Enhanced FER‑2013 folder‑based CNN training script.
- Fixes the latencies list bug.
- Adds a few quality‑of‑life CLI flags.
- Keeps the lightweight architecture so it can run on a Jetson‑class device.
"""
import argparse
import os
import time
from typing import Tuple, List

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, Flatten, Dense, Dropout,
    BatchNormalization, Activation
)

# -----------------------------
#  Global settings
# -----------------------------
EMOTION_LABELS: List[str] = [
    "angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"
]

# -----------------------------
#  Model architecture
# -----------------------------

def build_robust_cnn(input_shape: Tuple[int, int, int] = (48, 48, 1)) -> tf.keras.Model:
    """Construct a slightly deeper yet still lightweight CNN."""
    model = Sequential()

    # Block 1
    model.add(Conv2D(32, (3, 3), padding="same", input_shape=input_shape))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(2, 2))
    model.add(Dropout(0.25))

    # Block 2
    model.add(Conv2D(64, (3, 3), padding="same"))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(2, 2))
    model.add(Dropout(0.25))

    # Block 3
    model.add(Conv2D(128, (3, 3), padding="same"))
    model.add(BatchNormalization())
    model.add(Activation("relu"))
    model.add(MaxPooling2D(2, 2))
    model.add(Dropout(0.25))

    # FC
    model.add(Flatten())
    model.add(Dense(256, activation="relu"))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(len(EMOTION_LABELS), activation="softmax"))

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

# -----------------------------
#  Main
# -----------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Improved FER‑2013 CNN trainer (image‑folder version)")
    parser.add_argument("--data_dir", default="./archive", type=str,
                        help="資料資料夾 (包含 train/ test 子資料夾)")
    parser.add_argument("--epochs", default=35, type=int)
    parser.add_argument("--batch", default=128, type=int)
    parser.add_argument("--model_out", default="trained_model.h5", type=str)
    parser.add_argument("--pdf_out", default="fer_confusion_matrix.pdf", type=str)
    args = parser.parse_args()

    train_dir = os.path.join(args.data_dir, "train")
    test_dir = os.path.join(args.data_dir, "test")
    if not os.path.isdir(train_dir):
        raise FileNotFoundError(f"Train directory not found: {train_dir}")
    if not os.path.isdir(test_dir):
        raise FileNotFoundError(f"Test directory not found: {test_dir}")

    # Data pipeline
    train_gen = ImageDataGenerator(
        rescale=1.0/255,
        horizontal_flip=True,
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        validation_split=0.1,
    )
    test_gen = ImageDataGenerator(rescale=1.0/255)

    train_flow = train_gen.flow_from_directory(
        train_dir, target_size=(48,48), color_mode="grayscale",
        batch_size=args.batch, class_mode="categorical", subset="training", shuffle=True,
    )
    val_flow = train_gen.flow_from_directory(
        train_dir, target_size=(48,48), color_mode="grayscale",
        batch_size=args.batch, class_mode="categorical", subset="validation", shuffle=False,
    )
    test_flow = test_gen.flow_from_directory(
        test_dir, target_size=(48,48), color_mode="grayscale",
        batch_size=args.batch, class_mode="categorical", shuffle=False,
    )

    # Training
    model = build_robust_cnn()
    model.summary()
    model.fit(train_flow, epochs=args.epochs, validation_data=val_flow)

    # Evaluation
    y_true = test_flow.classes
    y_prob = model.predict(test_flow, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)
    acc = accuracy_score(y_true, y_pred)
    print(f"\nFinal Test Accuracy: {acc:.4f}")

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=EMOTION_LABELS, yticklabels=EMOTION_LABELS)
    plt.title('FER‑2013 Confusion Matrix', fontsize=14)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(args.pdf_out)
    print(f"Confusion matrix saved to {args.pdf_out}")

    # Latency test (FIXED)
    sample_batch, _ = next(test_flow)
    sample_img = sample_batch[:1]
    _ = model.predict(sample_img, verbose=0)  # warm‑up
    latencies: List[float] = []   # <-- bug fixed (initialized list)
    for _ in range(200):
        t0 = time.perf_counter()
        _ = model.predict(sample_img, verbose=0)
        latencies.append((time.perf_counter() - t0) * 1000.0)
    print(f"Average single‑image inference latency: {np.mean(latencies):.2f} ms")

    model.save(args.model_out)
    print(f"Model saved to {args.model_out}")

if __name__ == "__main__":
    main()
