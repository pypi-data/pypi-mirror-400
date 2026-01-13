#!/usr/bin/env python3
"""
Comprehensive Dogs vs Cats Layer & Classifier Experiment

This experiment explores:
1. Multiple classifier types (mass_mean, lda, logistic_regression, ridge)
2. Multi-layer strategies (all layers, fast auto-selection)
3. Normalization strategies (per_neuron, per_layer)
4. Single-layer probing across many layers
5. Visualization of results

CACHING OPTIMIZATION:
The experiment runs in two phases to maximize cache efficiency:
- Phase 1: Multi-layer strategies extract ALL candidate layers in a single forward pass
  This warms the per-layer cache with all layers for train and test prompts.
- Phase 2: Single-layer sweep is then ALL cache hits (no additional forward passes)

Result: Only 2 forward passes total (train + test), regardless of how many
layer × classifier combinations are tested.

FRACTIONAL LAYERS:
Candidate layers are specified as fractional positions (0.0 to 1.0), making
the experiment robust across different model sizes. For example, [0.25, 0.5, 0.75]
maps to layer 7 for a 32-layer model, or layer 3 for a 16-layer model.
"""

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import psutil

# Check for plotting dependencies
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib/seaborn not installed. Plots will be skipped.")
    print("Install with: pip install lmprobe[plot]")

from lmprobe import BaselineProbe, LinearProbe
from lmprobe.extraction import clear_model_cache


# =============================================================================
# Model Configuration
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str           # Short display name (e.g., "Llama-3.2-1B")
    model_id: str       # HuggingFace model ID
    remote: bool        # Whether to use remote execution (NDIF)
    device: str = "auto"


# Models to compare in this experiment
# NOTE: Llama-3.2-1B already completed - skipping to save time
MODELS = [
    # ModelConfig(
    #     name="Llama-3.2-1B",
    #     model_id="meta-llama/Llama-3.2-1B-Instruct",
    #     remote=False,
    # ),
    ModelConfig(
        name="Llama-3.1-405B",
        model_id="meta-llama/Llama-3.1-405B",
        remote=True,
    ),
]

# Memory-safe config for 405B: Use 8 layers instead of 16 to halve memory
# 405B has hidden_dim=16384, so 8 layers = 131,072 dims vs 262,144
LAYERS_405B_SAFE = tuple(i / 7 for i in range(8))  # 8 evenly-spaced positions


# =============================================================================
# Progress Utilities
# =============================================================================

def format_time(seconds: float) -> str:
    """Format seconds as human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return str(timedelta(seconds=int(seconds)))


def get_memory_usage() -> tuple[float, float]:
    """Get current and available memory in GB."""
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    available_gb = mem.available / (1024**3)
    return used_gb, available_gb


def print_memory_status(prefix: str = "") -> None:
    """Print current memory status."""
    used, available = get_memory_usage()
    total = used + available
    pct = (used / total) * 100
    status = "OK" if pct < 80 else "WARNING" if pct < 90 else "CRITICAL"
    print(f"{prefix}Memory: {used:.1f}GB used / {total:.1f}GB ({pct:.0f}%) [{status}]")


def force_gc() -> None:
    """Force garbage collection to free memory."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def print_progress_bar(current: int, total: int, width: int = 30, prefix: str = "") -> None:
    """Print a simple progress bar."""
    pct = current / total
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(f"\r{prefix}[{bar}] {current}/{total} ({pct:.0%})")
    sys.stdout.flush()


def print_results_table(results: dict, layers: list, classifiers: list, title: str = "") -> None:
    """Print a formatted results table."""
    if not results:
        return

    # Header
    clf_width = max(len(c) for c in classifiers)
    header = f"{'Layer':>6} | " + " | ".join(f"{c:>{clf_width}}" for c in classifiers)

    print(f"\n{title}" if title else "")
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    # Rows
    for layer in layers:
        row_vals = []
        for clf in classifiers:
            acc = results.get((layer, clf))
            if acc is not None:
                row_vals.append(f"{acc:>{clf_width}.1%}")
            else:
                row_vals.append(f"{'--':>{clf_width}}")
        print(f"{layer:>6} | " + " | ".join(row_vals))

    print("-" * len(header))

    # Best per classifier
    print("  Best | ", end="")
    for clf in classifiers:
        clf_results = [(l, results.get((l, clf), 0)) for l in layers if results.get((l, clf)) is not None]
        if clf_results:
            best_layer, best_acc = max(clf_results, key=lambda x: x[1])
            print(f"{best_acc:>{clf_width}.1%}", end=" | ")
        else:
            print(f"{'--':>{clf_width}}", end=" | ")
    print()


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class ExperimentConfig:
    """Experiment configuration.

    Note: model, device, and remote are set per-model from ModelConfig.
    This dataclass holds the common experiment settings.
    """
    # Model settings (set per-model from ModelConfig)
    model: str = ""
    device: str = "auto"
    remote: bool = False

    # Common settings
    batch_size: int = 8
    random_state: int = 42

    # Candidate layers: Use fractional positions for cross-model comparison
    # Set to None to force use of candidate_layer_fracs
    candidate_layers: tuple | None = None

    # Default: 16 evenly-spaced fractional positions (0.0 to 1.0)
    # For 405B: Use LAYERS_405B_SAFE (8 positions) to avoid OOM
    # Maps to actual layer indices based on model depth, enabling
    # apples-to-apples comparison across different model sizes
    candidate_layer_fracs: tuple = tuple(i / 15 for i in range(16))

    # Smaller batch size for large models to reduce peak memory
    large_model_batch_size: int = 4

    # Classifiers to compare
    classifiers: tuple = ("mass_mean", "lda", "logistic_regression", "ridge")

    # Fast auto layer selection: sweep over multiple top-k values
    # Setting a single int uses that value; a tuple sweeps over all values
    fast_auto_top_k: int = 3  # Default for backward compatibility
    fast_auto_top_k_values: tuple = (1, 2, 3, 4, 5)  # Values to sweep over

    # Normalization strategies to compare (only affects multi-layer)
    # - "per_neuron": Each neuron gets own mean/std (more parameters)
    # - "per_layer": All neurons in layer share mean/std (fewer parameters)
    normalization_strategies: tuple = ("per_neuron", "per_layer")

    # Baseline methods for comparison (text-only, no model activations)
    # - "bow": Bag-of-words
    # - "tfidf": TF-IDF weighted bag-of-words
    # - "random": Random predictions (true chance baseline)
    # - "majority": Always predict majority class
    baseline_methods: tuple = ("bow", "tfidf", "random", "majority")

    # Output directory
    output_dir: str = "experiment_results"


# =============================================================================
# Layer Resolution
# =============================================================================

def resolve_candidate_layers(fracs: tuple[float, ...], num_layers: int) -> list[int]:
    """Convert fractional layer positions to actual layer indices.

    Parameters
    ----------
    fracs : tuple[float, ...]
        Fractional positions in [0.0, 1.0].
    num_layers : int
        Total number of layers in the model.

    Returns
    -------
    list[int]
        Sorted list of unique layer indices.
    """
    layers = []
    for frac in fracs:
        # frac=0.0 -> layer 0, frac=1.0 -> layer num_layers-1
        idx = int(frac * (num_layers - 1))
        idx = max(0, min(idx, num_layers - 1))
        layers.append(idx)
    return sorted(set(layers))


