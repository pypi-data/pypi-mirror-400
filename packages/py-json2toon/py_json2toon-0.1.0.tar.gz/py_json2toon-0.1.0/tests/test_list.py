from json2toon.encoder import ToonEncoder
from json2toon.config import ToonConfig

encoder = ToonEncoder(ToonConfig())
item = {'id': 1, 'name': 'Alice'}

# Test at indent level 1
result = encoder._encode_value(item, 1)
print('Encoded dict at level 1:')
print(repr(result))
print(result)
