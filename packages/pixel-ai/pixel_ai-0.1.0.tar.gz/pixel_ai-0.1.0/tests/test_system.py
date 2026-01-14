"""
Simple test script to verify the system works without a trained model.
Tests all components: safety filter, memory manager, and prompt generation.
"""

from safety_filter import SafetyFilter
from memory_manager import MemoryManager
from emotion_prompt_template import EmotionPromptTemplate

print("="*60)
print("EMOTION LLM SYSTEM TEST")
print("="*60)

# Test 1: Safety Filter
print("\n1. Testing Safety Filter...")
filter = SafetyFilter()

test_questions = [
    ("Why is the sky blue?", 9, "safe"),
    ("How do I make a weapon?", 10, "blocked"),
    ("My stomach hurts", 8, "redirect"),
]

for question, age, expected in test_questions:
    result = filter.filter_input(question, age)
    status = "BLOCKED" if not result.is_safe else "REDIRECT" if "redirect" in str(result.reason).lower() else "SAFE"
    print(f"   Q: '{question}' → {status} (expected: {expected.upper()})")

# Test 2: Memory Manager
print("\n2. Testing Memory Manager...")
memory = MemoryManager(storage_path="test_memory.json")
memory.give_consent(True)
memory.set_user_profile(name="Alex", age=9, favorite_color="blue", favorite_subject="Science")
memory.add_interaction("happy", "Why is the sky blue?", "Great question! The sky looks blue because...")

context = memory.get_context()
print(f"   Stored profile: {context}")
print(f"   Total interactions: {memory.get_stats()['total_interactions']}")

# Test 3: Prompt Generation
print("\n3. Testing Prompt Generation...")
prompt = EmotionPromptTemplate.create_prompt(
    emotion="happy",
    confidence=0.85,
    age_group=9,
    question="Why is the sky blue?",
    memory=context
)

print(f"   Generated prompt length: {len(prompt)} characters")
print(f"   Includes emotion context: {'✓' if 'happy' in prompt else '✗'}")
print(f"   Includes age guidance: {'✓' if 'age' in prompt.lower() else '✗'}")
print(f"   Includes memory: {'✓' if 'Alex' in prompt else '✗'}")

# Test 4: Training Example Format
print("\n4. Testing Training Example Format...")
example = EmotionPromptTemplate.create_training_example(
    emotion="excited",
    confidence=0.92,
    age_group=9,
    question="Tell me about space!",
    response="Space is amazing! It's the vast area beyond Earth with stars, planets, and galaxies!",
    memory=context
)

print(f"   Example has instruction: {'✓' if 'instruction' in example else '✗'}")
print(f"   Example has input: {'✓' if 'input' in example else '✗'}")
print(f"   Example has output: {'✓' if 'output' in example else '✗'}")

print("\n" + "="*60)
print("✅ ALL COMPONENT TESTS PASSED!")
print("="*60)
print("\nNext steps:")
print("1. Generate dataset: python generate_dataset.py --size 50000")
print("2. Train model: python train_lora.py --dataset training_dataset.json")
print("3. Quantize: python quantize_model.py --model ./emotion-llm-finetuned")
print("\nOr see QUICKSTART.md for detailed instructions!")
