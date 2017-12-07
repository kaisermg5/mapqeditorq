
#ifndef STRING_H
#define STRING_H

// String ids = ((index & 0xFF) << 8) | (subindex & 0xFF)

struct StringCopyManager {
/*0x00*/	u8 never_seen[8];
/*0x08*/	u16 cur_string_ids;
};

struct StringCopyManager aStringCopyManager;	// 0x020227a0


extern u32 *textTablePtrPerLanguage[7]; 	// 0x08109214, there is only one language, they all point to the english table

extern u32 englishTextTable[]; // 0x089b1d90
// It cointains some u32 values. Adding englishTextTable and the value, 
// you get a pointer to a subtable

extern void string_get_ptr_from_ids(struct StringCopyManager scm, u16 string_ids); // 0x0805eeb4
// This function is pretty much unusable, but it is the one that gets the pointer to a  
// string from the ids.

#endif
