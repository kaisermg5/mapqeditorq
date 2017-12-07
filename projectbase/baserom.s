	.gba
	.thumb
	.open input_game,output_game, 0x08000000
	
	.include asm_include

	.org free_space_offset
	.importobj relocatable_obj
	
	.close


