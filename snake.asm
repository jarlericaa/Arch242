init:
    call init_snake
    call draw_divider
    call draw_0

game_loop:
    call move_snake
    call handle_input
    # call check_collision
    # call check_eat_food
    # call draw_score
    call draw_snake
    call clear_tail
    b game_loop

init_snake:
    # hardcode to LED
    rarb 217
    acc 14
    to-mba
    
    # set length
    acc 3
    rarb 0
    to-mba
    
    # INITIALIZE SNAKE OF LENGTH 3
    # store address of each part of snake (row, col)
    # head:
    rarb 1
    rcrd 2
    acc 5
    to-mba
    acc 3
    to-mdc

    # segment 1:
    rarb 3
    rcrd 4
    acc 5
    to-mba
    acc 2
    to-mdc

    # segment 2 (where the tail pointer is first pointed):
    rarb 5
    # store 5 to tail row pointer
    from-reg 0
    rcrd 0xff
    to-mdc # store ra of row -> 0xff
    from-reg 1
    rcrd 0xfe
    to-mdc # store rb of row -> 0xfe
    # so, current addr of tail row: MEM[0xfe]:MEM[0xff]

    # next, store 6 to tail col pointer
    rcrd 6
    from-reg 2
    rarb 0xfd
    to-mba # store ra of col -> 0xfd
    from-reg 3
    rarb 0xfc
    to-mba # store rb of col -> 0xfc
    # current addr of tail col: MEM[0xfc]:MEM[0xfd]

    rarb 5
    rcrd 6
    acc 5
    to-mba
    acc 1
    to-mdc
    rarb 242
    acc 8
    to-mba
    ret

handle_input:
    from-ioa
    to-reg 4 # store value of ioa to RE for retrieval
    # check if not pressed
    and 15
    beqz continue_direction
    b check_direction

check_direction:
    # check if up
    from-reg 4
    and 1
    bnez move_up
    # check if down
    from-reg 4
    and 2
    bnez move_down
    # check if left
    from-reg 4
    and 4
    bnez move_left
    # check if right
    from-reg 4
    and 8
    bnez move_right

continue_direction:
    rarb 242
    from-mba
    to-reg 4
    b check_direction

move_up:
    rarb 1
    from-mba    # ACC = old head row
    beqz bounds_collision    # if head row is at 0 and we go up pa, collision!
    
    dec*-mba
    ret

move_down:
    rarb 1
    from-mba    # ACC = old head row

    sub 9  # ACC = old head row - 9
    beqz bounds_collision   # if ACC = 0, then old head row was 9, so if we go down pa, collision!
    
    inc*-mba
    ret

move_left:
    rarb 2
    from-mba    # ACC = old head col
    beqz bounds_collision    # if head col is at 0 and we go left pa, collision!

    dec*-mba
    ret

move_right:
    rarb 2
    from-mba    # ACC = old head col

    sub 11  # ACC = old head row - 11
    beqz bounds_collision   # if ACC = 0, then old head row col 11, so if we go right pa, collision!
    
    inc*-mba
    ret

move_snake:
    rcrd 36
    rarb 34
    move_snake_base: # if ra is zero check if rb is also zero
        bnz-a move_snake_loop
    move_snake_base2: # if ra and rb are zero return to game_loop
        bnz-b move_snake_loop
        ret
    move_snake_loop:
        # update corresponding coordinate
        from-mba
        to-mdc
        from-reg 0 # put ra to acc to check if need to subtract 1 from rb
        dec*-reg 0 # decrement ra
        beqz is_rb_zero_move # if ra is zero, check if rb is also zero
        dec_rdrc_move:
            from-reg 2 # put rc to acc to check if need to subtract 1 from rd
            dec*-reg 2 # # if ra is nonzero decrement rdrc
        beqz dec_rd_move # if rc is zero, decrement rd. note that rdrc will never be zero.
        b move_snake_base # if rc is nonzero before decrementing then go back to snake_base
        is_rb_zero_move:
            bnz-b dec_rb_move
            ret # if rb is also zero, then we can return to game loop
        dec_rb_move:
            dec*-reg 1
            b dec_rdrc_move
        dec_rd_move:
            dec*-reg 3
        b move_snake_base