def get_model_num_layers(model_name: str, device: str = "auto") -> int:
    """Get the number of layers in a model from config (without loading weights).

    Uses AutoConfig to fetch only the config.json (~1KB) instead of loading
    the full model weights (which can be 100s of GB for large models).
    """
    from lmprobe.extraction import get_num_layers_from_config
    return get_num_layers_from_config(model_name)


# =============================================================================
# Data Loading
# =============================================================================

def load_prompts(filepath: str | Path) -> list[str]:
    """Load prompts from a JSON file."""
    with open(filepath) as f:
        return json.load(f)


def load_data(data_dir: Path) -> dict:
    """Load all train/test data."""
    return {
        "train_pos": load_prompts(data_dir / "dog-train.json"),
        "train_neg": load_prompts(data_dir / "cat-train.json"),
        "test_pos": load_prompts(data_dir / "dog-test.json"),
        "test_neg": load_prompts(data_dir / "cat-test.json"),
    }


# =============================================================================
# Baselines (text-only, no model activations)
# =============================================================================

def run_baselines(config: ExperimentConfig, data: dict) -> dict:
    """
    Run text-only baselines for comparison with probes.

    These baselines don't use model activations - they only look at
    the raw text. If a probe doesn't significantly beat these baselines,
    it may just be doing sophisticated token matching.

    Returns dict with baseline results.
    """
    print("\n" + "=" * 60)
    print("BASELINES (Text-Only)")
    print("=" * 60)
    print(f"Testing {len(config.baseline_methods)} methods: {config.baseline_methods}")

    results = {}
    test_prompts = data["test_pos"] + data["test_neg"]
    test_labels = [1] * len(data["test_pos"]) + [0] * len(data["test_neg"])

    for method in config.baseline_methods:
        print(f"\n  {method:15s} ", end="", flush=True)
        start = time.time()

        baseline = BaselineProbe(
            method=method,
            classifier="logistic_regression",
            random_state=config.random_state,
        )
        baseline.fit(data["train_pos"], data["train_neg"])
        accuracy = baseline.score(test_prompts, test_labels)
        elapsed = time.time() - start

        results[method] = accuracy

        # Visual bar
        bar_len = int(accuracy * 20)
        bar = "▓" * bar_len + "░" * (20 - bar_len)
        print(f"{accuracy:6.1%} [{bar}] ({elapsed:.2f}s)")

        # Show top features for interpretable methods
        if method in ("bow", "tfidf"):
            top = baseline.get_top_features(n=5)
            if top:
                pos_features = ", ".join(f[0] for f, _ in zip(top["positive"], range(3)))
                neg_features = ", ".join(f[0] for f, _ in zip(top["negative"], range(3)))
                print(f"    Top positive: {pos_features}")
                print(f"    Top negative: {neg_features}")

    # Summary
    print(f"\n{'─'*60}")
    best_method = max(results, key=results.get)
    print(f"  Best baseline: {best_method} @ {results[best_method]:.1%}")
    print(f"{'─'*60}")

    return results


# =============================================================================
# Experiment 2: Single Layer Sweep (runs SECOND, uses cached activations)
# =============================================================================

def run_single_layer_sweep(
    config: ExperimentConfig,
    data: dict,
    candidate_layers: list[int],
    output_dir: Path | None = None,
    model_name: str = "",
) -> dict:
    """
    Train probes on each layer individually with each classifier.

    This runs AFTER multi-layer strategies, so all candidate layer activations
    are already cached. Every extraction here should be a cache hit.

    Note: Single-layer probes don't use normalization (nothing to normalize).

    Returns dict mapping (layer, classifier) -> accuracy
    """
    print("\n" + "=" * 60)
    print("PHASE 2: Single Layer Sweep (all cache hits)")
    print("=" * 60)
    print(f"Testing {len(candidate_layers)} layers x {len(config.classifiers)} classifiers")

    results = {}
    test_prompts = data["test_pos"] + data["test_neg"]
    test_labels = [1] * len(data["test_pos"]) + [0] * len(data["test_neg"])

    total = len(candidate_layers) * len(config.classifiers)
    completed = 0
    times = []
    sweep_start = time.time()

    # Track best so far
    best_acc = 0.0
    best_config = None

    for layer_idx, layer in enumerate(candidate_layers):
        layer_start = time.time()
        print(f"\n{'─'*60}")
        print(f"Layer {layer} ({layer_idx + 1}/{len(candidate_layers)})")
        print(f"{'─'*60}")

        for clf_name in config.classifiers:
            completed += 1
            iter_start = time.time()

            # Progress indicator
            print(f"  {clf_name:25s} ", end="", flush=True)

            probe = LinearProbe(
                model=config.model,
                layers=layer,
                classifier=clf_name,
                device=config.device,
                remote=config.remote,
                batch_size=config.batch_size,
                random_state=config.random_state,
                normalize_layers=False,  # Single layer, no normalization needed
            )

            probe.fit(data["train_pos"], data["train_neg"])
            accuracy = probe.score(test_prompts, test_labels)
            elapsed = time.time() - iter_start
            times.append(elapsed)

            results[(layer, clf_name)] = accuracy

            # Track best
            if accuracy > best_acc:
                best_acc = accuracy
                best_config = (layer, clf_name)

            # Print result with visual indicator
            bar_len = int(accuracy * 20)
            bar = "▓" * bar_len + "░" * (20 - bar_len)
            print(f"{accuracy:6.1%} [{bar}] ({elapsed:.1f}s)")

        # Layer summary
        layer_elapsed = time.time() - layer_start
        layer_results = {clf: results.get((layer, clf), 0) for clf in config.classifiers}
        best_clf = max(layer_results, key=layer_results.get)
        print(f"  Layer {layer} best: {best_clf} @ {layer_results[best_clf]:.1%} (layer took {format_time(layer_elapsed)})")

        # ETA
        avg_time = sum(times) / len(times)
        remaining = total - completed
        eta = avg_time * remaining
        elapsed_total = time.time() - sweep_start
        print(f"  Progress: {completed}/{total} | Elapsed: {format_time(elapsed_total)} | ETA: {format_time(eta)}")

        # Print intermediate results table after each layer
        print_results_table(
            results,
            candidate_layers[:layer_idx + 1],
            list(config.classifiers),
            title=f"Results so far (best: {best_config[1]} @ layer {best_config[0]} = {best_acc:.1%})"
        )

        # Memory management and status after each layer
        force_gc()
        print_memory_status(prefix="  ")

        # Update plot after each layer if output_dir provided
        if output_dir and HAS_PLOTTING:
            update_progress_plot(config, candidate_layers, results, output_dir, model_name)

    # Final summary
    print(f"\n{'='*60}")
    print(f"Single Layer Sweep Complete!")
    print(f"Total time: {format_time(time.time() - sweep_start)}")
    print(f"Best result: {best_config[1]} @ layer {best_config[0]} = {best_acc:.1%}")
    print(f"{'='*60}")

    return results


