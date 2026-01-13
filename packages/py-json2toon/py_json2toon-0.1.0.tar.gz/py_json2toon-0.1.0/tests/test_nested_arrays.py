from json2toon import ToonEncoder, ToonDecoder

data = {'data': [[[[[1, 2, 3]]]]]}
print('Original:', data)

encoder = ToonEncoder()
toon = encoder.encode(data)
print('\nTOON:')
print(toon)
print('\nTOON (repr):', repr(toon))

decoder = ToonDecoder()
result = decoder.decode(toon)
print('\nResult:', result)
print('Match:', result == data)
