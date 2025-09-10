import torch
import torch.nn as nn

class SimpleGNN(nn.Module):
    """Tiny message-passing with two layers; adjacency A assumed dense tensor."""
    def __init__(self, in_dim=3, hid=64):
        super().__init__()
        self.w1 = nn.Linear(in_dim, hid)
        self.w2 = nn.Linear(hid, 1)  # allocation logit
        self.act = nn.ReLU()

    def forward(self, A, X):
        # A: (N,N), X: (N,F)
        H = self.act(A @ self.w1(X))
        out = torch.sigmoid(A @ self.w2(H))  # (N,1)
        return out  # allocation prob per node