draw_snake:
    rcrd 0x00
    from-mdc # acc = 0x00
    rcrd 0x27
    to-mdc # MEM[0x27] = length ng snake
    #store 0x00 sa temp registers: 0x32 (ra) 0x33(rb)
    rarb 0x32
    acc 0
    to-mba
    rarb 0x33
    to-mba

    Build_segment:
        # get current address na iddraw from 0x32 and 0x33
        rcrd 0x32 #acc = MEM[0x32] = current ra
        from-mdc
        rarb 0x26
        to-mba 

        rcrd 0x33
        from-mdc
        rarb 0x25
        to-mba

        Get_row:
            draw_snake_Compute_rowRA:
                rarb 0x26
                clr-cf
                acc 1
                add-mba
                to-mba
                bnez-cf draw_snake_Compute_rowRB
                b draw_snake_Done_Compute_row

            draw_snake_Compute_rowRB:
                rarb 0x25
                acc 1
                add-mba
                to-mba

            draw_snake_Done_Compute_row:
                rcrd 0x25
                from-mdc # acc = 1st nibble ng address ng segment (rb)
                to-reg 1

                rcrd 0x26
                from-mdc # acc = 2nd nibble ng address ng seg (ra)
                to-reg 0
                #atp, rb:ra should be the address of the snake segment ROW (0x01 to 0x24)
            # store the row to rc
            from-mba # acc  = row
            rarb 0x28
            to-mba # store the row muna sa MEM[0x28] kasi onti register xd

        Get_col:
            draw_snake_Compute_colRA:
                rarb 0x26
                clr-cf
                acc 1
                add-mba
                to-mba
                bnez-cf draw_snake_Compute_colRA
                b draw_snake_Done_Compute_col
            
            draw_snake_Compute_colRB:
                rarb 0x25
                acc 1
                add-mba
                to-mba

            draw_snake_Done_Compute_col:
                rcrd 0x25
                from-mdc # acc = 1st nibble ng address ng segment (rb)
                to-reg 1 # hi!!!?

                rcrd 0x26
                from-mdc # acc = 2nd nibble ng address ng seg (ra)
                to-reg 0
                #atp, rb:ra should be the address of the snake segment COL (0x01 to 0x24)
            from-mba # acc = col
            to-reg 4 # re = col by now plsss....
            # store current segment position address for next loop
            from-reg 0 # acc = ra
            rcrd 0x32
            to-mdc
            from-reg 1
            rcrd 0x33
            to-mdc
        
        rarb 0x28 # get the row from MEM[0x28]
        from-mba
        to-reg 2 # rc = row

        Draw_segment:
            # computing memory address given row, col
            # LED_addr = 192 + row*5 + (col//4)

            # input (assume na-load na yung row, col from memory):
            # rc = segment's row
            # re = segment's col
            

            # store c -> SCRATCH A and 0 -> scratch B
            acc 12
            rarb 0x25
            to-mba
            acc 0
            rarb 0x26
            to-mba #MEM[0x25] -> c ; MEM[0x26] -> 0

            #COMPUTING RA which is nasa MEM[0x26]
            clr-cf
            acc 5
            to-reg 3 # RA = counter for ilang beses mag-add (starting: 5)
            draw_segment_Compute_RA:
                rarb 0x26
                clr-cf
                from-reg 2 # acc = row
                add-mba # MEM[0x26] + row
                to-mba
                from-reg 2
                dec*-reg 3 # ra-=1
                bnez-cf draw_segment_Compute_RB
                bnz-d draw_segment_Compute_RA
                b Done_multiply

            draw_segment_Compute_RB:
                rarb 0x25
                acc 1
                add-mba
                to-mba
                bnz-d draw_segment_Compute_RA

            Done_multiply:
                from-reg 4
                rot-r
                rot-r
                and 3 #acc = 
                
            draw_segment_Compute_RA2:
                rarb 0x26
                add-mba 
                to-mba
                bnez-cf draw_segment_Compute_RB2
                b Done_finally
            
            draw_segment_Compute_RB2:
                rarb 0x25
                acc 1
                add-mba
                to-mba

            Done_finally:
                rcrd 0x25
                from-mdc #acc = MEM[0x25] -> rb dapat
                to-reg 1 

                rcrd 0x26
                from-mdc #acc = MEM[0x26] -> ra
                to-reg 0
            # ATP DAPAT RB:RA = LED ADDRESS NA
            # store rb sa MEM[0x29]
            rcrd 0x29 
            from-reg 1
            to-mdc

            # store ra sa MEM[0x30]
            rcrd 0x30
            from-reg 0
            to-mdc

            from-reg 4 # acc = col
            and 3 # acc = col and 3
            rcrd 0x31
            to-mdc 


            # load col and 3 sa acc
            rcrd 0x31
            from-mdc # acc = col and 3

            ZerothIsZero:
                b-bit 0 ZerothIsOne
                aOnethIsZero: #00
                    b-bit 1 aOnethIsOne
                    acc 1
                    b AfterBBit

                aOnethIsOne: #10
                    acc 4
                    b AfterBBit

            ZerothIsOne:
                bOnethIsZero: #01
                    b-bit 1 bOnethIsOne
                    acc 2
                    b AfterBBit

                bOnethIsOne: #11
                    acc 8
                    b AfterBBit
            
            AfterBBit:
                or*-mba # update the bits of the led, dapat iilaw na yung dapat iilaw


        rcrd 0x27
        dec*-mdc # subtract 1 to the length hanggang maging 0
        from-mdc 
        bnez Build_segment # if di pa 0, continue building
    ret
    # shutdown

    clear_tail:
    # first copmute the memory address of the tail 
    # load the tail's row, then store it to rc
    rcrd 0xfe
    from-mdc
    to-reg 1 # MEM[0xfe] -> rb
    rcrd 0xff
    from-mdc
    to-reg 0 # MEM[0xff] -> ra
    # ATP, RB:RA should hold the memory for the tail's row
    from-mba
    rcrd 0xfb
    to-mdc # 0xfb = row of tail

    # load the tail's col, thenn store it to re
    rcrd 0xfc
    from-mdc
    to-reg 1 # MEM[0xfc] -> rb
    rcrd 0xfd
    from-mdc
    to-reg 0 
    # ATP, RB:RA should hold the memory for the tail's col
    from-mba
    to-reg 4 # re = col of tail
    #load the row
    rarb 0xfb
    from-mba
    to-reg 2 # rc = row of tail

    # computing memory address given row, col
    # LED_addr = 192 + row*5 + (col//4)

    # input (assume na-load na yung row, col from memory):
    # rc = segment's row
    # re = segment's col

    # store c -> SCRATCH A and 0 -> scratch B
    acc 12
    rarb 0x25
    to-mba
    acc 0
    rarb 0x26
    to-mba #MEM[0x25] -> c ; MEM[0x26] -> 0

    #COMPUTING RA which is nasa MEM[0x26]
    clr-cf
    acc 5
    to-reg 3 # RA = counter for ilang beses mag-add (starting: 5)
    clear_segment_Compute_RA:
        rarb 0x26
        clr-cf
        from-reg 2 # acc = row
        add-mba # MEM[0x26] + row
        to-mba
        from-reg 2
        dec*-reg 3 # ra-=1
        bnez-cf clear_segment_Compute_RB
        bnz-d clear_segment_Compute_RA
        b clear_Done_multiply

    clear_segment_Compute_RB:
        rarb 0x25
        acc 1
        add-mba
        to-mba
        bnz-d clear_segment_Compute_RA

    clear_Done_multiply:
        from-reg 4
        rot-r
        rot-r
        and 3 #acc = 
        
    clear_segment_Compute_RA2:
        rarb 0x26
        add-mba 
        to-mba
        bnez-cf clear_segment_Compute_RB2
        b clear_Done_finally
    
    clear_segment_Compute_RB2:
        rarb 0x25
        acc 1
        add-mba
        to-mba

    clear_Done_finally:
        rcrd 0x25
        from-mdc #acc = MEM[0x25] -> rb dapat
        to-reg 1 

        rcrd 0x26
        from-mdc #acc = MEM[0x26] -> ra
        to-reg 0
    # ATP DAPAT RB:RA = LED ADDRESS NA
    # store rb sa MEM[0x29]
    rcrd 0x29 
    from-reg 1
    to-mdc

    # store ra sa MEM[0x30]
    rcrd 0x30
    from-reg 0
    to-mdc

    from-reg 4 # acc = col
    and 3 # acc = col and 3
    rcrd 0x31
    to-mdc 

    # MASKING, which bit needs to be lit up
    # load col and 3 sa acc
    rcrd 0x31
    from-mdc # acc = col and 3

    # 11 -> 1110 14
    # 10 -> 1101 13
    # 01 -> 1011 11
    # 00 -> 0111 7

    clear_ZerothIsZero:
        b-bit 0 clear_ZerothIsOne
        cler_aOnethIsZero: #00
            b-bit 1 cler_aOnethIsOne
            acc 14
            b clear_AfterBBit

        cler_aOnethIsOne: #10
            acc 11
            b clear_AfterBBit

    clear_ZerothIsOne:
        clear_bOnethIsZero: #01
            b-bit 1 clear_bOnethIsOne
            acc 13
            b clear_AfterBBit

        clear_bOnethIsOne: #11
            acc 7
            b clear_AfterBBit
    
    clear_AfterBBit:

        and*-mba # update the bits of the led, dapat mamamatay na yung ilaw
    
    ret

