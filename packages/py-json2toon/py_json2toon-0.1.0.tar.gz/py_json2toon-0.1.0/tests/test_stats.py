import sys
sys.path.insert(0, 'src')

from json2toon.core import get_conversion_stats

# Performance comparison
sample_data = {
    "users": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "active": True},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "active": True}
    ],
    "metadata": {
        "version": "1.0",
        "timestamp": "2025-12-09",
        "count": 3
    }
}

# Get stats
stats = get_conversion_stats(sample_data)

print("Performance Comparison:")
print(f"\nJSON Length: {stats['json_length']} characters")
print(f"TOON Length: {stats['toon_length']} characters")
print(f"\nJSON Tokens: {stats['json_tokens']}")
print(f"TOON Tokens: {stats['toon_tokens']}")
print(f"\nToken Reduction: {stats['token_reduction']:.1f}%")
print(f"\n✓ TOON is more compact!" if stats['token_reduction'] > 0 else "")

print("\n✓ All stats available successfully!")
