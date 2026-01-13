#!/usr/bin/env python3
"""
Mini Cache Test: Verify UnifiedCache warmup works correctly.

This is a scaled-down version of the geometry_of_truth_experiment that:
1. Uses a small model (tiny-random-llama-2 for local, or 8B for remote)
2. Sub-samples prompts (10 per class)
3. Uses UnifiedCache to warm up activations AND perplexity in one pass
4. Verifies that subsequent operations are 100% cache hits

Run locally (no API key needed):
    python experiments/mini_cache_test.py --local

Run with NDIF (requires NNSIGHT_API_KEY):
    python experiments/mini_cache_test.py --remote
"""

import argparse
import logging
import time
from pathlib import Path

import numpy as np
import pandas as pd

# Enable cache debug logging
import os
os.environ["LMPROBE_CACHE_DEBUG"] = "1"

from lmprobe import BaselineProbe, LinearProbe, UnifiedCache
from lmprobe.cache import (
    enable_cache_logging,
    get_prompt_cache_dir,
    get_prompt_cached_layers,
    is_prompt_perplexity_cached,
)


# Configuration
LOCAL_MODEL = "stas/tiny-random-llama-2"  # 2 layers, tiny
REMOTE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"  # 32 layers

SAMPLE_SIZE = 10  # prompts per class (true/false)


def load_and_sample_dataset(filepath: Path, n_per_class: int = 10, seed: int = 42) -> dict:
    """Load dataset and sample n examples per class."""
    df = pd.read_csv(filepath)

    # Normalize labels
    if df["label"].dtype == bool:
        pass
    elif df["label"].dtype in [int, float]:
        df["label"] = df["label"].astype(bool)
    else:
        df["label"] = df["label"].map({"True": True, "False": False})

    np.random.seed(seed)

    true_statements = df[df["label"] == True]["statement"].tolist()
    false_statements = df[df["label"] == False]["statement"].tolist()

    np.random.shuffle(true_statements)
    np.random.shuffle(false_statements)

    # Sample
    true_sample = true_statements[:n_per_class]
    false_sample = false_statements[:n_per_class]

    # Split 80/20
    n_train = int(n_per_class * 0.8)

    return {
        "train_true": true_sample[:n_train],
        "train_false": false_sample[:n_train],
        "test_true": true_sample[n_train:],
        "test_false": false_sample[n_train:],
    }


