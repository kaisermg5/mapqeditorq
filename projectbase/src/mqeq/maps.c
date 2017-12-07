

#include <global.h>
#include <map.h>
#include <palette.h>

void mqeq_custom_load_map_data(struct MapDataGenericHeader r4[]) {
	u32 i = 0;
	do {
		if (r4[i].uncomp_address) {
			u8 * ptr = (r4[i].data_ptr & 0x7fffffff) + 0x08324ae4;
			if (r4[i].uncomp_size & 0x80000000) {
				if (r4[i].uncomp_address & 0x06000000) {
					LZ77UnCompVram(ptr, r4[i].uncomp_address);
				} else {
					LZ77UnCompWram(ptr, r4[i].uncomp_address);
				}
			} else {
				memcpy(ptr, r4[i].uncomp_address, r4[i].uncomp_size);
			}
		} else {
			/* // original:
			load_palettes((u16) r4[i].data_ptr); 
			sub_080533cc(); */

			// custom:
			if (r4[i].data_ptr & 0x08000000) {
				copy_palettes_to_wram(r4[i].data_ptr, 2, 13);
			} else {
				load_palettes((u16) r4[i].data_ptr);
			}
			sub_080533cc();
		}
	} while (r4[i++].data_ptr & 0x80000000);
}