def update_progress_plot(
    config: ExperimentConfig,
    candidate_layers: list[int],
    results: dict,
    output_dir: Path,
    model_name: str = "",
) -> None:
    """Update the accuracy line plot with current results."""
    if not HAS_PLOTTING:
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    layers = candidate_layers

    for clf in config.classifiers:
        accuracies = [results.get((l, clf)) for l in layers]
        # Only plot layers we have results for
        valid_layers = [l for l, a in zip(layers, accuracies) if a is not None]
        valid_accs = [a for a in accuracies if a is not None]
        if valid_accs:
            ax.plot(valid_layers, valid_accs, marker="o", label=clf, linewidth=2, markersize=6)

    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Accuracy")
    title = f"Probe Accuracy by Layer - {model_name}" if model_name else "Probe Accuracy by Layer"
    ax.set_title(f"{title} (in progress)\n(Dogs vs Cats)")
    ax.legend()
    ax.set_ylim(0.4, 1.0)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "accuracy_by_layer_progress.png", dpi=100)
    plt.close(fig)


# =============================================================================
# Experiment 1: Multi-Layer Strategies (runs FIRST to warm cache)
# =============================================================================

def run_multi_layer_strategies(
    config: ExperimentConfig,
    data: dict,
    candidate_layers: list[int],
) -> dict:
    """
    Run multi-layer strategies: All Layers + Fast Auto Select with k sweep.

    Tests each strategy with each normalization method (per_neuron, per_layer).
    For Fast Auto, sweeps over all top-k values in config.fast_auto_top_k_values.

    This runs FIRST in the experiment pipeline because it extracts all
    candidate layers in a single forward pass, warming the per-layer cache.
    Subsequent single-layer experiments will be pure cache hits.

    Returns dict with results for each strategy, normalization, classifier, and k value.
    """
    # Get k values to sweep (use tuple if available, otherwise single value)
    k_values = config.fast_auto_top_k_values or (config.fast_auto_top_k,)

    print("\n" + "=" * 60)
    print("PHASE 1: Multi-Layer Strategies (warms cache)")
    print("=" * 60)
    print(f"Extracting all {len(candidate_layers)} candidate layers: {candidate_layers}")
    print(f"Testing {len(config.normalization_strategies)} normalizations x {len(config.classifiers)} classifiers")
    print(f"Fast Auto k values: {k_values}")

    results = {
        "all_layers": {norm: {} for norm in config.normalization_strategies},
        "fast_auto": {norm: {k: {} for k in k_values} for norm in config.normalization_strategies},
        "fast_auto_selected_layers": {norm: {k: {} for k in k_values} for norm in config.normalization_strategies},
        "fast_auto_importances": {norm: {k: {} for k in k_values} for norm in config.normalization_strategies},
        "k_values": k_values,
    }

    test_prompts = data["test_pos"] + data["test_neg"]
    test_labels = [1] * len(data["test_pos"]) + [0] * len(data["test_neg"])

    # Calculate total steps: all_layers + fast_auto for each k
    n_norms = len(config.normalization_strategies)
    n_clfs = len(config.classifiers)
    n_k = len(k_values)
    total_steps = n_clfs * n_norms * (1 + n_k)  # 1 all_layers + n_k fast_auto per norm per classifier
    completed = 0
    phase_start = time.time()

    # Track probe for layer importance plotting
    probe_for_plotting = None

    for clf_idx, clf_name in enumerate(config.classifiers):
        print(f"\n{'─'*60}")
        print(f"Classifier: {clf_name} ({clf_idx + 1}/{len(config.classifiers)})")
        print(f"{'─'*60}")

        for norm_idx, norm_strategy in enumerate(config.normalization_strategies):
            norm_label = f"[{norm_strategy}]"
            cache_status = "(extracting & caching)" if clf_idx == 0 and norm_idx == 0 else "(cache hit)"

            # Strategy 1: All candidate layers concatenated
            completed += 1
            print(f"  {norm_label:14s} All Layers ({len(candidate_layers)} layers) {cache_status}... ", end="", flush=True)
            start = time.time()
            probe_all = LinearProbe(
                model=config.model,
                layers=candidate_layers,
                classifier=clf_name,
                device=config.device,
                remote=config.remote,
                batch_size=config.batch_size,
                random_state=config.random_state,
                normalize_layers=norm_strategy,
            )
            probe_all.fit(data["train_pos"], data["train_neg"])
            acc_all = probe_all.score(test_prompts, test_labels)
            results["all_layers"][norm_strategy][clf_name] = acc_all
            elapsed = time.time() - start
            bar_len = int(acc_all * 20)
            bar = "▓" * bar_len + "░" * (20 - bar_len)
            print(f"{acc_all:6.1%} [{bar}] ({elapsed:.1f}s)")

            # Strategy 2: Fast Auto layer selection - sweep over k values
            for k in k_values:
                completed += 1
                print(f"  {norm_label:14s} Fast Auto (k={k})... ", end="", flush=True)
                start = time.time()
                probe_fast = LinearProbe(
                    model=config.model,
                    layers="fast_auto",
                    auto_candidates=candidate_layers,
                    fast_auto_top_k=k,
                    classifier=clf_name,
                    device=config.device,
                    remote=config.remote,
                    batch_size=config.batch_size,
                    random_state=config.random_state,
                    normalize_layers=norm_strategy,
                )
                probe_fast.fit(data["train_pos"], data["train_neg"])
                acc_fast = probe_fast.score(test_prompts, test_labels)
                selected = probe_fast.selected_layers_
                results["fast_auto"][norm_strategy][k][clf_name] = acc_fast
                results["fast_auto_selected_layers"][norm_strategy][k][clf_name] = selected
                if probe_fast.layer_importances_ is not None:
                    results["fast_auto_importances"][norm_strategy][k][clf_name] = probe_fast.layer_importances_.tolist()
                elapsed = time.time() - start
                bar_len = int(acc_fast * 20)
                bar = "▓" * bar_len + "░" * (20 - bar_len)
                print(f"{acc_fast:6.1%} [{bar}] ({elapsed:.1f}s) → {selected}")

                # Save first probe for layer importance plotting
                if probe_for_plotting is None and probe_fast.layer_importances_ is not None:
                    probe_for_plotting = probe_fast
                    results["candidate_layers"] = probe_fast.candidate_layers_

        # Summary for this classifier
        print(f"\n  Summary for {clf_name}:")
        for norm in config.normalization_strategies:
            all_acc = results["all_layers"][norm][clf_name]
            best_k = max(k_values, key=lambda k: results["fast_auto"][norm][k][clf_name])
            best_fast_acc = results["fast_auto"][norm][best_k][clf_name]
            winner = "All Layers" if all_acc >= best_fast_acc else f"Fast Auto k={best_k}"
            print(f"    {norm:12s}: All={all_acc:.1%}, Fast(best k={best_k})={best_fast_acc:.1%} → {winner}")

        # Progress
        elapsed_total = time.time() - phase_start
        print(f"  Progress: {completed}/{total_steps} | Elapsed: {format_time(elapsed_total)}")

    # Store probe for plotting
    if probe_for_plotting is not None:
        results["probe_for_plotting"] = probe_for_plotting

    # Print k-value sweep summary
    print(f"\n{'─'*60}")
    print("Fast Auto k-value sweep summary:")
    print(f"{'─'*60}")
    for norm in config.normalization_strategies:
        print(f"  [{norm}]")
        for clf in config.classifiers:
            k_accs = [(k, results["fast_auto"][norm][k][clf]) for k in k_values]
            best_k, best_acc = max(k_accs, key=lambda x: x[1])
            k_str = ", ".join([f"k={k}:{acc:.1%}" for k, acc in k_accs])
            print(f"    {clf:25s}: {k_str}  (best: k={best_k})")

    # Final summary
    print(f"\n{'='*60}")
    print(f"Phase 1 Complete! Cache warmed with all {len(candidate_layers)} layers.")
    print(f"Total time: {format_time(time.time() - phase_start)}")
    print(f"{'='*60}")

    return results


