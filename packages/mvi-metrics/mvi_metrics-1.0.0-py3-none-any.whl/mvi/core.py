# src/mvi/core.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import math
import numpy as np
import torch
import torch.nn as nn


def cosine_distance(a: torch.Tensor, b: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Cosine distance = 1 - cosine_similarity for vectors along last dim."""
    a_n = a / (a.norm(dim=-1, keepdim=True) + eps)
    b_n = b / (b.norm(dim=-1, keepdim=True) + eps)
    cos = (a_n * b_n).sum(dim=-1)
    return 1.0 - cos


@dataclass
class MemoryItem:
    x: Any
    y: Any
    embedding: Optional[torch.Tensor]  # shape [D] recommended
    inserted_step: int
    replay_count: int = 0
    critical: bool = False
    mvi: float = 0.0


@dataclass
class MVIConfig:
    # weights
    w_utility: float = 0.5
    w_grad: float = 0.25
    w_novelty: float = 0.20
    w_freq: float = 0.05

    # scaling / normalization
    grad_scale: float = 10.0
    novelty_knn: int = 1
    novelty_clip: Tuple[float, float] = (0.0, 1.0)

    # age/decay (Ebbinghaus-style)
    age_decay_lambda: float = 0.02
    critical_boost: float = 0.30

    # keep MVI in [0,1]
    clamp_01: bool = True


class MVICalculator:
    """
    Canonical Memory Vulnerability Index (MVI) calculator for Bio-MEA.
    Computes per-sample MVI using:
      - utility (loss)
      - gradient norm (per-sample; expensive)
      - novelty (cosine distance to memory embeddings, kNN)
      - frequency (replay count)
      - critical × age decay boost (Ebbinghaus)

    You provide:
      - model
      - loss_fn with reduction='none' returning [B]
      - embed_fn(model, x) -> [B, D]
    """

    def __init__(
        self,
        model: nn.Module,
        loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        embed_fn: Callable[[nn.Module, torch.Tensor], torch.Tensor],
        cfg: Optional[MVIConfig] = None,
        device: Optional[torch.device] = None,
    ):
        self.model = model
        self.loss_fn = loss_fn
        self.embed_fn = embed_fn
        self.cfg = cfg or MVIConfig()
        self.device = device or next(model.parameters()).device

    @torch.no_grad()
    def compute_novelty(self, z: torch.Tensor, memory: Sequence[MemoryItem]) -> torch.Tensor:
        """
        Novelty for embeddings z:
          novelty = mean of k-nearest cosine distances to memory embeddings.
        If memory empty (or no embeddings), novelty = 1.0.
        """
        if z.dim() == 1:
            z = z.unsqueeze(0)  # [1, D]

        mem_embs = [m.embedding for m in memory if m.embedding is not None]
        if len(mem_embs) == 0:
            return torch.ones(z.size(0), device=z.device)

        M = torch.stack(mem_embs, dim=0).to(z.device)  # [N, D]
        dists = cosine_distance(z.unsqueeze(1), M.unsqueeze(0))  # [B, N]

        k = max(1, int(self.cfg.novelty_knn))
        knn_vals, _ = torch.topk(dists, k=k, largest=False, dim=1)
        novelty = knn_vals.mean(dim=1)

        lo, hi = self.cfg.novelty_clip
        return novelty.clamp(min=lo, max=hi)

    def _per_sample_grad_norm(self, loss_vec: torch.Tensor) -> torch.Tensor:
        """
        Compute per-sample grad norm by backwarding each loss_i separately.
        Expensive but canonical/reference-correct.

        Returns: [B] norms.
        """
        if loss_vec.dim() != 1:
            raise ValueError("loss_vec must be shape [B].")

        B = loss_vec.numel()
        norms = torch.zeros(B, device=loss_vec.device)
        params = [p for p in self.model.parameters() if p.requires_grad]

        for i in range(B):
            for p in params:
                if p.grad is not None:
                    p.grad.detach_()
                    p.grad.zero_()

            loss_vec[i].backward(retain_graph=(i < B - 1))

            total_sq = 0.0
            for p in params:
                if p.grad is None:
                    continue
                g = p.grad.detach()
                total_sq += float(torch.sum(g * g).item())
            norms[i] = math.sqrt(total_sq + 1e-12)

        for p in params:
            if p.grad is not None:
                p.grad.detach_()
                p.grad.zero_()

        return norms

    def compute_mvi_batch(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        memory: Sequence[MemoryItem],
        step: int,
        replay_counts: Optional[torch.Tensor] = None,   # [B]
        critical_flags: Optional[torch.Tensor] = None,  # [B] bool/int
        inserted_steps: Optional[torch.Tensor] = None,  # [B] if scoring existing items; else None
        compute_grad_norm: bool = True,
    ) -> Dict[str, torch.Tensor]:
        """
        Returns dict with:
          mvi, utility, grad_term, grad_norm, novelty, freq, age_boost, loss
        """
        x = x.to(self.device)
        y = y.to(self.device)

        logits = self.model(x)
        loss_vec = self.loss_fn(logits, y)
        if loss_vec.dim() != 1:
            raise ValueError("loss_fn must return per-sample losses [B] (use reduction='none').")

        utility = torch.tanh(loss_vec.detach())

        with torch.no_grad():
            z = self.embed_fn(self.model, x)            # [B, D]
            novelty = self.compute_novelty(z, memory)   # [B]
            novelty = novelty.to(self.device)

        if replay_counts is None:
            replay_counts = torch.zeros_like(loss_vec.detach())
        freq = torch.log1p(torch.clamp(replay_counts.detach().float(), min=0.0))

        if critical_flags is None:
            critical_flags = torch.zeros_like(loss_vec.detach()).bool()
        else:
            critical_flags = critical_flags.bool()

        # age in steps
        if inserted_steps is None:
            age = torch.zeros_like(loss_vec.detach())
        else:
            inserted_steps = inserted_steps.to(self.device)
            age = torch.clamp((step - inserted_steps).float(), min=0.0)

        age_decay = torch.exp(-self.cfg.age_decay_lambda * age)
        age_boost = self.cfg.critical_boost * critical_flags.float() * age_decay

        if compute_grad_norm:
            grad_norm = self._per_sample_grad_norm(loss_vec)
            grad_term = torch.tanh(grad_norm / float(self.cfg.grad_scale))
        else:
            grad_norm = torch.zeros_like(loss_vec.detach())
            grad_term = torch.zeros_like(loss_vec.detach())

        mvi = (
            self.cfg.w_utility * utility
            + self.cfg.w_grad * grad_term
            + self.cfg.w_novelty * novelty
            + self.cfg.w_freq * freq
            + age_boost
        )

        if self.cfg.clamp_01:
            mvi = mvi.clamp(0.0, 1.0)

        return {
            "mvi": mvi.detach(),
            "utility": utility.detach(),
            "grad_term": grad_term.detach(),
            "grad_norm": grad_norm.detach(),
            "novelty": novelty.detach(),
            "freq": freq.detach(),
            "age_boost": age_boost.detach(),
            "loss": loss_vec.detach(),
        }


class MVIMemoryBuffer:
    """Minimal MVI-weighted buffer (reference-friendly)."""

    def __init__(self, capacity: int):
        self.capacity = int(capacity)
        self.items: List[MemoryItem] = []

    def __len__(self) -> int:
        return len(self.items)

    def insert(self, item: MemoryItem) -> None:
        self.items.append(item)
        if len(self.items) > self.capacity:
            self.evict_lowest_mvi()

    def evict_lowest_mvi(self) -> None:
        idx = int(np.argmin([it.mvi for it in self.items]))
        self.items.pop(idx)

    def sample_by_mvi(self, batch_size: int, tau: float = 1.0) -> List[MemoryItem]:
        if len(self.items) == 0:
            return []
        mvis = np.array([max(1e-6, float(it.mvi)) for it in self.items], dtype=np.float64)
        weights = (mvis ** float(tau))
        weights = weights / weights.sum()
        idxs = np.random.choice(
            len(self.items), size=min(int(batch_size), len(self.items)), replace=False, p=weights
        )
        out = [self.items[i] for i in idxs]
        for it in out:
            it.replay_count += 1
        return out


