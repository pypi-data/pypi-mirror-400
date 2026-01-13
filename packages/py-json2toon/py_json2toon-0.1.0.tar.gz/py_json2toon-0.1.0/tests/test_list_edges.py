from json2toon import ToonEncoder, ToonDecoder

encoder = ToonEncoder()
decoder = ToonDecoder()

# Test cases
cases = [
    ('List of primitives', {'items': [1, 2, 3]}),
    ('List of strings', {'items': ['a', 'b', 'c']}),
    ('Multiple lists', {'list1': [{'a': 1}], 'list2': [{'b': 2}]}),
    ('Nested list objects', {'users': [{'name': 'Alice', 'info': {'age': 30}}]}),
    ('Empty list', {'items': []}),
    ('Mixed list', {'items': [1, 'text', {'key': 'value'}]})
]

for name, data in cases:
    toon = encoder.encode(data)
    result = decoder.decode(toon)
    match = result == data
    print(f'{name}: {"✓" if match else "✗"} Match={match}')
    if not match:
        print(f'  Original: {data}')
        print(f'  Result:   {result}')
        print(f'  TOON:\n{toon}\n')
