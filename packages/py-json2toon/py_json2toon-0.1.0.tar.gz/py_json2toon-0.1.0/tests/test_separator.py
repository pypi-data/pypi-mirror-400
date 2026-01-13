"""Test custom separator configuration."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from json2toon import ToonEncoder, ToonDecoder, ToonConfig

# Test data
data = {
    "name": "Alice",
    "age": 30,
    "active": True,
    "hobbies": ["reading", "coding"],
    "address": {
        "city": "NYC",
        "zip": "10001"
    }
}

print("=" * 70)
print("Testing Custom Separator Configuration")
print("=" * 70)

# Test 1: Default separator (:)
print("\n1. Default Separator (':')")
print("-" * 70)
config_default = ToonConfig()
encoder_default = ToonEncoder(config_default)
toon_default = encoder_default.encode(data)
print(toon_default)

# Test 2: Custom separator ( = )
print("\n2. Custom Separator (' = ')")
print("-" * 70)
config_sep = ToonConfig(separator=" = ")
encoder_sep = ToonEncoder(config_sep)
toon_sep = encoder_sep.encode(data)
print(toon_sep)

# Test 3: Round-trip with custom separator
print("\n3. Round-trip Test with Custom Separator")
print("-" * 70)
decoder_sep = ToonDecoder(config_sep)
decoded = decoder_sep.decode(toon_sep)
print(f"Original: {data}")
print(f"Decoded:  {decoded}")
print(f"Match: {data == decoded}")

# Test 4: Different separator (->)
print("\n4. Custom Separator ('->')")
print("-" * 70)
config_arrow = ToonConfig(separator="->")
encoder_arrow = ToonEncoder(config_arrow)
toon_arrow = encoder_arrow.encode(data)
print(toon_arrow)

print("\n" + "=" * 70)
print("✓ All tests completed successfully!")
print("=" * 70)
