
import argparse
import os

p = argparse.ArgumentParser()
p.add_argument('inputfile', type=str, help='a configuration file, listing all files to include in order')
p.add_argument('outputfile', type=str)


def convert_to_valid_label(s):
	s = os.path.basename(s)
	return s.replace(' ', '_').replace('.', '_')


def get_label(line):
	return line.split(':')[0].strip()

def process_config_file(filename):
	tablefilenames = []
	tablelabels = []
	with open(filename) as f:
		for line in f:
			# Lazy comments system
			if '#' in line:
				line = line.split('#')[0]
			line = line.strip()
			if line:
				tablefilenames.append(line)
				tablelabels.append('subheader_' + convert_to_valid_label(line))
	return tablefilenames, tablelabels

def write_label(label, fileobject):
	fileobject.write('\n\n{0}:\n'.format(label))

def write_table_entry(header_label, entry_label, fileobject):
	fileobject.write('.4byte {0} - {1}\n'.format(entry_label, header_label))

def write_include(filename, fileobject):
	fileobject.write('\n\n.include "{0}"\n'.format(filename))


def write_main_header(header_label, outfileobject, entry_labels):
	# Write label
	write_label(header_label, outfileobject)

	# Write table data
	for label in entry_labels:
		write_table_entry(header_label, label, outfileobject)



def write_sub_header(header_label, inputfile, outfileobject):
	# Write label
	outfileobject.write('.align 2\n')
	write_label(header_label, outfileobject)

	# Write table data
	with open(inputfile) as infileobject:
		for line in infileobject:
			line = line.strip()
			if line and line[0] != '.' and ':' in line:
				label = get_label(line)
				write_table_entry(header_label, label, outfileobject)

		# Include file
		write_include(inputfile, outfileobject)

def main(inputfile, outputfile):
	header_label = 'header_' + convert_to_valid_label(inputfile)
	tablefilenames, tablelabels = process_config_file(inputfile)

	with open(outputfile, 'w') as outfileobject:
		outfileobject.write('.align 2\n')
		outfileobject.write('.global {}\n'.format(header_label))
		write_main_header(header_label, outfileobject, tablelabels)
		for i in range(len(tablelabels)):
			write_sub_header(tablelabels[i], tablefilenames[i], outfileobject)

if __name__ == '__main__':
	namespace = p.parse_args()
	main(namespace.inputfile, namespace.outputfile)

