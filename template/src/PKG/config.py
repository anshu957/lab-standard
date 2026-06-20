"""Config & seed handling. Experiments read params from a YAML file — never hardcode them."""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import yaml


def load_config(path: str | Path) -> dict:
    """Load a YAML config into a dict. Ensures a `seed` key exists."""
    with open(path) as f:
        cfg = yaml.safe_load(f) or {}
    cfg.setdefault("seed", 0)
    return cfg


def set_seed(seed: int) -> int:
    """Seed Python + NumPy (+ torch/jax if present). Record the returned seed in your manifest."""
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:
        pass
    return seed


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True, help="path to the experiment's config.yaml")
    return p.parse_args()
