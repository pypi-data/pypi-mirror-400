import argparse
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from mvi import score, rank_batches, rank_samples


def run_demo():
    torch.manual_seed(0)

    model = nn.Sequential(
        nn.Linear(10, 16),
        nn.ReLU(),
        nn.Linear(16, 3),
    )
    loss_fn = nn.CrossEntropyLoss()

    x = torch.randn(128, 10)
    y = torch.randint(0, 3, (128,))
    dl = DataLoader(TensorDataset(x, y), batch_size=32, shuffle=False)

    res = score(model, dl, loss_fn, max_batches=4)

    print("\n=== MVI AUDIT DEMO ===")
    print(f"MVI score: {res.score:.4f}")
    print("Top vulnerable batches:", rank_batches(model, dl, loss_fn, k=3))
    print("Top vulnerable samples:", rank_samples(model, dl, loss_fn, k=5, max_batches=2))
    print("======================\n")


def main():
    parser = argparse.ArgumentParser(description="MVI Audit CLI")
    parser.add_argument("--demo", action="store_true", help="Run a demo audit")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        print("Try: mvi-audit --demo")


if __name__ == "__main__":
    main()

