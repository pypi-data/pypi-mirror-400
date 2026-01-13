"""
Dog vs Cat Linear Probe Experiment

A light-hearted experiment to see if a linear probe can distinguish 
"dog energy" from "cat energy" in LLM activation space, using prompts 
that describe each animal's behavior without naming them directly.
"""

import json
from pathlib import Path
from lmprobe import LinearProbe


def load_prompts(filepath: str | Path) -> list[str]:
    """Load prompts from a JSON file."""
    with open(filepath) as f:
        return json.load(f)


def main():
    # Load data from JSON files
    data_dir = Path(__file__).parent / "prompts"
    
    train_positive = load_prompts(data_dir / "dog-train.json")  # label=1
    train_negative = load_prompts(data_dir / "cat-train.json")  # label=0
    test_positive = load_prompts(data_dir / "dog-test.json")
    test_negative = load_prompts(data_dir / "cat-test.json")
    
    print(f"Training: {len(train_positive)} dog, {len(train_negative)} cat")
    print(f"Testing:  {len(test_positive)} dog, {len(test_negative)} cat")
    
    # Combine test sets with labels
    test_prompts = test_positive + test_negative
    test_labels = [1] * len(test_positive) + [0] * len(test_negative)
    
    # Configure and train the probe
    probe = LinearProbe(
        model="meta-llama/Llama-3.1-8B",
        layers=16,                          # middle layer often works well
        pooling="last_token",
        classifier="logistic_regression",
        device="auto",
        remote=False,
        random_state=42,
    )
    
    print("\nTraining probe...")
    probe.fit(train_positive, train_negative)
    
    # Evaluate on held-out test set
    accuracy = probe.score(test_prompts, test_labels)
    print(f"\nTest accuracy: {accuracy:.2%}")
    
    # Detailed predictions
    predictions = probe.predict(test_prompts)
    probabilities = probe.predict_proba(test_prompts)
    
    # Count errors by class
    dog_errors = sum(1 for i, p in enumerate(test_positive) 
                     if predictions[i] != 1)
    cat_errors = sum(1 for i, p in enumerate(test_negative) 
                     if predictions[len(test_positive) + i] != 0)
    
    print(f"Dog errors: {dog_errors}/{len(test_positive)}")
    print(f"Cat errors: {cat_errors}/{len(test_negative)}")
    
    # Show misclassifications
    print("\n--- Misclassifications ---")
    for i, (prompt, pred, true, prob) in enumerate(zip(
        test_prompts, predictions, test_labels, probabilities
    )):
        if pred != true:
            label = "DOG" if true == 1 else "CAT"
            pred_label = "dog" if pred == 1 else "cat"
            confidence = max(prob)
            print(f"[{label}→{pred_label}] ({confidence:.0%}) {prompt[:60]}...")
    
    # Show most confident correct predictions
    print("\n--- Most Confident Correct Predictions ---")
    correct = [
        (prompt, prob, true)
        for prompt, pred, true, prob in zip(
            test_prompts, predictions, test_labels, probabilities
        )
        if pred == true
    ]
    correct.sort(key=lambda x: max(x[1]), reverse=True)
    
    for prompt, prob, true in correct[:5]:
        label = "DOG" if true == 1 else "CAT"
        confidence = max(prob)
        print(f"[{label}] ({confidence:.0%}) {prompt[:60]}...")
    
    # Show least confident predictions (closest to decision boundary)
    print("\n--- Least Confident Predictions (near boundary) ---")
    all_preds = list(zip(test_prompts, predictions, test_labels, probabilities))
    all_preds.sort(key=lambda x: abs(x[3][1] - 0.5))  # closest to 50%
    
    for prompt, pred, true, prob in all_preds[:5]:
        true_label = "DOG" if true == 1 else "CAT"
        pred_label = "dog" if pred == 1 else "cat"
        status = "✓" if pred == true else "✗"
        print(f"{status} [{true_label}→{pred_label}] ({prob[1]:.0%} dog) {prompt[:50]}...")
    
    # Save the trained probe
    output_path = Path(__file__).parent / "dog_vs_cat_probe.pkl"
    probe.save(output_path)
    print(f"\nProbe saved to: {output_path}")


if __name__ == "__main__":
    main()
