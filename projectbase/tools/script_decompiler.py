#! /usr/bin/env python3

import sys

if len(sys.argv) < 3:
	print('Missing parameters')
	exit(-1)

SCRIPT_END = 0xffff

COMMAND_NAMES = {
	0x0: 'nop',
	0x1: 'enterquick',
	0x2: 'exitquick',
	0x3: 'branch_explicit',
	0x4: 'branch_ifzero_explicit',
	0x5: 'branch_ifnotzero_explicit',
	0xb: 'callfunction',
	0x14: 'checkflag',
	0x18: 'checknewactions',
	0x28: 'sendsignal',
	0x2d: 'setflag',
	0x2e: 'clearflag',
	0x31: 'waitframes',
	0x33: 'waitsignal',
	0x43: 'lock',
	0x44: 'release',
	0x45: 'lock2',
	0x47: 'setplayerscript',
	0x49: 'set_unk_important_flags_zero',
	0x4a: 'set_unk_important_flags_two',
	0x4b: 'set_unk_important_flags_four',
	0x4c: 'set_unk_important_flags_eigth',
	0x53: 'addaction_talk',
	0x59: 'waitmsg',
	0x5b: 'msgbox',
	0x5c: 'msgbox2',
	0x5d: 'msgbox3',
	0x61: 'face',
	0x63: 'faceplayer',
	0x64: 'faceme', 
	0x67: 'setmovementspeed',
	0x73: 'move',
	0x79: 'setbehaviourflag',
	0x82: 'giveitem',
	
}

COMMAND_PARAMETERS = {
	0xb: (4,),
	0x28: (4,),
	0x33: (4,),
	0x47: (4,)
}


offset = int(sys.argv[2], base=16)
f  = open(sys.argv[1], 'rb')
f.seek(offset)

def read_number(f, byte_count= 2):
	if byte_count > 0:
		return int.from_bytes(f.read(byte_count), 'little')
	else:
		return abs(byte_count)

def format_word(num):
	return '{0:0>4}'.format((hex(num)[2::]).upper())

fail_safe = 0
while True:
	data = read_number(f)
	command = data & 0x3ff
	arg_count = (data >> 0xa) - 1

	if command not in COMMAND_NAMES:
		cmd_txt = 'cmd_{}'.format(hex(command)[2::])
	else:
		cmd_txt = COMMAND_NAMES[command]

	if data != SCRIPT_END:	
		args = []
		i = 0
		while arg_count > 0:
			if command in COMMAND_PARAMETERS:
				byte_count = COMMAND_PARAMETERS[command][i]
				i += 1
			else:
				byte_count = 2
			if isinstance(byte_count, int):
				args.append(hex(read_number(f, byte_count)))		
				arg_count -= byte_count // 2
			else:
				args.append(byte_count)
		print('\t' + cmd_txt, *args)
	else:
		print('\tend')
		break;
	if fail_safe == 1000:
		print('\n\nFailed')
		break;
	fail_safe += 1


f.close()




