
.macro nop
.2byte 0x400
.endm

.macro enterquick
.2byte 0x401
.endm

.macro exitquick
.2byte 0x402
.endm

/*									.macro branch from:req to:req
									.2byte 0x803
									.2byte (\to - \from - 2) 
									.endm

									.macro branch_ifnotzero from:req to:req
									.2byte 0x804
									.2byte (\to - \from - 2) 
									.endm

									.macro branch_ifzero from:req to:req
									.2byte 0x805
									.2byte (\to - \from - 2) 
									.endm
*/
.macro branch to:req
.2byte 0x803
.2byte (\to - .) 
.endm

.macro branch_ifnotzero to:req
.2byte 0x804
.2byte (\to - .) 
.endm

.macro branch_ifzero to:req
.2byte 0x805
.2byte (\to - .) 
.endm


.macro branch_explicit factor:req
.2byte 0x803
.2byte \factor 
.endm

.macro branch_ifnotzero_explicit factor:req
.2byte 0x804
.2byte \factor 
.endm
.macro branch_ifzero_explicit factor:req
.2byte 0x805
.2byte \factor 
.endm



.macro callfunction func_ptr:req
.2byte 0xc0b
.4byte \func_ptr
.endm

.macro checkflag par:req
.2byte 0x814
.2byte \par
.endm

.macro cmd_16 par1:req par2:req par3:req
.2byte 0x1016
.2byte \par1
.2byte \par2
.2byte \par3
.endm

.macro checknewactions
.2byte 0x418
.endm

.macro cmd_1c
.2byte 0x41c
.endm

.macro sendsignal flags:req
.2byte 0xc28
.4byte \flags
.endm

.macro setflag flag:req
.2byte 0x82d
.2byte \flag
// flag has to be more than 0
.endm

.macro clearflag flag:req
.2byte 0x82e
.2byte \flag
.endm

.macro waitframes par:req
.2byte 0x831
.2byte \par
.endm

.macro waitsignal flags:req
.2byte 0xc33
.4byte \flags
.endm

.macro cmd_34
.2byte 0x434
.endm

.macro cmd_37
.2byte 0x437
.endm

.macro cmd_38 par:req
.2byte 0x838
.2byte \par
.endm

.macro cmd_3d
.2byte 0x43d
.endm

.macro lock
.2byte 0x443
.endm

.macro release
.2byte 0x444
.endm

.macro lock2
.2byte 0x445
.endm

.macro setplayerscript par1:req
.2byte 0xc47
.4byte \par1
.endm

.macro set_unk_important_flags_zero
.2byte 0x449
.endm

.macro set_unk_important_flags_two
.2byte 0x44a
.endm

.macro set_unk_important_flags_four
.2byte 0x44b
.endm

.macro set_unk_important_flags_eigth
.2byte 0x44c
.endm

.macro cmd_4d par:req
.2byte 0x84d
.2byte \par
.endm

.macro cmd_50 par:req
.2byte 0x850
.2byte \par
.endm

.macro cmd_51
.2byte 0x451
.endm

.macro addaction_talk
.2byte 0x453
.endm

.macro waitmsg
.2byte 0x459
.endm

.macro msgbox msg_num:req
.2byte 0x85b
.2byte \msg_num
.endm

.macro msgbox2 msg_num:req par2:req
.2byte 0xc5c
.2byte \msg_num
.2byte \par2
.endm

.macro msgbox3 msg_num:req par2:req
.2byte 0xc5d
.2byte \msg_num
.2byte \par2
.endm

.macro cmd_5f par:req
.2byte 0x85f
.2byte \par
.endm

.macro face direction:req
.2byte 0x861
.2byte \direction
// 0x0, 0x1: up
// 0x2, 0x3: right
// 0x4, 0x5: down
// 0x6, 0x7: up
// and it repeats...
.endm

.macro faceplayer
.2byte 0x463
.endm

.macro faceme
.2byte 0x464
.endm

.macro setmovementspeed speed:req
.2byte 0x867
.2byte \speed
.endm

.macro move x:req y:req
.2byte 0xc73
.2byte \x
.2byte \y
.endm

.macro setbehaviourflag flag:req
.2byte 0x879
.2byte \flag

// 0x0	-	not walking
// 0x1	-	walking
// 0x4	- 	exclamation mark globe per 60 frames
// 0xa	-	not traspasable
.endm

.macro cmd_7b par:req
.2byte 0x87b
.2byte \par
.endm

.macro giveitem par:req
.2byte 0x882
.2byte \par
.endm

.macro end
.2byte 0xffff
.endm


.macro simple_msgbox msg_indexes:req
.2byte 0x8ca
.2byte \msg_indexes
.endm
