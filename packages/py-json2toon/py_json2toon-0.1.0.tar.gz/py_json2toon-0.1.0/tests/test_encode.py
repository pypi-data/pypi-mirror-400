from json2toon.encoder import ToonEncoder
from json2toon.config import ToonConfig

config = ToonConfig(quote_strings=True)
encoder = ToonEncoder(config)

# Test inline array
arr = ['a', 'b', 'c']
result = encoder._encode_array(arr, 1)  # indent_level = 1
print('Array result:', repr(result))
print('Has indent?', result.startswith(' '))

# Test object with array
obj = {'items': ['a', 'b', 'c']}
result2 = encoder._encode_object(obj, 0)  # indent_level = 0
print('\nObject result:')
print(repr(result2))
