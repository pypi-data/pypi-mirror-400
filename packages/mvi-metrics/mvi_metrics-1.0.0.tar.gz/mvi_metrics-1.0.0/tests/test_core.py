import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from mvi import score, rank_batches, rank_samples



class TinyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(10, 16), nn.ReLU(), nn.Linear(16, 3))

    def forward(self, x):
        return self.net(x)


def test_score_runs_and_in_range():
    torch.manual_seed(0)
    model = TinyNet()
    x = torch.randn(64, 10)
    y = torch.randint(0, 3, (64,))
    dl = DataLoader(TensorDataset(x, y), batch_size=16, shuffle=False)

    res = score(model, dl, nn.CrossEntropyLoss(), max_batches=3)
    assert 0.0 <= res.score <= 1.0
    assert len(res.per_batch) == 3
    assert res.n_samples == 48


def test_rank_batches_returns_k():
    torch.manual_seed(1)
    model = TinyNet()
    x = torch.randn(80, 10)
    y = torch.randint(0, 3, (80,))
    dl = DataLoader(TensorDataset(x, y), batch_size=20, shuffle=False)

    top = rank_batches(model, dl, nn.CrossEntropyLoss(), k=2)
    assert len(top) == 2
    assert top[0][1] >= top[1][1]

def test_rank_samples_returns_k_and_sorted():
    torch.manual_seed(2)
    model = TinyNet()
    x = torch.randn(50, 10)
    y = torch.randint(0, 3, (50,))
    dl = DataLoader(TensorDataset(x, y), batch_size=10, shuffle=False)

    top = rank_samples(model, dl, nn.CrossEntropyLoss(), k=5, max_batches=2)
    assert len(top) == 5
    assert top[0][1] >= top[1][1]