def add_best_single_comparison(
    multi_layer_results: dict,
    single_layer_results: dict,
    candidate_layers: list[int],
    classifiers: tuple[str, ...],
) -> None:
    """Add best single layer comparison to multi_layer_results (in-place).

    This is called AFTER single-layer sweep completes. No extraction needed,
    just a lookup of best results.
    """
    multi_layer_results["best_single"] = {}

    for clf_name in classifiers:
        best_layer = max(
            candidate_layers,
            key=lambda l: single_layer_results.get((l, clf_name), 0)
        )
        best_acc = single_layer_results.get((best_layer, clf_name), 0)
        multi_layer_results["best_single"][clf_name] = (best_layer, best_acc)


# =============================================================================
# Visualization
# =============================================================================

def create_visualizations(
    config: ExperimentConfig,
    candidate_layers: list[int],
    single_layer_results: dict,
    multi_layer_results: dict,
    baseline_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Generate all visualization plots."""
    if not HAS_PLOTTING:
        print("\nSkipping visualizations (matplotlib not installed)")
        return

    print("\n" + "=" * 60)
    print(f"GENERATING VISUALIZATIONS{f' - {model_name}' if model_name else ''}")
    print("=" * 60)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Heatmap: Accuracy by (layer, classifier)
    print("\n  Creating layer accuracy heatmap...")
    create_accuracy_heatmap(config, candidate_layers, single_layer_results, output_dir, model_name)

    # 2. Layer importance from Fast Auto
    print("  Creating layer importance plot...")
    create_layer_importance_plot(multi_layer_results, output_dir, model_name)

    # 3. Classifier comparison bar chart (with baseline reference lines)
    print("  Creating classifier comparison chart...")
    create_classifier_comparison(config, single_layer_results, multi_layer_results, baseline_results, output_dir, model_name)

    # 4. Accuracy by layer (line plot with baseline reference lines)
    print("  Creating accuracy by layer line plot...")
    create_accuracy_line_plot(config, candidate_layers, single_layer_results, baseline_results, output_dir, model_name)

    # 5. Normalization comparison
    print("  Creating normalization comparison chart...")
    create_normalization_comparison(config, multi_layer_results, output_dir, model_name)

    # 6. Fast Auto k-value sweep plot
    print("  Creating Fast Auto k-value sweep plot...")
    create_k_value_sweep_plot(config, multi_layer_results, output_dir, model_name)

    print(f"\n  Plots saved to: {output_dir}/")


def create_accuracy_heatmap(
    config: ExperimentConfig,
    candidate_layers: list[int],
    single_layer_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Create heatmap of accuracy by layer and classifier."""
    # Build matrix
    layers = candidate_layers
    classifiers = list(config.classifiers)

    matrix = np.zeros((len(layers), len(classifiers)))
    for i, layer in enumerate(layers):
        for j, clf in enumerate(classifiers):
            matrix[i, j] = single_layer_results.get((layer, clf), 0)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        matrix,
        annot=True,
        fmt=".1%",
        xticklabels=classifiers,
        yticklabels=layers,
        cmap="RdYlGn",
        vmin=0.5,
        vmax=1.0,
        ax=ax,
    )
    ax.set_xlabel("Classifier")
    ax.set_ylabel("Layer")
    title = f"Probe Accuracy - {model_name}" if model_name else "Probe Accuracy by Layer and Classifier"
    ax.set_title(f"{title}\n(Dogs vs Cats)")

    plt.tight_layout()
    fig.savefig(output_dir / "accuracy_heatmap.png", dpi=150)
    plt.close(fig)


def create_layer_importance_plot(multi_layer_results: dict, output_dir: Path, model_name: str = ""):
    """Create layer importance bar chart from Fast Auto."""
    if "probe_for_plotting" not in multi_layer_results:
        print("    (Skipping - no probe with layer importances)")
        return

    probe = multi_layer_results["probe_for_plotting"]
    title = f"Layer Importance - {model_name}" if model_name else "Layer Importance (Coefficient L2 Norms)"
    fig, _ = probe.plot_layer_importance(
        figsize=(12, 5),
        title=f"{title}\nDogs vs Cats Task",
    )

    fig.savefig(output_dir / "layer_importance.png", dpi=150)
    plt.close(fig)


def create_classifier_comparison(
    config: ExperimentConfig,
    single_layer_results: dict,
    multi_layer_results: dict,
    baseline_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Create grouped bar chart comparing classifiers across strategies."""
    classifiers = list(config.classifiers)
    # Use first normalization strategy for this comparison
    norm = config.normalization_strategies[0]
    k_values = multi_layer_results.get("k_values", (config.fast_auto_top_k,))
    strategies = ["Best Single Layer", "All Layers", "Fast Auto (best k)"]

    # Build data
    data = {clf: [] for clf in classifiers}
    for clf in classifiers:
        # Best single
        _, acc = multi_layer_results["best_single"][clf]
        data[clf].append(acc)
        # All layers
        data[clf].append(multi_layer_results["all_layers"][norm][clf])
        # Fast auto - use best k value
        best_k = max(k_values, key=lambda k: multi_layer_results["fast_auto"][norm][k][clf])
        data[clf].append(multi_layer_results["fast_auto"][norm][best_k][clf])

    # Plot
    x = np.arange(len(strategies))
    width = 0.2

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, clf in enumerate(classifiers):
        offset = (i - len(classifiers)/2 + 0.5) * width
        bars = ax.bar(x + offset, data[clf], width, label=clf)
        # Add value labels
        for bar, val in zip(bars, data[clf]):
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.01,
                f"{val:.1%}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    # Add baseline reference lines
    if baseline_results:
        colors = {"tfidf": "red", "bow": "orange", "random": "gray", "majority": "purple"}
        for method, acc in baseline_results.items():
            color = colors.get(method, "gray")
            ax.axhline(y=acc, color=color, linestyle="--", alpha=0.7, label=f"{method} baseline")

    ax.set_ylabel("Accuracy")
    title = f"Classifier Comparison - {model_name}" if model_name else "Classifier Comparison: Single vs Multi-Layer Strategies"
    ax.set_title(f"{title}\n(Dogs vs Cats, {norm} normalization)")
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend(loc="lower right", fontsize=8)
    ax.set_ylim(0.4, 1.05)

    plt.tight_layout()
    fig.savefig(output_dir / "classifier_comparison.png", dpi=150)
    plt.close(fig)


def create_accuracy_line_plot(
    config: ExperimentConfig,
    candidate_layers: list[int],
    single_layer_results: dict,
    baseline_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Create line plot showing accuracy by layer for each classifier."""
    fig, ax = plt.subplots(figsize=(12, 6))

    layers = candidate_layers

    for clf in config.classifiers:
        accuracies = [single_layer_results.get((l, clf), 0) for l in layers]
        ax.plot(layers, accuracies, marker="o", label=clf, linewidth=2, markersize=6)

    # Add baseline reference lines
    if baseline_results:
        colors = {"tfidf": "red", "bow": "orange", "random": "gray", "majority": "purple"}
        for method, acc in baseline_results.items():
            if method in ("tfidf", "bow"):  # Only show the interesting baselines
                color = colors.get(method, "gray")
                ax.axhline(y=acc, color=color, linestyle="--", alpha=0.7, label=f"{method} baseline")

    ax.set_xlabel("Layer Index")
    ax.set_ylabel("Accuracy")
    title = f"Probe Accuracy by Layer - {model_name}" if model_name else "Probe Accuracy by Layer vs Text Baselines"
    ax.set_title(f"{title}\n(Dogs vs Cats)")
    ax.legend(loc="lower right")
    ax.set_ylim(0.4, 1.0)
    ax.axhline(y=0.5, color="gray", linestyle=":", alpha=0.3, label="chance")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "accuracy_by_layer.png", dpi=150)
    plt.close(fig)


