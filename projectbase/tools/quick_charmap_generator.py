
import argparse
import os.path
import math

p = argparse.ArgumentParser()
p.add_argument('outputfile', type=str)
p.add_argument('-f', help='Replace file if it already exists', action='store_true')
namespace = p.parse_args()

if os.path.exists(namespace.outputfile) and not namespace.f:
	print('The file already exist.\nPlease delete it to continue, or use the "-f" flag.')
	exit(-1)




def get_hex_repr(num):
	if num < 0:
		raise Exception('Invalid num')
	elif num == 0:
		byte_num = 0
	else:
		byte_num = int(math.log(num, 256))

	ret = ''
	while byte_num >= 0:
		ret += '{0:0>2} '.format(hex((num >> (8 * byte_num))& 0xff)[2::].upper())
		byte_num -= 1
	return ret


knownchars = [
	(0, 'END'),
	(0xa, 'NL'),

	(0xe, 'BYTE_0E'),
]

parameteredchars = [
	(0x01, 'SPECIAL_01_PAR_1'),
	(0x02, 'SPECIAL_02_PAR_1'),
	(0x03, 'SPECIAL_03_PAR_2'),
	(0x04, 'SPECIAL_04_PAR_2'),
	(0x05, 'SPECIAL_05_PAR_1'),
	(0x06, 'SPECIAL_06_PAR_1'),
	(0x07, 'SPECIAL_07_PAR_1'),
	(0x0c, 'SPECIAL_0C_PAR_1'),
	(0x0f, 'SPECIAL_0F_PAR_1'),
]

invalid_chars = {
	'\\': 'BACKSLASH',
	'\'': 'SINGLE_QUOTE',
	'\"': 'DOUBLE_QUOTE',
	'{': 'OPEN_CURLY',
	'}': 'CLOSE_CURLY',
}

# Append ASCII chars
for i in range(32, 127):
	char = i.to_bytes(1, 'little').decode('ascii')
	if char in invalid_chars:
		char = invalid_chars[char]
	else:
		char = "'{0}'".format(char)
	knownchars.append((i, char))

with open(namespace.outputfile, 'w') as f:
	f.write('\n')
	used = []
	for num, char in knownchars:
		f.write('{0} = {1}\n'.format(char, get_hex_repr(num)))
		used.append(num)
	f.write('\n\n@PARAMETERED\n')
	for num, char in parameteredchars:
		used.append(num)
		f.write('{0} = {1}\n'.format(char, get_hex_repr(num)))
	for i in range(256):
		if i not in used:
			f.write('BYTE_{0}= {0}\n'.format(get_hex_repr(i)))

