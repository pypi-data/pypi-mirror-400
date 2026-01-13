#!/usr/bin/env python3
"""Baseline comparison experiment for dogs vs cats classification.

This script tests all available baseline methods against the best probe
performance (86.79% accuracy) on the dogs vs cats dataset.

The goal is to determine if any simpler baseline can match or beat the
linear probe, which would suggest the probe might not be learning
something meaningfully different from surface-level features.

Best probe result: 86.79% (ridge classifier at layer 71/125 on Llama-3.1-405B)
Best original baseline: TF-IDF at 75.47%

Usage:
    python baseline_comparison_experiment.py [--text-only] [--verbose]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lmprobe import BaselineBattery, BaselineProbe, ActivationBaseline


# Benchmark to beat
BEST_PROBE_ACCURACY = 0.8679
BEST_PROBE_DESC = "ridge classifier at layer 71/125 on Llama-3.1-405B"


def load_data(prompts_dir: Path) -> tuple[list[str], list[str], list[str], list[int]]:
    """Load dogs vs cats training and test data.

    Returns:
        Tuple of (positive_train, negative_train, test_prompts, test_labels)
        where positive=dog (1), negative=cat (0)
    """
    with open(prompts_dir / "dog-train.json") as f:
        dog_train = json.load(f)
    with open(prompts_dir / "cat-train.json") as f:
        cat_train = json.load(f)
    with open(prompts_dir / "dog-test.json") as f:
        dog_test = json.load(f)
    with open(prompts_dir / "cat-test.json") as f:
        cat_test = json.load(f)

    # Combine test data with labels
    test_prompts = dog_test + cat_test
    test_labels = [1] * len(dog_test) + [0] * len(cat_test)

    return dog_train, cat_train, test_prompts, test_labels


def run_text_only_baselines(
    positive_train: list[str],
    negative_train: list[str],
    test_prompts: list[str],
    test_labels: list[int],
    verbose: bool = False,
) -> dict:
    """Run all text-only baselines (no model required)."""
    print("\n" + "=" * 60)
    print("TEXT-ONLY BASELINES")
    print("=" * 60)

    battery = BaselineBattery(
        model=None,  # No model = text-only baselines
        random_state=42,
        exclude=["sentence_transformers"],  # Test separately due to download
    )

    print(f"\nRunning baselines: {battery.applicable_baselines}")
    results = battery.fit(positive_train, negative_train, test_prompts, test_labels)

    print("\n" + results.summary())

    return {r.name: r.score for r in results}


def run_sentence_transformers_baseline(
    positive_train: list[str],
    negative_train: list[str],
    test_prompts: list[str],
    test_labels: list[int],
) -> float | None:
    """Run sentence-transformers baseline (requires optional dependency)."""
    print("\n" + "=" * 60)
    print("SENTENCE-TRANSFORMERS BASELINE")
    print("=" * 60)

    try:
        import sentence_transformers
    except ImportError:
        print("sentence-transformers not installed. Skipping.")
        print("Install with: pip install lmprobe[embeddings]")
        return None

    baseline = BaselineProbe(
        method="sentence_transformers",
        random_state=42,
    )
    baseline.fit(positive_train, negative_train)
    accuracy = baseline.score(test_prompts, test_labels)

    print(f"\nsentence_transformers: {accuracy:.4f} ({accuracy*100:.2f}%)")
    return accuracy


def run_activation_baselines(
    positive_train: list[str],
    negative_train: list[str],
    test_prompts: list[str],
    test_labels: list[int],
    model: str = "meta-llama/Llama-3.1-405B-Instruct",
    layers: int | list[int] = -1,
    verbose: bool = False,
) -> dict:
    """Run activation-based baselines (requires model).

    These baselines use the same model as the probe but apply simpler
    transformations (random direction, PCA, layer 0) to test whether
    the probe's learned direction is special.
    """
    print("\n" + "=" * 60)
    print(f"ACTIVATION BASELINES (model: {model})")
    print("=" * 60)

    # Check for API key
    api_key = os.environ.get("NNSIGHT_API_KEY")
    if not api_key:
        print("\nWarning: NNSIGHT_API_KEY not set. Remote execution will fail.")
        print("Set the key with: export NNSIGHT_API_KEY='your-key'")
        return {}

    battery = BaselineBattery(
        model=model,
        layers=layers,
        device="auto",
        remote=True,  # Required for 405B model
        random_state=42,
        include=["random_direction", "pca", "layer_0", "perplexity"],
    )

    print(f"\nRunning baselines: {battery.applicable_baselines}")
    print("This may take a while for remote execution...")

    results = battery.fit(positive_train, negative_train, test_prompts, test_labels)

    print("\n" + results.summary())

    return {r.name: r.score for r in results}


def run_perplexity_baseline(
    positive_train: list[str],
    negative_train: list[str],
    test_prompts: list[str],
    test_labels: list[int],
    model: str = "meta-llama/Llama-3.1-405B-Instruct",
) -> float | None:
    """Run perplexity baseline separately (useful for debugging)."""
    print("\n" + "=" * 60)
    print(f"PERPLEXITY BASELINE (model: {model})")
    print("=" * 60)

    api_key = os.environ.get("NNSIGHT_API_KEY")
    if not api_key:
        print("\nWarning: NNSIGHT_API_KEY not set. Skipping perplexity baseline.")
        return None

    baseline = BaselineProbe(
        method="perplexity",
        model=model,
        device="auto",
        remote=True,
        random_state=42,
    )

    print("\nFitting perplexity baseline...")
    baseline.fit(positive_train, negative_train)
    accuracy = baseline.score(test_prompts, test_labels)

    print(f"\nperplexity: {accuracy:.4f} ({accuracy*100:.2f}%)")
    return accuracy


def print_comparison(all_results: dict, verbose: bool = False):
    """Print comparison of all baselines against the probe benchmark."""
    print("\n" + "=" * 60)
    print("COMPARISON TO BEST PROBE")
    print("=" * 60)
    print(f"\nBest probe accuracy: {BEST_PROBE_ACCURACY:.4f} ({BEST_PROBE_ACCURACY*100:.2f}%)")
    print(f"  ({BEST_PROBE_DESC})")

    # Sort by score
    sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)

    print(f"\nAll baseline results (sorted by accuracy):")
    print("-" * 50)

    any_beats_probe = False
    for name, score in sorted_results:
        diff = score - BEST_PROBE_ACCURACY
        diff_str = f"+{diff:.4f}" if diff >= 0 else f"{diff:.4f}"
        status = "BEATS PROBE!" if score >= BEST_PROBE_ACCURACY else ""
        if score >= BEST_PROBE_ACCURACY:
            any_beats_probe = True
        print(f"  {name:25s} {score:.4f} ({diff_str}) {status}")

    print("-" * 50)

    if any_beats_probe:
        print("\n*** WARNING: A baseline method matched or beat the probe! ***")
        print("This suggests the probe may not be learning something")
        print("meaningfully different from simpler approaches.")
    else:
        best_baseline = sorted_results[0]
        gap = BEST_PROBE_ACCURACY - best_baseline[1]
        print(f"\nBest baseline: {best_baseline[0]} ({best_baseline[1]:.4f})")
        print(f"Gap to probe: {gap:.4f} ({gap*100:.2f}%)")
        print("\nThe probe outperforms all baselines.")


def main():
    parser = argparse.ArgumentParser(
        description="Compare baseline methods against the best probe on dogs vs cats"
    )
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Only run text-based baselines (no model required)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed output",
    )
    parser.add_argument(
        "--model",
        default="meta-llama/Llama-3.1-405B-Instruct",
        help="Model for activation baselines (default: Llama-3.1-405B-Instruct)",
    )
    parser.add_argument(
        "--layers",
        type=int,
        default=-1,
        help="Layer(s) for activation extraction (default: -1 = last layer)",
    )
    args = parser.parse_args()

    # Find prompts directory
    script_dir = Path(__file__).parent
    prompts_dir = script_dir.parent / "prompts"

    if not prompts_dir.exists():
        print(f"Error: prompts directory not found at {prompts_dir}")
        sys.exit(1)

    # Load data
    print("Loading dogs vs cats dataset...")
    dog_train, cat_train, test_prompts, test_labels = load_data(prompts_dir)

    print(f"  Training: {len(dog_train)} dog + {len(cat_train)} cat prompts")
    print(f"  Test: {len(test_prompts)} prompts ({sum(test_labels)} dog, {len(test_labels) - sum(test_labels)} cat)")

    all_results = {}

    # Run text-only baselines (always)
    text_results = run_text_only_baselines(
        dog_train, cat_train, test_prompts, test_labels, args.verbose
    )
    all_results.update(text_results)

    # Run sentence-transformers baseline
    st_accuracy = run_sentence_transformers_baseline(
        dog_train, cat_train, test_prompts, test_labels
    )
    if st_accuracy is not None:
        all_results["sentence_transformers"] = st_accuracy

    # Run activation baselines (unless text-only mode)
    if not args.text_only:
        activation_results = run_activation_baselines(
            dog_train, cat_train, test_prompts, test_labels,
            model=args.model,
            layers=args.layers,
            verbose=args.verbose,
        )
        all_results.update(activation_results)
    else:
        print("\n(Skipping activation baselines in text-only mode)")

    # Print comparison
    if all_results:
        print_comparison(all_results, args.verbose)

    # Save results
    output_dir = script_dir / "experiment_results" / "baseline_comparison"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "results.json"

    with open(output_file, "w") as f:
        json.dump({
            "benchmark": {
                "accuracy": BEST_PROBE_ACCURACY,
                "description": BEST_PROBE_DESC,
            },
            "baselines": all_results,
            "text_only_mode": args.text_only,
            "model": args.model if not args.text_only else None,
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