def create_normalization_comparison(
    config: ExperimentConfig,
    multi_layer_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Create comparison of normalization strategies."""
    classifiers = list(config.classifiers)
    norms = list(config.normalization_strategies)
    k_values = multi_layer_results.get("k_values", (config.fast_auto_top_k,))

    # Compare for both All Layers and Fast Auto (best k)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, strategy, strat_title in [
        (axes[0], "all_layers", "All Layers"),
        (axes[1], "fast_auto", "Fast Auto (best k)"),
    ]:
        x = np.arange(len(classifiers))
        width = 0.35

        for i, norm in enumerate(norms):
            offset = (i - len(norms)/2 + 0.5) * width
            if strategy == "fast_auto":
                # Use best k for each classifier
                accs = []
                for clf in classifiers:
                    best_k = max(k_values, key=lambda k: multi_layer_results[strategy][norm][k].get(clf, 0))
                    accs.append(multi_layer_results[strategy][norm][best_k].get(clf, 0))
            else:
                accs = [multi_layer_results[strategy][norm].get(clf, 0) for clf in classifiers]
            bars = ax.bar(x + offset, accs, width, label=norm)

            # Add value labels
            for bar, val in zip(bars, accs):
                ax.text(
                    bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.005,
                    f"{val:.1%}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )

        ax.set_ylabel("Accuracy")
        ax.set_title(f"{strat_title} Strategy")
        ax.set_xticks(x)
        ax.set_xticklabels(classifiers, rotation=15, ha="right")
        ax.legend()
        ax.set_ylim(0.5, 1.05)
        ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    title = f"Normalization Comparison - {model_name}" if model_name else "Normalization Strategy Comparison"
    fig.suptitle(f"{title}\n(Dogs vs Cats)", fontsize=14)
    plt.tight_layout()
    fig.savefig(output_dir / "normalization_comparison.png", dpi=150)
    plt.close(fig)


def create_k_value_sweep_plot(
    config: ExperimentConfig,
    multi_layer_results: dict,
    output_dir: Path,
    model_name: str = "",
):
    """Create plot showing Fast Auto accuracy vs k value for each classifier."""
    k_values = multi_layer_results.get("k_values", (config.fast_auto_top_k,))
    if len(k_values) <= 1:
        print("    (Skipping - only one k value)")
        return

    classifiers = list(config.classifiers)
    norms = list(config.normalization_strategies)

    # One subplot per normalization strategy
    fig, axes = plt.subplots(1, len(norms), figsize=(7 * len(norms), 6))
    if len(norms) == 1:
        axes = [axes]

    for ax, norm in zip(axes, norms):
        for clf in classifiers:
            accs = [multi_layer_results["fast_auto"][norm][k][clf] for k in k_values]
            ax.plot(list(k_values), accs, marker="o", label=clf, linewidth=2, markersize=6)

            # Mark the best k value
            best_k_idx = np.argmax(accs)
            ax.scatter([k_values[best_k_idx]], [accs[best_k_idx]], s=150,
                      marker="*", c="gold", edgecolors="black", zorder=5)

        # Add All Layers reference line for comparison
        for clf_idx, clf in enumerate(classifiers):
            all_acc = multi_layer_results["all_layers"][norm][clf]
            ax.axhline(y=all_acc, color=f"C{clf_idx}", linestyle="--", alpha=0.3)

        ax.set_xlabel("Top-k Layers")
        ax.set_ylabel("Accuracy")
        ax.set_title(f"{norm} normalization")
        ax.legend(loc="lower right", fontsize=8)
        ax.set_ylim(0.4, 1.0)
        ax.axhline(y=0.5, color="gray", linestyle=":", alpha=0.3)
        ax.grid(True, alpha=0.3)
        ax.set_xticks(list(k_values))

    title = f"Fast Auto k-Value Sweep - {model_name}" if model_name else "Fast Auto k-Value Sweep"
    fig.suptitle(f"{title}\n(Dogs vs Cats, dashed lines = All Layers baseline)", fontsize=14)
    plt.tight_layout()
    fig.savefig(output_dir / "k_value_sweep.png", dpi=150)
    plt.close(fig)


# =============================================================================
# Results Summary
# =============================================================================

def print_summary(
    config: ExperimentConfig,
    single_layer_results: dict,
    multi_layer_results: dict,
    baseline_results: dict,
):
    """Print a comprehensive summary of results."""
    k_values = multi_layer_results.get("k_values", (config.fast_auto_top_k,))

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)

    # Baselines first
    print("\n--- Text-Only Baselines ---")
    for method, acc in sorted(baseline_results.items(), key=lambda x: -x[1]):
        print(f"  {method:15s}: {acc:.2%}")
    best_baseline = max(baseline_results, key=baseline_results.get)
    best_baseline_acc = baseline_results[best_baseline]
    print(f"  {'Best baseline':15s}: {best_baseline} ({best_baseline_acc:.2%})")

    # Best single layer per classifier
    print("\n--- Best Single Layer per Classifier ---")
    for clf in config.classifiers:
        best_layer, best_acc = multi_layer_results["best_single"][clf]
        delta = best_acc - best_baseline_acc
        sign = "+" if delta > 0 else ""
        print(f"  {clf:25s}: Layer {best_layer:2d} ({best_acc:.2%}, {sign}{delta:.1%} vs baseline)")

    # Multi-layer strategies by normalization
    for norm in config.normalization_strategies:
        print(f"\n--- Multi-Layer Strategies ({norm}) ---")
        print(f"{'Classifier':<25s} {'All Layers':>12s} {'Fast Auto':>20s} {'Selected Layers'}")
        print("-" * 90)
        for clf in config.classifiers:
            all_acc = multi_layer_results["all_layers"][norm][clf]
            # Find best k for Fast Auto
            best_k = max(k_values, key=lambda k: multi_layer_results["fast_auto"][norm][k][clf])
            fast_acc = multi_layer_results["fast_auto"][norm][best_k][clf]
            selected = multi_layer_results["fast_auto_selected_layers"][norm][best_k][clf]
            print(f"{clf:<25s} {all_acc:>11.2%} {fast_acc:>11.2%} (k={best_k})  {selected}")

    # Normalization comparison
    print("\n--- Normalization Strategy Comparison ---")
    print(f"{'Classifier':<25s}", end="")
    for norm in config.normalization_strategies:
        print(f" {norm:>12s}", end="")
    print("  Better")
    print("-" * 70)

    for clf in config.classifiers:
        print(f"{clf:<25s}", end="")
        accs = {}
        for norm in config.normalization_strategies:
            acc = multi_layer_results["all_layers"][norm][clf]
            accs[norm] = acc
            print(f" {acc:>11.2%}", end="")
        best_norm = max(accs, key=accs.get)
        diff = accs[best_norm] - min(accs.values())
        print(f"  {best_norm} (+{diff:.1%})")

    # Overall winner
    print("\n--- Overall Best ---")
    all_results = []
    for clf in config.classifiers:
        _, best_single = multi_layer_results["best_single"][clf]
        all_results.append((f"{clf} (best single)", best_single))
        for norm in config.normalization_strategies:
            all_results.append((f"{clf} (all, {norm})", multi_layer_results["all_layers"][norm][clf]))
            # Find best k for Fast Auto
            best_k = max(k_values, key=lambda k: multi_layer_results["fast_auto"][norm][k][clf])
            all_results.append((f"{clf} (fast k={best_k}, {norm})", multi_layer_results["fast_auto"][norm][best_k][clf]))

    all_results.sort(key=lambda x: x[1], reverse=True)
    print(f"  Top 5:")
    for name, acc in all_results[:5]:
        print(f"    {name}: {acc:.2%}")

    # Key insights
    print("\n--- Key Insights ---")

    # Does fast_auto (best k) beat all layers?
    for norm in config.normalization_strategies:
        fast_wins = 0
        for clf in config.classifiers:
            best_k = max(k_values, key=lambda k: multi_layer_results["fast_auto"][norm][k][clf])
            if multi_layer_results["fast_auto"][norm][best_k][clf] >= multi_layer_results["all_layers"][norm][clf]:
                fast_wins += 1
        print(f"  Fast Auto (best k) >= All layers ({norm}): {fast_wins}/{len(config.classifiers)} classifiers")

    # Does multi-layer beat best single?
    norm = config.normalization_strategies[0]  # Use first norm for comparison
    multi_wins = sum(
        1 for clf in config.classifiers
        if multi_layer_results["all_layers"][norm][clf] > multi_layer_results["best_single"][clf][1]
    )
    print(f"  All layers > Best single: {multi_wins}/{len(config.classifiers)} classifiers")

    # Normalization comparison
    per_neuron_wins = 0
    per_layer_wins = 0
    for clf in config.classifiers:
        if "per_neuron" in config.normalization_strategies and "per_layer" in config.normalization_strategies:
            pn = multi_layer_results["all_layers"]["per_neuron"][clf]
            pl = multi_layer_results["all_layers"]["per_layer"][clf]
            if pn > pl:
                per_neuron_wins += 1
            elif pl > pn:
                per_layer_wins += 1
    if per_neuron_wins + per_layer_wins > 0:
        print(f"  per_neuron vs per_layer: {per_neuron_wins} wins vs {per_layer_wins} wins")


def save_results(
    config: ExperimentConfig,
    candidate_layers: list[int],
    single_layer_results: dict,
    multi_layer_results: dict,
    baseline_results: dict,
    output_dir: Path,
):
    """Save results to JSON for later analysis."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Convert tuple keys to strings for JSON
    single_json = {
        f"{layer}_{clf}": acc
        for (layer, clf), acc in single_layer_results.items()
    }

    # Prepare multi-layer results (exclude non-serializable probe)
    multi_json = {
        k: v for k, v in multi_layer_results.items()
        if k not in ("probe_for_plotting",)
    }

    # Convert k_values tuple to list for JSON serialization
    k_values = multi_layer_results.get("k_values", (config.fast_auto_top_k,))
    multi_json["k_values"] = list(k_values)

    results = {
        "config": {
            "model": config.model,
            "candidate_layer_fracs": list(config.candidate_layer_fracs),
            "candidate_layers_resolved": candidate_layers,
            "classifiers": list(config.classifiers),
            "fast_auto_top_k": config.fast_auto_top_k,
            "fast_auto_top_k_values": list(config.fast_auto_top_k_values),
            "normalization_strategies": list(config.normalization_strategies),
            "baseline_methods": list(config.baseline_methods),
        },
        "baselines": baseline_results,
        "single_layer": single_json,
        "multi_layer": multi_json,
    }

    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_dir}/results.json")


