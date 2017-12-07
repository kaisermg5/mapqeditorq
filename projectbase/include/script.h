
#ifndef SCRIPT_H
#define SCRIPT_H

struct ScriptRaw {
	u16 data[0];
};

struct ScriptEnv {
/*0x00*/	struct ScriptRaw * script;
/*0x04*/	u8 never_seen[4];
/*0x08*/	u32 behaviour_flags;
/*0x0C*/	u8 never_seen2[4];
/*0x10*/	u16 unk; 			// set to 0x2d by script cmd_34
/*0x12*/	u8 never_seen3[2];
/*0x14*/	u32 lastresult;
};

struct ScriptEnv2 {
/*0x00*/	u8 never_seen[0x39];
/*0x39*/	u8 ocurred_actions;
/*0x3a*/	u8 never_seen2[0x2e];
/*0x68*/	u8 something_related_to_talking; 	// used by function 0x8066289, used by the blacksmith script
};

struct GlobalScriptEnv {
/*0x00*/	u8 never_seen[6];
/*0x06*/	u8 unk;				// set to 0 with script cmd_34
/*0x07*/	u8 a_flag: 1;		// script command excecuted succesfully?
			u8 never_seen2: 7;
};

struct UnkImportant {
/*0x00*/	u8 never_seen[0xc];
/*0x0c*/	u8 unk;				// readed by script cmd_34
/*0x0d*/	u8 never_seen2[7];
/*0x14*/	u8 someflags_setted_by_script_cmds_49_to_4c;

};

struct UnkImportant unk_important;		// 0x03001160
struct GlobalScriptEnv gScriptEnv;		// 0x02033280


extern void script_cmd_0(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_10(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_11(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_12(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_13(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_14(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_15(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_16(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_17(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_18(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_19(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_1f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_20(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_21(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_22(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_23(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_24(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_25(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_26(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_27(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_28(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_29(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_2f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_30(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_31(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_32(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_33(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_34(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_35(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_36(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_37(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_38(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_39(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_3f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_40(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_41(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_42(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_43(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_44(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_45(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_46(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_47(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_48(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_49(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_4f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_50(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_51(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_52(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_53(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_54(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_55(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_56(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_57(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_58(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_59(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_5f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_60(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_61(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_62(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_63(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_64(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_65(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_66(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_67(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_68(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_69(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_6f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_70(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_71(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_72(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_73(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_74(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_75(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_76(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_77(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_78(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_79(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_7f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_80(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_81(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_82(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_83(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_84(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_85(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_86(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_87(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_88(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_89(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_8f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_90(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_91(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_92(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_93(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_94(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_95(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_96(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_97(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_98(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_99(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9a(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9b(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9c(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9d(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9e(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_9f(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a0(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a1(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a2(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a3(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a4(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a5(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a6(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a7(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a8(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_a9(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_aa(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_ab(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_ac(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_ad(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_ae(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_af(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b0(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b1(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b2(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b3(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b4(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b5(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b6(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b7(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b8(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_b9(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_ba(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_bb(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_bc(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_bd(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_be(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_bf(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c0(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c1(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c2(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c3(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c4(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c5(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c6(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c7(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c8(void * unk_struct, struct ScriptEnv * se);
extern void script_cmd_c9(void * unk_struct, struct ScriptEnv * se);

#endif // SCRIPT_H
