from json2toon import ToonEncoder, ToonDecoder, ToonConfig

# Test with default config
data = {'text': 'Line 1\nLine 2'}
encoder = ToonEncoder()
toon = encoder.encode(data)
print('TOON (default):')
print(repr(toon))
print()
result = ToonDecoder().decode(toon)
print('Result:', result)
print('Expected:', data)
print('Match:', result == data)
print()

# Test with quote_strings
config = ToonConfig(quote_strings=True)
encoder = ToonEncoder(config)
toon = encoder.encode(data)
print('TOON (quoted):')
print(repr(toon))
print()
result = ToonDecoder(config).decode(toon)
print('Result:', result)
print('Expected:', data)
print('Match:', result == data)