# =============================================================================
# Cross-Model Comparison Plots
# =============================================================================

def create_cross_model_plots(
    all_model_results: dict[str, dict[str, Any]],
    output_dir: Path,
):
    """Create plots comparing results across models.

    Parameters
    ----------
    all_model_results : dict
        Dictionary mapping model_name -> {
            "layer_fracs": list of fractional positions,
            "candidate_layers": list of layer indices,
            "single_layer": single layer results dict,
            "multi_layer": multi-layer results dict,
            "baselines": baseline results dict,
            "config": ExperimentConfig,
        }
    output_dir : Path
        Directory to save plots to.
    """
    if not HAS_PLOTTING:
        print("\nSkipping cross-model visualizations (matplotlib not installed)")
        return

    print("\n" + "=" * 60)
    print("GENERATING CROSS-MODEL COMPARISON PLOTS")
    print("=" * 60)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get layer fracs from first model (should be same for all)
    first_model = next(iter(all_model_results.values()))
    layer_fracs = list(first_model["layer_fracs"])

    # Define colors for models
    model_colors = plt.cm.tab10.colors

    # =========================================================================
    # Plot A: Accuracy by Layer Fraction (line plot for each classifier)
    # =========================================================================
    print("\n  Creating cross-model accuracy by layer fraction...")

    # One subplot per classifier
    config = first_model["config"]
    classifiers = list(config.classifiers)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for clf_idx, clf in enumerate(classifiers):
        ax = axes[clf_idx]
        for model_idx, (model_name, results) in enumerate(all_model_results.items()):
            candidate_layers = results["candidate_layers"]
            single_layer = results["single_layer"]
            accs = [single_layer.get((layer, clf), 0) for layer in candidate_layers]
            ax.plot(
                layer_fracs,
                accs,
                marker="o",
                label=model_name,
                color=model_colors[model_idx],
                linewidth=2,
                markersize=5,
            )

        ax.set_xlabel("Layer Fraction (0=first, 1=last)")
        ax.set_ylabel("Accuracy")
        ax.set_title(f"{clf}")
        ax.legend(loc="lower right", fontsize=8)
        ax.set_ylim(0.4, 1.0)
        ax.axhline(y=0.5, color="gray", linestyle=":", alpha=0.3)
        ax.grid(True, alpha=0.3)

    fig.suptitle("Probe Accuracy by Relative Layer Depth\n(Dogs vs Cats)", fontsize=14)
    plt.tight_layout()
    fig.savefig(output_dir / "cross_model_accuracy_by_layer_frac.png", dpi=150)
    plt.close(fig)

    # =========================================================================
    # Plot B: Best Single-Layer Accuracy Bar Comparison
    # =========================================================================
    print("  Creating cross-model best accuracy comparison...")

    fig, ax = plt.subplots(figsize=(12, 6))

    model_names = list(all_model_results.keys())
    x = np.arange(len(classifiers))
    width = 0.35
    n_models = len(model_names)

    for model_idx, model_name in enumerate(model_names):
        results = all_model_results[model_name]
        multi_layer = results["multi_layer"]
        best_accs = []
        for clf in classifiers:
            _, acc = multi_layer["best_single"][clf]
            best_accs.append(acc)

        offset = (model_idx - n_models / 2 + 0.5) * width
        bars = ax.bar(x + offset, best_accs, width, label=model_name, color=model_colors[model_idx])

        # Add value labels
        for bar, val in zip(bars, best_accs):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.1%}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_ylabel("Accuracy")
    ax.set_title("Best Single-Layer Accuracy by Classifier\n(Dogs vs Cats)")
    ax.set_xticks(x)
    ax.set_xticklabels(classifiers)
    ax.legend(loc="lower right")
    ax.set_ylim(0.4, 1.05)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(output_dir / "cross_model_best_accuracy.png", dpi=150)
    plt.close(fig)

    # =========================================================================
    # Plot C: Accuracy Difference Heatmap (if exactly 2 models)
    # =========================================================================
    if len(all_model_results) == 2:
        print("  Creating accuracy difference heatmap...")

        model_names = list(all_model_results.keys())
        model_a, model_b = model_names[0], model_names[1]
        results_a, results_b = all_model_results[model_a], all_model_results[model_b]

        # Build difference matrix (B - A)
        layers_a = results_a["candidate_layers"]
        layers_b = results_b["candidate_layers"]
        single_a = results_a["single_layer"]
        single_b = results_b["single_layer"]

        matrix = np.zeros((len(layer_fracs), len(classifiers)))
        for i, (layer_a, layer_b) in enumerate(zip(layers_a, layers_b)):
            for j, clf in enumerate(classifiers):
                acc_a = single_a.get((layer_a, clf), 0)
                acc_b = single_b.get((layer_b, clf), 0)
                matrix[i, j] = acc_b - acc_a

        fig, ax = plt.subplots(figsize=(10, 8))
        vmax = max(abs(matrix.min()), abs(matrix.max()))
        sns.heatmap(
            matrix,
            annot=True,
            fmt="+.1%",
            xticklabels=classifiers,
            yticklabels=[f"{frac:.2f}" for frac in layer_fracs],
            cmap="RdBu_r",
            center=0,
            vmin=-vmax,
            vmax=vmax,
            ax=ax,
        )
        ax.set_xlabel("Classifier")
        ax.set_ylabel("Layer Fraction")
        ax.set_title(f"Accuracy Difference ({model_b} - {model_a})\n(Dogs vs Cats)")

        plt.tight_layout()
        fig.savefig(output_dir / "cross_model_accuracy_diff.png", dpi=150)
        plt.close(fig)

    # =========================================================================
    # Plot D: Best Overall Performance (across all configurations)
    # =========================================================================
    print("  Creating cross-model best overall performance plot...")

    fig, ax = plt.subplots(figsize=(12, 7))

    model_names = list(all_model_results.keys())
    strategies = ["Best Single\nLayer", "All Layers", "Fast Auto\n(best k)"]
    x = np.arange(len(strategies))
    width = 0.35
    n_models = len(model_names)

    # Also track overall best for annotation
    overall_best = {}

    for model_idx, model_name in enumerate(model_names):
        results = all_model_results[model_name]
        multi_layer = results["multi_layer"]
        config = results["config"]
        k_values = multi_layer.get("k_values", (config.fast_auto_top_k,))
        norm = config.normalization_strategies[0]  # Use first norm

        # Find best across all classifiers for each strategy
        best_single = max(multi_layer["best_single"][clf][1] for clf in config.classifiers)
        best_all_layers = max(multi_layer["all_layers"][norm][clf] for clf in config.classifiers)
        best_fast_auto = max(
            max(multi_layer["fast_auto"][norm][k][clf] for k in k_values)
            for clf in config.classifiers
        )

        strategy_bests = [best_single, best_all_layers, best_fast_auto]
        overall_best[model_name] = max(strategy_bests)

        offset = (model_idx - n_models / 2 + 0.5) * width
        bars = ax.bar(x + offset, strategy_bests, width, label=model_name, color=model_colors[model_idx])

        # Add value labels
        for bar, val in zip(bars, strategy_bests):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{val:.1%}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold" if val == overall_best[model_name] else "normal",
            )

    ax.set_ylabel("Accuracy")
    ax.set_title("Best Performance Across All Configurations\n(Dogs vs Cats, per_neuron normalization)")
    ax.set_xticks(x)
    ax.set_xticklabels(strategies)
    ax.legend(loc="lower right")
    ax.set_ylim(0.4, 1.1)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)

    # Add overall best annotation
    textstr = "Overall Best:\n" + "\n".join([f"  {m}: {v:.1%}" for m, v in overall_best.items()])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    fig.savefig(output_dir / "cross_model_best_overall.png", dpi=150)
    plt.close(fig)

    # =========================================================================
    # Plot E: k-Value Comparison Across Models (if multiple k values)
    # =========================================================================
    first_model_k = all_model_results[list(all_model_results.keys())[0]]["multi_layer"].get("k_values", ())
    if len(first_model_k) > 1:
        print("  Creating cross-model k-value comparison plot...")

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        for clf_idx, clf in enumerate(classifiers):
            ax = axes[clf_idx]

            for model_idx, model_name in enumerate(model_names):
                results = all_model_results[model_name]
                multi_layer = results["multi_layer"]
                config = results["config"]
                k_values = multi_layer.get("k_values", (config.fast_auto_top_k,))
                norm = config.normalization_strategies[0]

                accs = [multi_layer["fast_auto"][norm][k][clf] for k in k_values]
                ax.plot(list(k_values), accs, marker="o", label=model_name,
                       color=model_colors[model_idx], linewidth=2, markersize=6)

                # Mark the best k value
                best_k_idx = np.argmax(accs)
                ax.scatter([k_values[best_k_idx]], [accs[best_k_idx]], s=150,
                          marker="*", c="gold", edgecolors="black", zorder=5)

            ax.set_xlabel("Top-k Layers")
            ax.set_ylabel("Accuracy")
            ax.set_title(f"{clf}")
            ax.legend(loc="lower right", fontsize=8)
            ax.set_ylim(0.4, 1.0)
            ax.axhline(y=0.5, color="gray", linestyle=":", alpha=0.3)
            ax.grid(True, alpha=0.3)
            ax.set_xticks(list(first_model_k))

        fig.suptitle("Fast Auto k-Value Sweep Across Models\n(Dogs vs Cats)", fontsize=14)
        plt.tight_layout()
        fig.savefig(output_dir / "cross_model_k_value_sweep.png", dpi=150)
        plt.close(fig)

    print(f"\n  Cross-model plots saved to: {output_dir}/")


