# =========================================
# generative_response_simulation_fixed_v2.py
# =========================================
#!/usr/bin/env python3
"""
Simulate the edge‑AI → artwork response loop using the trained FER model and a
folder‑based FER‑2013 dataset. Generates a 3‑column PDF for a handful of target
emotions.

‑ Fixes list/str bug in `os.path.join`.
‑ Adds graceful fallbacks and automatic resizing to 48×48.
"""
import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from typing import Dict, List

MODEL_FILE = "trained_model.h5"  # produced by the training script
DATA_DIR = "./archive"            # folder with train/ test subfolders
EMOTION_LABELS: List[str] = [
    "angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"
]
TARGET_EMOTIONS: List[str] = ["happy", "sad", "surprise", "neutral"]

# -----------------------------------------
# Helpers
# -----------------------------------------

def load_and_find_emotion_samples(data_dir: str, target_emotions: List[str]) -> Dict[str, np.ndarray]:
    """Return one 48×48 grayscale face image per requested emotion."""
    samples: Dict[str,np.ndarray] = {}
    for emo in target_emotions:
        folder = os.path.join(data_dir, "test", emo)
        if not os.path.isdir(folder):
            print(f"[WARN] Folder not found for emotion '{emo}': {folder}")
            continue
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith((".png",".jpg",".jpeg"))])
        if not files:
            print(f"[WARN] No images for emotion '{emo}'")
            continue
        img_path = os.path.join(folder, files[0])  # pick the first image
        face = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if face is None:
            print(f"[WARN] Failed to read image {img_path}")
            continue
        if face.shape != (48,48):
            face = cv2.resize(face, (48,48))
        samples[emo] = face
    return samples

def load_mona_lisa_responses() -> Dict[str, np.ndarray]:
    responses: Dict[str,np.ndarray] = {}
    for emo in TARGET_EMOTIONS:
        path = f"mona_{emo.lower()}.png"
        if os.path.exists(path):
            responses[emo] = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        else:
            # simple placeholder (purple rect w/ text)
            placeholder = np.zeros((200,150,3), dtype=np.uint8)
            cv2.putText(placeholder, emo, (5,100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (180,50,180), 2, cv2.LINE_AA)
            responses[emo] = placeholder
    return responses

# -----------------------------------------
# Main
# -----------------------------------------

def main() -> None:
    if not os.path.exists(MODEL_FILE):
        raise FileNotFoundError(f"Model file '{MODEL_FILE}' not found – run the training script first.")

    model = tf.keras.models.load_model(MODEL_FILE)
    faces = load_and_find_emotion_samples(DATA_DIR, TARGET_EMOTIONS)
    responses = load_mona_lisa_responses()

    if len(faces) < len(TARGET_EMOTIONS):
        raise RuntimeError("Could not load all requested emotion samples. Check dataset paths.")

    n = len(TARGET_EMOTIONS)
    fig, axes = plt.subplots(n, 3, figsize=(9, 3*n))
    fig.suptitle("Generative Response Simulation", fontsize=16)

    for i, emo in enumerate(TARGET_EMOTIONS):
        # Column 1 – input
        axes[i,0].imshow(faces[emo], cmap='gray')
        axes[i,0].set_title(f"User Input: {emo}")
        axes[i,0].axis('off')

        # Column 2 – edge AI prediction
        face_norm = faces[emo] / 255.0
        face_norm = np.expand_dims(np.expand_dims(face_norm, -1), 0)  # shape (1,48,48,1)
        pred = model.predict(face_norm, verbose=0)
        pred_emo = EMOTION_LABELS[int(np.argmax(pred))]
        axes[i,1].text(0.5,0.5,f"Predicted\n'{pred_emo}'", ha='center', va='center', fontsize=12)
        axes[i,1].axis('off')

        # Column 3 – Mona Lisa response
        img_resp = responses.get(pred_emo, responses['neutral'])
        axes[i,2].imshow(img_resp)
        axes[i,2].set_title(f"Artwork → {pred_emo}")
        axes[i,2].axis('off')

    plt.tight_layout(rect=[0,0,1,0.96])
    plt.savefig('generative_response.pdf', bbox_inches='tight')
    print("Saved 'generative_response.pdf'")
    plt.show()

if __name__ == "__main__":
    main()