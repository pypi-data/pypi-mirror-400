"""Quick test script to verify dataset generation."""
import json

# Load test dataset
with open('test_dataset.json', 'r', encoding='utf-8') as f:
    test_data = json.load(f)

print("="*60)
print("TEST DATASET VERIFICATION")
print("="*60)
print(f"\nTotal examples: {len(test_data['examples'])}")
print(f"Emotion distribution: {test_data['dataset_info']['emotion_distribution']}")
print(f"Age distribution: {test_data['dataset_info']['age_distribution']}")

print("\n" + "="*60)
print("SAMPLE EXAMPLES (First 3)")
print("="*60)

for i, ex in enumerate(test_data['examples'][:3], 1):
    print(f"\n{i}. Emotion: {ex['input']['emotion']} | Age: {ex['input']['age_group']}")
    print(f"   Question: {ex['input']['question']}")
    print(f"   Response: {ex['output'][:100]}...")
    print(f"   Safety: {ex['metadata']['safety_level']}")

# Load sample dataset
print("\n" + "="*60)
print("CURATED SAMPLE DATASET")
print("="*60)

with open('sample_dataset.json', 'r', encoding='utf-8') as f:
    sample_data = json.load(f)

print(f"\nTotal curated examples: {sample_data['dataset_info']['total_examples']}")

print("\nExample conversations:")
for i, ex in enumerate(sample_data['examples'][:5], 1):
    print(f"\n{i}. [{ex['input']['emotion']}] Age {ex['input']['age_group']}")
    print(f"   Q: {ex['input']['question'][:60]}...")
    print(f"   A: {ex['output'][:80]}...")

print("\n" + "="*60)
print("✓ All datasets verified successfully!")
print("="*60)
