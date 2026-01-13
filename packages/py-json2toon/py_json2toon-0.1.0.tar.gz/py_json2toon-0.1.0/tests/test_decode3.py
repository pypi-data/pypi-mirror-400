from json2toon.decoder import ToonDecoder

toon = '''nested:
  a:
    b:
      c: d'''

print('TOON:')
print(toon)
print('\nLines:')
lines = toon.strip().split('\n')
for i, line in enumerate(lines):
    indent = len(line) - len(line.lstrip())
    print(f'{i}: indent={indent} "{line}"')

decoder = ToonDecoder()
result = decoder.decode(toon)
print('\nResult:', result)
