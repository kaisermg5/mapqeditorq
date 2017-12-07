
import sys

if len(sys.argv) > 1:
	for filename in sys.argv[1::]:
		print('.include "{0}"'.format(filename))
