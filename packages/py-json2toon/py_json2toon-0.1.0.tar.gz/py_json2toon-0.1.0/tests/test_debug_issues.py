from json2toon import ToonEncoder, ToonDecoder

# Issue 1: Mixed escapes
print("=== Issue 1: Mixed escapes ===")
data1 = {'text': 'Path: C:\\test\\n\\file.txt\nNew line'}
print('Original:', repr(data1['text']))
encoder = ToonEncoder()
toon1 = encoder.encode(data1)
print('TOON:', repr(toon1))
result1 = ToonDecoder().decode(toon1)
print('Result:', repr(result1['text']))
print('Match:', result1 == data1)
print()

# Issue 2: Very long string
print("=== Issue 2: Very long string ===")
data2 = {'text': 'This is a very long string ' * 50}
toon2 = encoder.encode(data2)
result2 = ToonDecoder().decode(toon2)
print('Original length:', len(data2['text']))
print('Result length:', len(result2['text']))
print('Original ends with:', repr(data2['text'][-10:]))
print('Result ends with:', repr(result2['text'][-10:]))
print('Match:', result2 == data2)
print()

# Issue 3: Deeply nested arrays
print("=== Issue 3: Deeply nested arrays ===")
data3 = {'data': [[[[[1, 2, 3]]]]]}