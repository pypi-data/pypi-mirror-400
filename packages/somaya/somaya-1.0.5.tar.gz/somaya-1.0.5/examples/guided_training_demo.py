"""
SOMA Core Guided Training Demo
===========================

Demonstrates the guided training pipeline that uses multi-model signals
to guide vocabulary building and training.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.guided_training_pipeline import GuidedTrainingPipeline

def main():
    """Demo guided training."""
    print("="*70)
    print("SOMA Core Guided Training Demo")
    print("="*70)
    print()
    print("This demo shows how the multi-model system guides training:")
    print("  1. Vocabulary building uses Promote/Demote gate")
    print("  2. Only tokens that pass the gate become vocabulary units")
    print("  3. Training focuses on high-quality, promoted tokens")
    print()
    
    # Check for training data
    possible_data = [
        Path("training_data/combined_training_data.txt"),
        Path("training_data/books/book_11.txt"),
        Path("training_data/real_training_data/real_training_data.txt"),
    ]
    
    data_file = None
    for path in possible_data:
        if path.exists() and path.stat().st_size > 100000:  # At least 100KB
            data_file = path
            break
    
    if not data_file:
        print("❌ No training data found!")
        print("\nPlease provide training data:")
        print("  - training_data/combined_training_data.txt")
        print("  - Or use: python examples/guided_training_demo.py --data your_file.txt")
        print("\nFor a quick test, you can use a small sample:")
        print("  python examples/guided_training_demo.py --data training_data/books/book_11.txt")
        return
    
    print(f"✓ Found training data: {data_file}")
    size_mb = data_file.stat().st_size / (1024 * 1024)
    print(f"  Size: {size_mb:.2f} MB")
    print()
    
    # Create pipeline (smaller vocab for demo)
    print("Creating guided training pipeline...")
    print("  (Using smaller vocab size for demo - 10K instead of 60K)")
    print()
    
    pipeline = GuidedTrainingPipeline(
        vocab_size=10000,  # Smaller for demo
        embedding_dim=256,  # Smaller for demo
        num_layers=4,  # Smaller for demo
        num_heads=4,  # Smaller for demo
        max_seq_length=512,
        learning_rate=1e-4,
        batch_size=16,
        promote_threshold=0.7
    )
    
    # Train (just 2 epochs for demo)
    print("Starting guided training (2 epochs for demo)...")
    print("  This will:")
    print("    1. Learn from text with multi-model system")
    print("    2. Analyze tokens with Promote/Demote gate")
    print("    3. Build vocabulary from promoted tokens only")
    print("    4. Train language model")
    print()
    
    success = pipeline.train(
        text_file=data_file,
        epochs=2,  # Just 2 epochs for demo
        output_dir=Path("models/guided_demo")
    )
    
    if success:
        print("\n" + "="*70)
        print("✓ Demo Complete!")
        print("="*70)
        print("\nWhat happened:")
        print("  ✓ Multi-model system analyzed tokens")
        print("  ✓ Only tokens that passed Promote gate were included")
        print("  ✓ Vocabulary built from high-confidence tokens")
        print("  ✓ Language model trained on guided vocabulary")
        print()
        print("Next steps:")
        print("  1. Check models/guided_demo/ for output files")
        print("  2. Compare vocabulary quality vs standard training")
        print("  3. Use full training: python src/training/guided_training_pipeline.py --data your_data.txt")
    else:
        print("\n❌ Demo failed - check errors above")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, help="Training data file (optional)")
    args = parser.parse_args()
    
    if args.data:
        # Override data file
        data_file = Path(args.data)
        if not data_file.exists():
            print(f"❌ File not found: {data_file}")
            sys.exit(1)
        
        # Update the demo to use this file
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.training.guided_training_pipeline import GuidedTrainingPipeline
        
        pipeline = GuidedTrainingPipeline(
            vocab_size=10000,
            embedding_dim=256,
            num_layers=4,
            num_heads=4
        )
        
        pipeline.train(
            text_file=data_file,
            epochs=2,
            output_dir=Path("models/guided_demo")
        )
    else:
        main()
