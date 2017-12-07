

#ifndef MEMORY_H
#define MEMORY_H


extern void LZ77UnCompVram(void * src, void * dest); // 0x080b14d8
extern void LZ77UnCompWram(void * src, void * dest); // 0x080b14dc
extern void memcpy(void * src, void * dest, u32 size); // 0x0801d66c

#endif
