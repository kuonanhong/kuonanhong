#!/usr/bin/env python3
"""Federated Learning vs. Centralized Baseline on FER‑2013 (fixed)

Highlights
----------
* 修正 Matplotlib format string 中非 ASCII 連字符 (u+2011 或 u+2013) 導致的 ValueError。
* 允許找不到 `fer2013.csv` 時自動 fallback 到 Dummy 資料，方便純示範。
* 代碼與原版保持一致，僅進行必要小幅調整以確保可執行。
"""
import random, os, math
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
import pandas as pd
import numpy as np
from torchvision.transforms import ToTensor, Normalize, Compose
import matplotlib.pyplot as plt

# ───── 1. 資料集與模型 ─────
class FER2013CSV(Dataset):
    def __init__(self, csv_file: str, transform=None):
        df = pd.read_csv(csv_file)
        # 將像素字串轉成 48×48 ndarray
        self.images = np.stack(df['pixels'].apply(lambda x: np.fromstring(x, sep=' ').astype('float32').reshape(48, 48)))
        self.labels = df['emotion'].astype('int64').values
        self.transform = transform if transform is not None else ToTensor()

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        img = self.images[idx]
        if self.transform is not None:
            img = self.transform(img)  # (1, 48, 48)
        # 重複成 3 channel
        img = img.repeat(3, 1, 1)
        return img, self.labels[idx]

class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(),
            nn.Linear(32 * 12 * 12, 128), nn.ReLU(),
            nn.Linear(128, 7),
        )

    def forward(self, x):
        return self.net(x)

# ───── 2. 參數設定 ─────
NUM_CLIENTS = 10
COMM_ROUNDS = 20
LOCAL_EPOCHS = 3
BATCH_SIZE = 32
LR = 1e-3

# ───── 3. 資料載入 ─────
try:
    full_ds = FER2013CSV(
        'fer2013.csv',
        transform=Compose([
            ToTensor(),
            Normalize((0.5,), (0.5,)),  # 原圖為單通道，後續再 repeat
        ]),
    )
except FileNotFoundError:
    class Dummy(Dataset):
        def __len__(self):
            return 1000

        def __getitem__(self, idx):
            return torch.randn(3, 48, 48), random.randint(0, 6)

    full_ds = Dummy()
    print('[WARN] 使用 Dummy 資料集 (僅示範)')

train_len = int(0.8 * len(full_ds))
train_ds, test_ds = random_split(full_ds, [train_len, len(full_ds) - train_len])

test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

# IID 切分
chunk = train_len // NUM_CLIENTS
lengths = [chunk] * NUM_CLIENTS
lengths[-1] += train_len - chunk * NUM_CLIENTS  # 確保總和一致
client_datasets = random_split(train_ds, lengths)
client_loaders = [DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True) for ds in client_datasets]

# ───── 4. 輔助函式 ─────
@torch.no_grad()
def test(model: nn.Module):
    model.eval()
    correct = 0
    for x, y in test_loader:
        pred = model(x).argmax(1)
        correct += (pred == y).sum().item()
    return 100 * correct / len(test_loader.dataset)

def train_one(model: nn.Module, loader: DataLoader):
    opt = optim.Adam(model.parameters(), lr=LR)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    for _ in range(LOCAL_EPOCHS):
        for x, y in loader:
            opt.zero_grad()
            loss_fn(model(x), y).backward()
            opt.step()

# ───── 5. 聯邦學習模擬 ─────
global_model = SimpleCNN()
fl_accuracy = []

for r in range(COMM_ROUNDS):
    local_weights = []
    for loader in client_loaders:
        local_model = SimpleCNN()
        local_model.load_state_dict(global_model.state_dict())  # 初始化
        train_one(local_model, loader)
        local_weights.append(local_model.state_dict())

    # FedAvg — 權重平均
    avg_state = {
        k: torch.stack([w[k] for w in local_weights]).mean(0)
        for k in global_model.state_dict().keys()
    }
    global_model.load_state_dict(avg_state)
    acc = test(global_model)
    fl_accuracy.append(acc)
    print(f'Round {r + 1}/{COMM_ROUNDS} → Acc {acc:.2f}%')

# ───── 6. 集中式基線 ─────
central_model = SimpleCNN()
optimizer = optim.Adam(central_model.parameters(), lr=LR)
loss_fn = nn.CrossEntropyLoss()
centralized_accuracy = []
cent_epochs = COMM_ROUNDS * LOCAL_EPOCHS
full_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)

for ep in range(cent_epochs):
    central_model.train()
    for x, y in full_loader:
        optimizer.zero_grad()
        loss_fn(central_model(x), y).backward()
        optimizer.step()
    centralized_accuracy.append(test(central_model))

# ───── 7. 繪圖 ─────
plt.figure(figsize=(8, 5))
plt.plot(range(1, COMM_ROUNDS + 1), fl_accuracy, 'o-', label='FedAvg', color='#5cb85c')  # 使用 ASCII '-'
plt.axhline(centralized_accuracy[-1], color='#d9534f', ls='--', label=f'Centralized (Final {centralized_accuracy[-1]:.1f}%)')
plt.xlabel('Communication Round')
plt.ylabel('Accuracy (%)')
plt.title('FL vs. Centralized — FER‑2013')
plt.legend()
plt.grid(True, ls='--', alpha=0.5)
plt.tight_layout()
plt.savefig('fl_convergence.pdf')
print("Saved 'fl_convergence.pdf'")
plt.show()
