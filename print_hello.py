import sys

if __name__ == "__main__":
    print("Hello, World!")
    args = sys.argv[1:]
    print("Passed in arguments: ", args)
    print("Epoch 43/64")
    print("  Train Loss: 6.0207")
    print("  Val Loss: 8.3453")
    print(
        "  Metrics: {'r@1': 4.232327461242676, 'r@5': 14.281291961669922, 'r@10': 21.943944931030273, 'mAR@5': 7.6793961226940155}"
    )
    print("  Checkpoint saved: checkpoints_20260522-113459/best_model.pt")
    print("  ✓ New best model! (r@1: 4.23)")
