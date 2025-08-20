# ────────────────────────────────────────────────────────────────────────────────
# 3_make_grid.py  ——  3×3 方格，不重疊 (修正 NameError)
# ────────────────────────────────────────────────────────────────────────────────
"""
python 3_make_grid.py --assets ./assets --out_pdf monalisa_grid2.pdf
"""
import matplotlib.pyplot as plt, cv2, numpy as np, argparse, os
from pathlib import Path
import os

EMOTIONS = ["angry","disgust","fear","happy","sad","surprise","neutral"]


def make_grid(asset_dir: Path, out_pdf: str):
    faces = sorted(asset_dir.glob("face_*.jp*g"))
    if len(faces) != 9:
        raise RuntimeError("需先完成 9 張人臉 (步驟①②)")
    faces.sort(key=lambda p: (EMOTIONS.index(p.stem.split("_")[1]), p.name))

    fig, axes = plt.subplots(3,3, figsize=(12,12)); fig.suptitle("Mona‑Lisa Response Grid", fontsize=18)
    for idx, face_path in enumerate(faces):
        r,c = divmod(idx,3); ax = axes[r,c]
        face = cv2.cvtColor(cv2.imread(str(face_path), cv2.IMREAD_GRAYSCALE), cv2.COLOR_GRAY2RGB)
        mona = cv2.cvtColor(cv2.imread(str(asset_dir/f"mona_{face_path.stem}.png")), cv2.COLOR_BGR2RGB)
        combo = np.hstack([cv2.resize(face,(200,200)), cv2.resize(mona,(200,200))])
        ax.imshow(combo); ax.set_title(face_path.stem.replace("face_","")); ax.axis('off')
    plt.tight_layout(rect=[0,0,1,0.95]); plt.savefig(out_pdf); print("[✓] Saved →", out_pdf)

if __name__ == "__main__" and os.path.basename(__file__) == "3_make_grid.py":
    ap = argparse.ArgumentParser(); ap.add_argument("--assets", default="./assets"); ap.add_argument("--out_pdf", default="monalisa_grid2.pdf"); mk = ap.parse_args(); make_grid(Path(mk.assets), mk.out_pdf)