bounds_collision:
    b restart

map_to_led:
    
is_in_bounds:

restart:
    b init

draw_divider:
    acc 1
    rarb 195
    to-mba
    rarb 200
    to-mba
    rarb 205
    to-mba
    rarb 210
    to-mba
    rarb 215
    to-mba
    rarb 220
    to-mba
    rarb 225
    to-mba
    rarb 230
    to-mba
    rarb 235
    to-mba
    rarb 240
    to-mba
    ret

draw_0:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 231
    to-mba
    rarb 206
    to-mba
    acc 2
    rarb 226
    to-mba
    rarb 221
    to-mba
    rarb 216
    to-mba
    rarb 211
    to-mba
    ret

draw_1:
    acc 1
    rarb 206
    to-mba
    rarb 211
    to-mba
    rarb 216
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    ret

draw_2:
    acc 8
    rarb 205
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 2
    rarb 211
    to-mba
    ret

draw_3:
    acc 8
    rarb 205
    or*-mba
    rarb 215
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 2
    rarb 211
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_4:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    acc 2
    rarb 206
    to-mba
    rarb 211
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    acc 3
    rarb 216
    to-mba
    ret

draw_5:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 2
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_6:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 2
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_7:
    acc 8
    rarb 205
    or*-mba
    acc 3
    rarb 206
    to-mba
    acc 2
    rarb 211
    to-mba
    rarb 216
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    ret

