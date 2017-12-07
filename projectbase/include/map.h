
#ifndef MAP_H
#define MAP_H

struct MapHeader {
	s16 unk1;
	u16 unk2;
	u16 tiles_wide;
	u16 tiles_high;
	u16 tileset_subindex;
};

#define MASK_MAP_LENGTH(x) x << 4

struct MapDataGenericHeader {
	u32 data_ptr;
	u32 uncomp_address;
	u32 uncomp_size;
};

#define MASK_MAPDATA_PTR(ptr) (0x80000000 + MASK_FINAL_MAPDATA_PTR(ptr))
#define MASK_FINAL_MAPDATA_PTR(ptr) (((u32) ptr) - 0x8324ae4)

struct MapWarp {
	u16 warp_mode;
	u16 warp_tile_x;		// unused in map limit warp
	u16 warp_tile_y;		// unused in map limit warp
	u16 dest_x;
	u16 dest_y;
 	u8 limit_flags;			// one bit per half map limits (walking left at botom of map, walking left at the top of the map, walking up at the rigth half of the map...)
	u8 map_index;
	u8 map_subindex;
	u8 unk_d;
	u8 unk_e;
	u8 unk_f;
	u16 unk_10;
	u16 padding;
};

enum WarpModes {
	map_limit,
	staircase,	// tile has to have behaviour 0x91
};


#define TILESET_1_UNCOMP_ADDRESS
#define TILESET_2_UNCOMP_ADDRESS
#define MAPLAYER_1_UNCOMP_ADDRESS 0x2025eb4
#define MAPLAYER_2_UNCOMP_ADDRESS 0x200b654
#define BLOCKS_1_DATA_UNCOMP_ADDRESS 0x202ceb4
#define BLOCKS_2_DATA_UNCOMP_ADDRESS 0x2012654
#define BLOCKS_1_BEHAVIOURS_UNCOMP_ADDRESS 0x202aeb4
#define BLOCKS_2_BEHAVIOURS_UNCOMP_ADDRESS 0x2010654

extern void vanilla_load_map_data(struct MapDataGenericHeader r4[]); // 0x080197d4

#endif
