
import sys
import argparse
import os
import errno
import binascii
import math

def hex_digits(num):
	return hex(num)[2::].upper()

def get_char(line, quote):
	quote_closed = False
	char = ''
	escape = False
	for i in range(1, len(line)):
		if line[i] != quote or escape:
			char += line[i]
			if line[i] == '\\' and not escape:
				escape = True
			elif escape:
				escape = False
		else:
			quote_closed = True
			break

	if not quote_closed:
		raise Exception('not closed quote...')
	elif not char:
		raise Exception('no char especified...')

	return char
	

def parse_line(line):
	if line[0] == '\'' or line[0] == '\"':
		char = get_char(line, line[0])	
		hex_string = (line.split('=')[-1]).split('@')[0].strip()
	else:
		line = line.split('@')[0].strip()
		char, hex_string = line.split('=')
		char = '{' + char.strip() + '}'
	num = int.from_bytes(binascii.unhexlify(hex_string.replace(' ', '')), 'big')

	return char, num

STRING_END = '{END}'
def load_charmap(filename):
	charmap = {}
	with open(filename) as f:
		lines = f.readlines()
	for line in lines:
		if '=' in line:
			char, num = parse_line(line.strip())
			charmap[num] = char

	return charmap

def get_table_ptrs(data, table_start):
	ptrs = []
	curr_pos = table_start
	done = False
	while not done:
		ptr = table_start + int.from_bytes(data[curr_pos:curr_pos + 4], 'little')
		if ptr >= 0x1000000:
			print('Invalid pointer:', hex(ptr))
			print('Aborting')
			done = True
		else:
			ptrs.append(ptr)

		curr_pos += 4
		for prev_ptr in ptrs:
			if prev_ptr <= curr_pos:
				done = True
				break
	return ptrs

def read_char(data, str_ptr, charmap):
	num = data[str_ptr]
	if num in charmap:
		char = charmap[num]
	else:
		print(data[str_ptr - 40:str_ptr])
		print(data[str_ptr:str_ptr + 40])
		raise Exception('Unknown char "{0:0>2}".'.format(hex_digits(num)))

	return char

def decode_string(data, str_ptr, charmap):
	ret = ''
	tolerance = 0
	while True:
		char = read_char(data, str_ptr, charmap)
		ret += char
		if char == STRING_END and tolerance == 0:
			break
		if tolerance > 0:
			tolerance -= 1
		elif 'SPECIAL' in char:
			tolerance = int(char.split('_')[-1].split('}')[0])
			
		str_ptr += 1
	return ret

p = argparse.ArgumentParser()
p.add_argument('rom_filename', type=str)
p.add_argument('dump_directory', type=str)
p.add_argument('-f', help='Overwrite existing files', action='store_true')
p.add_argument('charmap', type=str)
namespace = p.parse_args()

if not os.path.exists(namespace.rom_filename):
	print('Especified rom doesn\'t exist.')
	exit(-1)
elif not os.path.exists(namespace.charmap):
	print('Especified charmap doesn\'t exist.')
	exit(-1)
if os.path.exists(namespace.dump_directory) and not namespace.f:
	print('The dump directory already exists, data might get overwrited.\nEither delete it or rename it or pass the "-f" flag to continue.')
	exit(-1)

with open(namespace.rom_filename, 'rb') as f:
	data = f.read()

try:
	os.makedirs(namespace.dump_directory)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise e


#print('Getting subtables...')
main_table = get_table_ptrs(data, 0x9b1d90)

subtables = []
i = 0
for subtable_ptr in main_table:
	print('Getting subtable {} texts...'.format(i), hex(subtable_ptr))
	text_ptrs = get_table_ptrs(data, subtable_ptr)
	subtables.append(text_ptrs)
	i += 1

charmap = load_charmap(namespace.charmap)
config_filename = os.path.join(namespace.dump_directory, 'table_order.cfg')
with open(config_filename, 'w') as cfg_file:
	cfg_file.write('\n# Table header order\n')
	for i in range(len(subtables)):
		#print('Dumping subtable {}...'.format(i))
		table_filename = os.path.join(namespace.dump_directory, 'text_table_{0:0>2}.inc'.format(hex_digits(i)))
		with open(table_filename, 'w') as f:
			for j in range(len(subtables[i])):
				f.write('\ntext_{0:0>4}__08{1:0>6}:\n'.format(hex_digits((i << 8 ) | j), hex_digits(subtables[i][j])))
				f.write('\t.string "{}"\n\n'.format(decode_string(data, subtables[i][j], charmap)))
	
		cfg_file.write(table_filename + '\n')

