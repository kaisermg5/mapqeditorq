

#ifndef PALETTE_H
#define PALETTE_H


struct PaletteHeader {
	u16 palette_table_index;
	u8 palette_dest_index;
	u8 amount_of_palettes;
};

extern struct PaletteHeader *palette_header_table[]; // 0x80ff850


extern u8 palette_table[][32]; // 0x86e46c8



// palette_index:
//		 0x0 to  0xf for bg's
//		0x10 to 0x1f for oam's
extern void copy_palettes_to_wram(void * palettes_ptr, u8 palette_index, u8 palette_quantity); // 0x0801d754

extern void load_palettes(u16 pal_header_index); // 0x0801d714
/*
// Equivalent:
void load_palettes(u16 pal_header_index) {
	do {
		copy_palettes_to_wram(
			palette_table[palette_header_table[pal_header_index]->palette_table_index], 
			palette_header_table[pal_header_index]->palette_dest_index, 
			palette_header_table[pal_header_index]->amount_of_palettes & 0xF
		);
	} while (palette_header_table[pal_header_index++]->amount_of_palettes & 0x80); 
}*/

extern void sub_080533cc(); // 0x080533cc

extern u32 palettes_to_update_flags; // 0x0200b644

#endif