# =============================================================================
# Main
# =============================================================================

def run_model_experiment(
    model_config: ModelConfig,
    base_config: ExperimentConfig,
    data: dict,
    output_dir: Path,
) -> dict[str, Any]:
    """Run experiment for a single model.

    Returns a dictionary with all results needed for cross-model comparison.
    """
    # Check if this is a large model that needs memory-safe settings
    is_large_model = "405B" in model_config.name or "70B" in model_config.name

    # Use memory-safe layer config for large models
    layer_fracs = LAYERS_405B_SAFE if is_large_model else base_config.candidate_layer_fracs
    batch_size = base_config.large_model_batch_size if is_large_model else base_config.batch_size

    if is_large_model:
        print(f"\n{'!'*60}")
        print(f"MEMORY-SAFE MODE for {model_config.name}")
        print(f"  Using {len(layer_fracs)} layers instead of {len(base_config.candidate_layer_fracs)}")
        print(f"  Batch size: {batch_size}")
        print(f"{'!'*60}")

    # Create config for this model
    config = ExperimentConfig(
        model=model_config.model_id,
        device=model_config.device,
        remote=model_config.remote,
        batch_size=batch_size,
        random_state=base_config.random_state,
        candidate_layers=base_config.candidate_layers,
        candidate_layer_fracs=layer_fracs,
        classifiers=base_config.classifiers,
        fast_auto_top_k=base_config.fast_auto_top_k,
        normalization_strategies=base_config.normalization_strategies,
        baseline_methods=base_config.baseline_methods,
        output_dir=str(output_dir),
    )

    model_name = model_config.name

    print("\n" + "=" * 60)
    print(f"RUNNING EXPERIMENT: {model_name}")
    print("=" * 60)
    print(f"  Model ID: {model_config.model_id}")
    print(f"  Remote:   {model_config.remote}")
    print(f"  Device:   {model_config.device}")

    # Resolve layer configuration
    print(f"\n{'─'*60}")
    print("Resolving layer configuration...")
    print(f"{'─'*60}")
    print(f"  Fetching model config to determine layer count...")
    num_layers = get_model_num_layers(config.model, config.device)
    print(f"  Model has {num_layers} layers")

    # Use fractional layer positions for cross-model comparison
    candidate_layers = resolve_candidate_layers(config.candidate_layer_fracs, num_layers)
    print(f"  Fractional positions: {[f'{f:.2f}' for f in config.candidate_layer_fracs]}")
    print(f"  Resolved to layers:   {candidate_layers}")

    print(f"\n{'─'*60}")
    print("Configuration:")
    print(f"{'─'*60}")
    print(f"  Model:         {config.model}")
    print(f"  Num layers:    {num_layers}")
    print(f"  Candidates:    {candidate_layers}")
    print(f"  Classifiers:   {config.classifiers}")
    print(f"  Normalization: {config.normalization_strategies}")
    print(f"  Fast Auto k:   {config.fast_auto_top_k}")
    print(f"  Remote:        {config.remote}")

    # Estimate work
    n_single = len(candidate_layers) * len(config.classifiers)
    n_multi = len(config.classifiers) * len(config.normalization_strategies) * 2
    print(f"\n  Planned work:")
    print(f"    - Phase 1 (multi-layer): {n_multi} trainings (warms cache)")
    print(f"    - Phase 2 (single-layer): {n_single} trainings (cache hits)")
    print(f"    - Total: {n_single + n_multi} trainings")

    # Create model-specific output directory
    model_output_dir = output_dir / model_name.lower().replace(" ", "-")
    model_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Output: {model_output_dir}")

    # Run experiments
    print(f"\n{'─'*60}")
    print(f"Starting Experiments for {model_name}...")
    print(f"{'─'*60}")
    print_memory_status(prefix="  Initial ")

    # Run text-only baselines first (fast, provides reference point)
    # Only run once since baselines are model-independent
    baseline_results = run_baselines(config, data)

    # Phase 1: Multi-layer strategies (runs FIRST to warm cache)
    multi_layer_results = run_multi_layer_strategies(config, data, candidate_layers)

    # Memory cleanup between phases
    force_gc()
    print_memory_status(prefix="  After Phase 1: ")

    # Phase 2: Single layer sweep (all cache hits now!)
    single_layer_results = run_single_layer_sweep(
        config, data, candidate_layers, model_output_dir, model_name
    )

    # Add best single layer comparison
    add_best_single_comparison(
        multi_layer_results,
        single_layer_results,
        candidate_layers,
        config.classifiers,
    )

    # Generate per-model visualizations
    create_visualizations(
        config,
        candidate_layers,
        single_layer_results,
        multi_layer_results,
        baseline_results,
        model_output_dir,
        model_name,
    )

    # Print per-model summary
    print_summary(config, single_layer_results, multi_layer_results, baseline_results)

    # Save per-model results
    save_results(
        config,
        candidate_layers,
        single_layer_results,
        multi_layer_results,
        baseline_results,
        model_output_dir,
    )

    # Return results for cross-model comparison
    return {
        "config": config,
        "layer_fracs": list(config.candidate_layer_fracs),
        "candidate_layers": candidate_layers,
        "single_layer": single_layer_results,
        "multi_layer": multi_layer_results,
        "baselines": baseline_results,
    }


