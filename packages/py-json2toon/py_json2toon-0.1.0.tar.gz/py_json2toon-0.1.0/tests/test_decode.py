from json2toon.decoder import ToonDecoder

toon = 'items:\n["a", "b", "c"]'
print('Parsing TOON:', repr(toon))
decoder = ToonDecoder()
result = decoder.decode(toon)
print('Result:', result)
