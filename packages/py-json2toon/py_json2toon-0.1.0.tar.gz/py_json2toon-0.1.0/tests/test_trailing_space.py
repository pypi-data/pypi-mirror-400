from json2toon import ToonEncoder, ToonDecoder

# Simple trailing space test
data = {'text': 'hello '}
print('Original:', repr(data['text']))

encoder = ToonEncoder()
toon = encoder.encode(data)
print('TOON:', repr(toon))

decoder = ToonDecoder()
result = decoder.decode(toon)
print('Result:', repr(result['text']))
print('Match:', result == data)
