#-------------------------------------------------------------------------------

ifeq ($(strip $(DEVKITARM)),)
$(error Please set DEVKITARM in your environment. export DEVKITARM=/path/to/devkitARM)
endif

include $(DEVKITARM)/base_tools

#-------------------------------------------------------------------------------
# Tools
PYTHON3 := python3
TXT_HEADER_MAKER := $(PYTHON3) tools/create_texttable_header.py
INCLUDES_GENERATOR := $(PYTHON3) tools/includes_generator.py
POKERUBY_TOOLS := tools/pokeruby
PREPROC := $(POKERUBY_TOOLS)/preproc/preproc
SCANINC := $(POKERUBY_TOOLS)/scaninc/scaninc
GFX := $(POKERUBY_TOOLS)/gbagfx/gbagfx


MKDIR_P := mkdir -p
RM_F := rm -f

#-------------------------------------------------------------------------------

export ROM_CODE := BZME

export BUILD := build
export HEADER_DIR := include
export SRC := src
export ASM := asm
export DATA := data
export LINKER_FILES_DIR := linker
export ALL_TXT_FILE := $(BUILD)/fulltextable.s
export TXTS_DIR := $(DATA)/texts
export TXT_TABLE_CONFIG := $(TXTS_DIR)/table_order.cfg
export BASE_PREFIX := baserom
export BASEROM := $(BASE_PREFIX).gba
export BASEDATA := $(BASE_PREFIX).s
export OUTPUT := game/rom.gba
export RELOCATABLE := $(BUILD)/relocatable.o
export PATCHES := $(BUILD)/patches.inc
export FREE_SPACE_OFFSET := 0x08de7db0
export EMPTY := $(BUILD)/empty.s

export ARMIPS ?= armips
export LD := $(PREFIX)ld
export CPP := $(PREFIX)cpp

export ASFLAGS := -mthumb

export CPP_FLAGS := -I $(HEADER_DIR)
export WARNINGFLAGS :=	-Wall -Wno-discarded-array-qualifiers \
	-Wno-int-conversion
export CFLAGS := -mthumb -mno-thumb-interwork -mcpu=arm7tdmi -mtune=arm7tdmi \
	-march=armv4t -mlong-calls -fno-builtin $(WARNINGFLAGS) -O -finline

export ARMIPS_FLAGS := -strequ input_game $(BASEROM) -strequ relocatable_obj $(RELOCATABLE) \
				-strequ asm_include $(PATCHES) -equ free_space_offset $(FREE_SPACE_OFFSET)


export LDFLAGS := -r



#-------------------------------------------------------------------------------

rwildcard=$(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
getdeps=$(if $(strip $(wildcard $1)),$(shell $(SCANINC) $1),)

# Sources
C_SRC := $(call rwildcard,$(SRC),*.c) $(call rwildcard,$(DATA),*.c)
ASM_SRC := $(call rwildcard,$(ASM),*.s) $(call rwildcard,$(DATA),*.s)

ASM_PATCHES :=  $(call rwildcard,$(ASM),*.sinc)


# Texts
TXT_INCS := $(call rwildcard,$(TXTS_DIR),*.inc)
ifneq ($(strip $(TXT_INCS)),)
ASM_SRC := $(ASM_SRC) $(ALL_TXT_FILE)
endif

# Binaries
ifeq ($(strip $(ASM_SRC) $(C_SRC)),)
ASM_SRC := $(EMPTY)
endif
C_OBJ := $(C_SRC:%.c=$(BUILD)/%.o)
ASM_OBJ := $(ASM_SRC:%.s=$(BUILD)/%.o)


RELOCATABLE_OBJ := $(C_OBJ) $(ASM_OBJ)

LD_FILES := $(call rwildcard,linker,*.ld)

#-------------------------------------------------------------------------------

.PHONY: all clean

all: $(OUTPUT)

delete_rom:
	$(RM_F) $(OUTPUT)

again: delete_rom all

$(OUTPUT): $(BASEDATA) $(PATCHES) $(RELOCATABLE)
	@$(MKDIR_P) $(@D)
	$(ARMIPS) $(BASEDATA) -sym offsets.txt -strequ output_game $@ $(ARMIPS_FLAGS)

clean:
	$(RM_F) -r build $(OUTPUT)

$(PATCHES): $(ASM_PATCHES)
	@$(MKDIR_P) $(@D)
	$(INCLUDES_GENERATOR) $^ > $@

$(RELOCATABLE): $(RELOCATABLE_OBJ) $(LD_FILES)
	$(LD) $(LDFLAGS) $(foreach f,$(LD_FILES),-T $f) -o $@ $(RELOCATABLE_OBJ)


$(EMPTY):
	@$(MKDIR_P) $(@D)
	@echo "//empty" > $@

$(ALL_TXT_FILE): $(TXT_INCS) $(TXT_TABLE_CONFIG)
	@$(MKDIR_P) $(@D)
	$(TXT_HEADER_MAKER) $(TXT_TABLE_CONFIG) $@



.SECONDEXPANSION:
.PRECIOUS: $(BUILD)/%.4bpp $(BUILD)/%.gbapal $(BUILD)/%.lz

$(BUILD)/%.4bpp: %.png
	@$(MKDIR_P) $(@D)
	$(GFX) $< $@
$(BUILD)/%.gbapal: %.pal
	@$(MKDIR_P) $(@D)
	$(GFX) $< $@
$(BUILD)/%.lz: %
	@$(MKDIR_P) $(@D)
	$(GFX) $< $@

$(BUILD)/%.o: %.c $$(call getdeps,%.c)
	@$(MKDIR_P) $(@D)
	$(CPP) $< $(CPP_FLAGS) -o $(BUILD)/$*.i
	$(PREPROC) $(BUILD)/$*.i charmap.txt | $(CC) $(CFLAGS) -o $@ -c -x c -


$(BUILD)/%.o: %.s $$(call getdeps,%.s)
	@$(MKDIR_P) $(@D)
	$(PREPROC) $< charmap.txt | $(AS) $(ASFLAGS) -o $@


	
	
	