draw_8:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 2
    rarb 211
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_9:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    acc 3
    rarb 206
    to-mba
    rarb 216
    to-mba
    acc 2
    rarb 211
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    ret

draw_10:
    acc 4
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 7
    rarb 206
    to-mba
    rarb 231
    to-mba
    acc 5
    rarb 211
    to-mba
    rarb 216
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_11:
    acc 8
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 2
    rarb 206
    to-mba
    rarb 211
    to-mba
    rarb 216
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    ret

draw_12:
    acc 4
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 7
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 4
    rarb 211
    to-mba
    acc 1
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_13:
    acc 4
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 7
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 4
    rarb 211
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

draw_14:
    acc 4
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 5
    rarb 206
    to-mba
    rarb 211
    to-mba
    acc 7
    rarb 216
    to-mba
    acc 4
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    ret

draw_15:
    acc 4
    rarb 205
    or*-mba
    rarb 210
    or*-mba
    rarb 215
    or*-mba
    rarb 220
    or*-mba
    rarb 225
    or*-mba
    rarb 230
    or*-mba
    acc 7
    rarb 206
    to-mba
    rarb 216
    to-mba
    rarb 231
    to-mba
    acc 1
    rarb 211
    to-mba
    acc 4
    rarb 221
    to-mba
    rarb 226
    to-mba
    ret

clear_scoreboard:
    b draw_divider
    acc 0
    rarb 196
    to-mba
    rarb 201
    to-mba
    rarb 206
    to-mba
    rarb 211
    to-mba
    rarb 216
    to-mba
    rarb 221
    to-mba
    rarb 226
    to-mba
    rarb 231
    to-mba
    rarb 236
    to-mba
    rarb 241
    to-mba
    ret