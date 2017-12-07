
#ifndef EWRAM_H
#define EWRAM_H

struct UnkEwram {
	u8 never_seen[7];
	u8 language_id_probably; // read when looking for a text String.
};

struct LoadedMapData {
	u8 never_seen[4];
	u8 map_index;
	u8 map_subindex;
	
};

struct MapToLoad {
	u8 never_seen[0xc];
	u8 map_index;
	u8 map_subindex;
};

struct LoadedMapData loadedMap; // 0x03000bf0
struct MapToLoad mapToLoad; // 0x030010a0


struct UnkStruct1 {
	u8 never_seen[0x860];
	u32 something1;
	u32 something2;
};		

struct UnkStruct2 {
	u8 never_seen[0x8];
	u8 unk_08;
	u8 never_seen2[0x37];
	u32 unk_flags;

};

extern struct UnkStruct1 unk_load_map_struct1; // 0x02033a90
extern struct UnkStruct2 unk_load_map_struct2; // 0x02002a40

#endif