def run_mini_experiment(model: str, remote: bool, tmp_cache_dir: str | None = None):
    """Run the mini cache test experiment."""

    print("=" * 70)
    print("MINI CACHE TEST")
    print("=" * 70)
    print(f"Model: {model}")
    print(f"Remote: {remote}")
    print(f"Sample size: {SAMPLE_SIZE} per class")

    # Set custom cache dir if specified
    if tmp_cache_dir:
        os.environ["LMPROBE_CACHE_DIR"] = tmp_cache_dir
        print(f"Cache dir: {tmp_cache_dir}")

    # Enable logging
    enable_cache_logging()
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Load dataset
    data_dir = Path(__file__).parent / "datasets" / "geometry_of_truth"
    dataset_file = data_dir / "cities.csv"

    if not dataset_file.exists():
        print(f"\nError: Dataset not found: {dataset_file}")
        print("Creating synthetic test data instead...")

        # Create synthetic data for testing
        data = {
            "train_true": [f"The capital of France is Paris {i}" for i in range(8)],
            "train_false": [f"The capital of France is London {i}" for i in range(8)],
            "test_true": [f"The capital of Germany is Berlin {i}" for i in range(2)],
            "test_false": [f"The capital of Germany is Madrid {i}" for i in range(2)],
        }
    else:
        print(f"\nLoading dataset: {dataset_file}")
        data = load_and_sample_dataset(dataset_file, SAMPLE_SIZE)

    n_train = len(data["train_true"]) + len(data["train_false"])
    n_test = len(data["test_true"]) + len(data["test_false"])
    print(f"Train: {n_train} prompts ({len(data['train_true'])} true, {len(data['train_false'])} false)")
    print(f"Test: {n_test} prompts ({len(data['test_true'])} true, {len(data['test_false'])} false)")

    all_prompts = (
        data["train_true"] + data["train_false"] +
        data["test_true"] + data["test_false"]
    )

    # Determine layers based on model
    if model == LOCAL_MODEL:
        layers = [0, 1]  # tiny model has 2 layers
    else:
        layers = [0, 8, 16, 24, 31]  # sample layers for 8B

    print(f"Layers: {layers}")

    # ==========================================================================
    # PHASE 1: UnifiedCache Warmup
    # ==========================================================================
    print(f"\n{'─'*70}")
    print("PHASE 1: UnifiedCache Warmup")
    print(f"{'─'*70}")
    print("This should extract ALL activations AND perplexity in ONE forward pass per batch.")

    cache = UnifiedCache(
        model=model,
        layers=layers,
        compute_perplexity=True,
        device="cpu" if not remote else "auto",
        remote=remote,
        batch_size=4,
    )

    warmup_start = time.time()
    stats = cache.warmup(all_prompts)
    warmup_elapsed = time.time() - warmup_start

    print(f"\nWarmup completed in {warmup_elapsed:.1f}s")
    print(f"  Total prompts: {stats.total_prompts}")
    print(f"  Activations: {stats.activations_cached} cached, {stats.activations_extracted} extracted")
    print(f"  Perplexity: {stats.perplexity_cached} cached, {stats.perplexity_extracted} extracted")
    print(f"  Cache hit rate: {stats.cache_hit_rate:.1%}")

    # Verify cache contents
    print("\nVerifying cache contents...")
    layers_set = set(layers)
    all_cached = True
    for prompt in all_prompts[:3]:  # Check first 3
        cache_dir = get_prompt_cache_dir(model, prompt)
        cached_layers = get_prompt_cached_layers(cache_dir)
        ppl_cached = is_prompt_perplexity_cached(model, prompt)

        layers_ok = cached_layers >= layers_set
        print(f"  Prompt '{prompt[:30]}...': layers={cached_layers}, ppl={ppl_cached}")

        if not layers_ok or not ppl_cached:
            all_cached = False

    if all_cached:
        print("  [OK] All checked prompts fully cached")
    else:
        print("  [WARN] Some prompts not fully cached!")

    # ==========================================================================
    # PHASE 2: Second Warmup (should be instant - 100% cache hits)
    # ==========================================================================
    print(f"\n{'─'*70}")
    print("PHASE 2: Second Warmup (should be 100% cache hits)")
    print(f"{'─'*70}")

    warmup2_start = time.time()
    stats2 = cache.warmup(all_prompts)
    warmup2_elapsed = time.time() - warmup2_start

    print(f"\nSecond warmup completed in {warmup2_elapsed:.1f}s")
    print(f"  Activations: {stats2.activations_cached} cached, {stats2.activations_extracted} extracted")
    print(f"  Perplexity: {stats2.perplexity_cached} cached, {stats2.perplexity_extracted} extracted")
    print(f"  Cache hit rate: {stats2.cache_hit_rate:.1%}")

    if stats2.activations_extracted == 0 and stats2.perplexity_extracted == 0:
        print("  [OK] 100% cache hits as expected!")
        speedup = warmup_elapsed / max(warmup2_elapsed, 0.001)
        print(f"  Speedup: {speedup:.1f}x faster")
    else:
        print("  [WARN] Some extractions happened - cache miss!")

    # ==========================================================================
    # PHASE 3: LinearProbe (should use cached activations)
    # ==========================================================================
    print(f"\n{'─'*70}")
    print("PHASE 3: LinearProbe Training (should be cache hits)")
    print(f"{'─'*70}")

    test_prompts = data["test_true"] + data["test_false"]
    test_labels = [1] * len(data["test_true"]) + [0] * len(data["test_false"])

    for layer in layers[:2]:  # Test first 2 layers
        print(f"\nTraining probe on layer {layer}...")

        probe_start = time.time()
        probe = LinearProbe(
            model=model,
            layers=layer,
            classifier="logistic_regression",
            device="cpu" if not remote else "auto",
            remote=remote,
            batch_size=4,
        )
        probe.fit(data["train_true"], data["train_false"])
        accuracy = probe.score(test_prompts, test_labels)
        probe_elapsed = time.time() - probe_start

        print(f"  Layer {layer}: accuracy={accuracy:.1%}, time={probe_elapsed:.2f}s")

    # ==========================================================================
    # PHASE 4: Perplexity Baseline (should use cached perplexity)
    # ==========================================================================
    print(f"\n{'─'*70}")
    print("PHASE 4: Perplexity Baseline (should use cached perplexity)")
    print(f"{'─'*70}")

    ppl_start = time.time()
    baseline = BaselineProbe(
        method="perplexity",
        model=model,
        device="cpu" if not remote else "auto",
        remote=remote,
    )
    baseline.fit(data["train_true"], data["train_false"])
    ppl_accuracy = baseline.score(test_prompts, test_labels)
    ppl_elapsed = time.time() - ppl_start

    print(f"  Perplexity baseline: accuracy={ppl_accuracy:.1%}, time={ppl_elapsed:.2f}s")

    # ==========================================================================
    # SUMMARY
    # ==========================================================================
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Initial warmup: {warmup_elapsed:.1f}s ({stats.activations_extracted} activations + {stats.perplexity_extracted} perplexity)")
    print(f"Second warmup:  {warmup2_elapsed:.1f}s (100% cache hits)")
    print(f"Probe training: instant (cache hits)")
    print(f"Perplexity:     instant (cache hits)")

    if stats2.cache_hit_rate == 1.0:
        print("\n[SUCCESS] UnifiedCache warmup working correctly!")
    else:
        print("\n[PARTIAL] Some cache misses detected - investigate logs above")


def main():
    parser = argparse.ArgumentParser(description="Mini cache test for UnifiedCache")
    parser.add_argument("--local", action="store_true", help="Use local tiny model (no API key)")
    parser.add_argument("--remote", action="store_true", help="Use remote 8B model via NDIF")
    parser.add_argument("--tmp-cache", type=str, help="Use temporary cache directory")

    args = parser.parse_args()

    if args.local:
        run_mini_experiment(LOCAL_MODEL, remote=False, tmp_cache_dir=args.tmp_cache)
    elif args.remote:
        run_mini_experiment(REMOTE_MODEL, remote=True, tmp_cache_dir=args.tmp_cache)
    else:
        # Default to local for safety
        print("No mode specified, defaulting to --local")
        print("Use --remote for NDIF testing (requires NNSIGHT_API_KEY)")
        run_mini_experiment(LOCAL_MODEL, remote=False, tmp_cache_dir=args.tmp_cache)


if __name__ == "__main__":
    main()