def main():
    """Run the full multi-model experiment."""
    experiment_start = time.time()

    print("=" * 60)
    print("DOGS VS CATS: Multi-Model Layer & Classifier Experiment")
    print("=" * 60)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nModels to compare:")
    for model_config in MODELS:
        mode = "remote (NDIF)" if model_config.remote else "local"
        print(f"  - {model_config.name}: {model_config.model_id} ({mode})")

    # Base configuration (model-independent settings)
    base_config = ExperimentConfig()

    # Load data (shared across all models)
    data_dir = Path(__file__).parent.parent / "prompts"
    if not data_dir.exists():
        data_dir = Path(__file__).parent / "prompts"

    print(f"\n{'─'*60}")
    print("Loading Data:")
    print(f"{'─'*60}")
    print(f"  Source: {data_dir}")
    data = load_data(data_dir)
    print(f"  Train: {len(data['train_pos'])} dogs, {len(data['train_neg'])} cats")
    print(f"  Test:  {len(data['test_pos'])} dogs, {len(data['test_neg'])} cats")

    # Output directory
    output_dir = Path(__file__).parent / base_config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  Base output: {output_dir}")

    # Run experiments for each model
    all_model_results: dict[str, dict[str, Any]] = {}

    for model_idx, model_config in enumerate(MODELS):
        model_start = time.time()

        try:
            results = run_model_experiment(model_config, base_config, data, output_dir)
            all_model_results[model_config.name] = results

            model_time = time.time() - model_start
            print(f"\n{'─'*60}")
            print(f"{model_config.name} completed in {format_time(model_time)}")
            print(f"{'─'*60}")

        except Exception as e:
            print(f"\n{'!'*60}")
            print(f"ERROR: {model_config.name} failed: {e}")
            print(f"{'!'*60}")
            import traceback
            traceback.print_exc()
            continue

        finally:
            # Clear model cache to free GPU memory before next model
            print(f"\n  Clearing model cache for {model_config.name}...")
            clear_model_cache()

    # Generate cross-model comparison plots
    if len(all_model_results) >= 2:
        comparison_dir = output_dir / "comparison"
        create_cross_model_plots(all_model_results, comparison_dir)
    elif len(all_model_results) == 1:
        print("\n  Skipping cross-model comparison (only 1 model succeeded)")

    total_time = time.time() - experiment_start

    # Final report
    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)
    print(f"  Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Total time:  {format_time(total_time)}")
    print(f"  Models completed: {len(all_model_results)}/{len(MODELS)}")
    for model_name in all_model_results:
        model_dir = output_dir / model_name.lower().replace(" ", "-")
        print(f"    - {model_name}: {model_dir}/")
    if len(all_model_results) >= 2:
        print(f"  Comparison plots: {output_dir}/comparison/")
    print("=" * 60)


if __name__ == "__main__":
    main()
