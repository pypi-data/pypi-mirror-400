from json2toon.decoder import ToonDecoder

toon = 'items:\n["a", "b", "c"]'
lines = toon.strip().split('\n')
print('Lines:', lines)
print('Line 0:', repr(lines[0]))
print('Line 1:', repr(lines[1]))

# Check what happens
line = lines[0]
if ':' in line:
    key, _, value = line.partition(':')
    print('Key:', repr(key))
    print('Value:', repr(value.strip()))
    print('Value is empty:', not value.strip())
    
# Check next line
next_line = lines[1]
print('Next line:', repr(next_line))
print('Has colon:', ':' in next_line)
print('Indent:', len(next_line) - len(next_line.lstrip()))
