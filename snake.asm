init:
    call clear_screen
    call init_snake
    call draw_divider
    call draw_score
    call draw_food
    call draw_snake

game_loop:
    handle_input:
        from-ioa
        to-reg 4 # store value of ioa to RE for retrieval
        # check if not pressed
        and 15
        bnez jump
        call continue_direction
        jump:
        call move_snake
        call check_direction
        call after_move
        call draw_food
        call draw_score
        # call check_collision
        # call check_eat_food
        b game_loop


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
        ret

    move_up:
        # update head
        rarb 1
        from-mba
        beqz bounds_collision    # if head row is at 0 and we go up pa, collision!
        
        #checking of food collision:
        # head row == food row AND head col == food col -> collide
        # food row colflag: 0x38
        rarb 0x38
        rcrd 0x01 # head row
        from-mdc
        to-mba 
        rcrd 0xf4 # food row
        from-mdc # acc = food row
        xor*-mba 

        # food col colflag: 0x39
        rarb 0x39
        rcrd 0x02 # head col
        from-mdc
        to-mba 
        rcrd 0xf5 # food col
        from-mdc # acc = food col
        xor*-mba 

        # food collision flag: 0x37
        rarb 0x37
        rcrd 0x38
        from-mdc
        to-mba # 0x37 == food row colflag
        rcrd 0x39
        from-mdc # acc == food col colflag
        xor*-mba
        from-mba

        rarb 1
        dec*-mba # head row -= 1

        
        # 0x37 == 1 -> food collision
        beqz food_collision
        b after_food_collision

    move_down:
        # update head
        rarb 1
        from-mba
        sub 9  # ACC = old head row - 9
        beqz bounds_collision   # if ACC = 0, then old head row was 9, so if we go down pa, collision!
        
        #checking of food collision:
        # head row == food row AND head col == food col -> collide
        # food row colflag: 0x38
        rarb 0x38
        rcrd 0x01 # head row
        from-mdc
        to-mba 
        rcrd 0xf4 # food row
        from-mdc # acc = food row
        xor*-mba 

        # food col colflag: 0x39
        rarb 0x39
        rcrd 0x02 # head col
        from-mdc
        to-mba 
        rcrd 0xf5 # food col
        from-mdc # acc = food col
        xor*-mba 

        # food collision flag: 0x37
        rarb 0x37
        rcrd 0x38
        from-mdc
        to-mba # 0x37 == food row colflag
        rcrd 0x39
        from-mdc # acc == food col colflag
        xor*-mba
        from-mba

        rarb 1
        inc*-mba # old head row += 1

        
        # 0x37 == 1 -> food collision
        beqz food_collision
        b after_food_collision

    move_left:
        # update head
        rarb 2
        from-mba
        beqz bounds_collision    # if head col is at 0 xor we go left pa, collision!

        #checking of food collision:
        # head row == food row AND head col == food col -> collide
        # food row colflag: 0x38
        rarb 0x38
        rcrd 0x01 # head row
        from-mdc
        to-mba 
        rcrd 0xf4 # food row
        from-mdc # acc = food row
        xor*-mba 

        # food col colflag: 0x39
        rarb 0x39
        rcrd 0x02 # head col
        from-mdc
        to-mba 
        rcrd 0xf5 # food col
        from-mdc # acc = food col
        xor*-mba 

        # food collision flag: 0x37
        rarb 0x37
        rcrd 0x38
        from-mdc
        to-mba # 0x37 == food row colflag
        rcrd 0x39
        from-mdc # acc == food col colflag
        xor*-mba
        from-mba
        
        rarb 2
        dec*-mba # old head col -= 1
        # 0x37 == 1 -> food collision
        beqz food_collision

        b after_food_collision

    move_right:
        # update head
        rarb 2
        from-mba
        sub 11  # ACC = old head row - 11
        beqz bounds_collision   # if ACC = 0, then old head row col 11, so if we go right pa, collision!

        #checking of food collision:
        # head row == food row AND head col == food col -> collide
        # food row colflag: 0x38
        
        rarb 0x38
        rcrd 0x01 # head row
        from-mdc
        to-mba 
        rcrd 0xf4 # food row
        from-mdc # acc = food row
        xor*-mba 

        # food col colflag: 0x39
        rarb 0x39
        rcrd 0x02 # head col
        from-mdc
        to-mba 
        rcrd 0xf5 # food col
        from-mdc # acc = food col
        xor*-mba 

        # food collision flag: 0x37
        rarb 0x37
        rcrd 0x38
        from-mdc
        to-mba # 0x37 == food row colflag
        rcrd 0x39
        from-mdc # acc == food col colflag
        xor*-mba
        from-mba # acc == food col 

        rarb 2
        inc*-mba
        # 0x37 == 0 -> food collision
        beqz food_collision

        # old head col += 1
        b after_food_collision

after_food_collision:
    acc 1
    rarb 0x37
    to-mba
    rarb 0x38
    to-mba
    rarb 0x39
    to-mba
    ret 

    move_snake:
        # atp, current rb:ra is 0x02 -> head col
        # we want to update the tail coord

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

    # ---- END OF HANDLE INPUT/MOVVE----


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

    # segment 2:
    rarb 3
    rcrd 4
    acc 5
    to-mba
    acc 2
    to-mdc

    # segment 3:
    rarb 5
    rcrd 6
    acc 5
    to-mba
    acc 1
    to-mdc
    

    # NULL (where the tail pointer is pointed):
    rarb 7
    # store 5 to tail row pointer
    from-reg 0
    rcrd 0xff
    to-mdc # store ra of row -> 0xff
    from-reg 1
    rcrd 0xfe
    to-mdc # store rb of row -> 0xfe
    # so, current addr of tail row: MEM[0xfe]:MEM[0xff]

    # next, store 6 to tail col pointer
    rcrd 8
    from-reg 2
    rarb 0xfd
    to-mba # store ra of col -> 0xfd
    from-reg 3
    rarb 0xfc
    to-mba # store rb of col -> 0xfc
    # current addr of tail col: MEM[0xfc]:MEM[0xfd]

    #set the position of the NULL
    rarb 7
    acc 5
    to-mba
    rcrd 8
    acc 0
    to-mdc

    # set initial direction
    rarb 242
    acc 8
    to-mba

    # set initial score
    rarb 243
    acc 0
    to-mba

    # set initial food locatino
    rarb 244
    acc 5
    to-mba
    rarb 245
    acc 6
    to-mba

    # set initial food col flag to 1
    rarb 0x37
    acc 1
    to-mba
    ret

clear_screen:
    rarb 0xC0 # first LED address, let RA be 0x0 and RB be 0xC

    clear_screen_loop:
        acc 0
        to-mba
        inc*-reg 0
        from-reg 0  # acc = RA
        sub 15      # check if RA = 0xF for incrementing RB
        beqz increment_rb
        b clear_screen_loop     # otherwise continue clearing

    increment_rb:
        inc*-reg 1
        from-reg 1  # acc = RB
        sub 15      # check if RB = 0xF for stopping
        beqz clear_screen_done
        b clear_screen_loop

    clear_screen_done:
        ret

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
    
after_move: # draw new head and clear old tail
    # HEAD:
    # by now, head is now updated dapat cc: handle_input
    # load the new head's row, then store it to rc
    rarb 0x01
    from-mba #acc = head row
    to-reg 2 # rc = new head's row
    # load the new head's col, store to re
    rarb 0x02
    from-mba #acc = head col
    to-reg 4 # re = new head's col

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
    afterm_draw_segment_Compute_RA:
        rarb 0x26
        clr-cf
        from-reg 2 # acc = row
        add-mba # MEM[0x26] + row
        to-mba
        from-reg 2
        dec*-reg 3 # ra-=1
        bnez-cf afterm_draw_segment_Compute_RB
        bnz-d afterm_draw_segment_Compute_RA
        b afterm_Done_multiply

    afterm_draw_segment_Compute_RB:
        rarb 0x25
        acc 1
        add-mba
        to-mba
        bnz-d afterm_draw_segment_Compute_RA

    afterm_Done_multiply:
        from-reg 4
        rot-r
        rot-r
        and 3 #acc = 
        
    afterm_draw_segment_Compute_RA2:
        rarb 0x26
        add-mba 
        to-mba
        bnez-cf afterm_draw_segment_Compute_RB2
        b afterm_Done_finally
    
    afterm_draw_segment_Compute_RB2:
        rarb 0x25
        acc 1
        add-mba
        to-mba

    afterm_Done_finally:
        rcrd 0x25
        from-mdc #acc = MEM[0x25] -> rb dapat
        to-reg 1 

        rcrd 0x26
        from-mdc #acc = MEM[0x26] -> ra
        to-reg 0
    # ATP DAPAT RB:RA = LED ADDRESS NA
    # store rb sa MEM[0x35]
    rcrd 0x35
    from-reg 1
    to-mdc
    

    # store ra sa MEM[0x36]
    rcrd 0x36
    from-reg 0
    to-mdc
    # address is in 0x35:0x36

    from-reg 4 # acc = col
    and 3 # acc = col and 3
    rcrd 0x31
    to-mdc 


    # load col and 3 sa acc
    rcrd 0x31
    from-mdc # acc = col and 3

    afterm_ZerothIsZero:
        b-bit 0 afterm_ZerothIsOne
        afterm_aOnethIsZero: #00
            b-bit 1 afterm_aOnethIsOne
            acc 1
            b afterm_AfterBBit

        afterm_aOnethIsOne: #10
            acc 4
            b afterm_AfterBBit

    afterm_ZerothIsOne:
        afterm_bOnethIsZero: #01
            b-bit 1 afterm_bOnethIsOne
            acc 2
            b afterm_AfterBBit

        afterm_bOnethIsOne: #11
            acc 8
            b afterm_AfterBBit
    
    
    
    afterm_AfterBBit:
    rarb 0x34
    to-mba

    # NOW COMPUTE TAIL
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
    
    # NOW CLEAR THE TAIL
    clear_AfterBBit:
        and*-mba # update the bits of the led, dapat mamamatay na yung ilaw
    
    #now draw the new head
    #load the head address from 0x35 and 0x36
    rarb 0x35
    from-mba
    to-reg 1
    rcrd 0x36
    from-mdc
    to-reg 0

    # load acc offset from 0x34
    rcrd 0x34
    from-mdc
    or*-mba # update the bits of the led, dapat iilaw na yung dapat iilaw
    ret


food_collision:
    rarb 0xf3
    inc*-mba
    
    add_segment:
        # +1 length
        rarb 0x00
        inc*-mba
        
        # load the NULL col
        rarb 0xfd
        from-mba
        to-reg 0
        rcrd 0xfc
        from-mdc
        to-reg 1
        # store NULL col to re
        from-mba
        to-reg 4

        # draw the current NULL pointer
        # load the NULL row 
        rarb 0xff
        from-mba
        to-reg 0
        rcrd 0xfe
        from-mdc
        to-reg 1
        # store NULL row to rc
        from-mba
        to-reg 2

        # DRAW CURRENT NULL
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
        add_segment_Compute_RA:
            rarb 0x26
            clr-cf
            from-reg 2 # acc = row
            add-mba # MEM[0x26] + row
            to-mba
            from-reg 2
            dec*-reg 3 # ra-=1
            bnez-cf add_segment_Compute_RB
            bnz-d add_segment_Compute_RA
            b add_Done_multiply

        add_segment_Compute_RB:
            rarb 0x25
            acc 1
            add-mba
            to-mba
            bnz-d add_segment_Compute_RA

        add_Done_multiply:
            from-reg 4
            rot-r
            rot-r
            and 3 #acc = 
            
        add_segment_Compute_RA2:
            rarb 0x26
            add-mba 
            to-mba
            bnez-cf add_segment_Compute_RB2
            b add_Done_finally
        
        add_segment_Compute_RB2:
            rarb 0x25
            acc 1
            add-mba
            to-mba

        add_Done_finally:
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

        add_ZerothIsZero:
            b-bit 0 add_ZerothIsOne
            add_aOnethIsZero: #00
                b-bit 1 add_aOnethIsOne
                acc 1
                b add_AfterBBit

            add_aOnethIsOne: #10
                acc 4
                b add_AfterBBit

        add_ZerothIsOne:
            add_bOnethIsZero: #01
                b-bit 1 add_bOnethIsOne
                acc 2
                b add_AfterBBit

            add_bOnethIsOne: #11
                acc 8
                b add_AfterBBit
        
        add_AfterBBit:

            or*-mba # update the bits of the led, dapat iilaw na yung dapat iilaw

        # ---------------------------------------------------
        # move the NULL pointer to the next segment.
        NULL_Get_row:
            NULL_Compute_rowRA: # + 1 to the address of NULL COL
                rarb 0xfd
                clr-cf
                acc 1
                add-mba
                rcrd 0xff
                to-mdc
                bnez-cf NULL_Compute_rowRB
                b NULL_Get_col

            NULL_Compute_rowRB:
                rarb 0xfc
                acc 1
                add-mba
                rcrd 0xfe
                to-mdc
            #atp, MEM[0xfe:0xff] shoud be the address of the new NULL ROW

            NULL_Done_Compute_row:


        NULL_Get_col:
            NULL_Compute_colRA: # +1 to the address of the new NULL ROW
                rarb 0xff
                clr-cf
                acc 1
                add-mba
                rcrd 0xfd
                to-mdc
                bnez-cf NULL_Compute_colRA
                b NULL_Done_Compute_col
            
            NULL_Compute_colRB:
                rarb 0xfe
                acc 1
                add-mba
                rcrd 0xfc
                to-mdc

            NULL_Done_Compute_col:

    # --------------------------
    
    b after_food_collision


bounds_collision:
    b restart

restart:
    b init

draw_food:
    rarb 244 # food ROW address
    from-mba
    to-reg 2
    rarb 245 # food COL address
    from-mba
    to-reg 4

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
    draw_food_Compute_RA:
        rarb 0x26
        clr-cf
        from-reg 2 # acc = row
        add-mba # MEM[0x26] + row
        to-mba
        from-reg 2
        dec*-reg 3 # ra-=1
        bnez-cf draw_food_Compute_RB
        bnz-d draw_food_Compute_RA
        b Done_multiply_food

    draw_food_Compute_RB:
        rarb 0x25
        acc 1
        add-mba
        to-mba
        bnz-d draw_food_Compute_RA

    Done_multiply_food:
        from-reg 4
        rot-r
        rot-r
        and 3 #acc = 
        
    draw_food_Compute_RA2:
        rarb 0x26
        add-mba 
        to-mba
        bnez-cf draw_food_Compute_RB2
        b finally_done
    
    draw_food_Compute_RB2:
        rarb 0x25
        acc 1
        add-mba
        to-mba

    finally_done:
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

    food_ZerothIsZero:
        b-bit 0 food_ZerothIsOne
        food_aOnethIsZero: #00
            b-bit 1 food_aOnethIsOne
            acc 1
            b food_AfterBBit

        food_aOnethIsOne: #10
            acc 4
            b food_AfterBBit

    food_ZerothIsOne:
        food_bOnethIsZero: #01
            b-bit 1 food_bOnethIsOne
            acc 2
            b food_AfterBBit

        food_bOnethIsOne: #11
            acc 8
            b food_AfterBBit
    
    food_AfterBBit:
        or*-mba # update the bits of the led, dapat iilaw na yung dapat iilaw

    ret

draw_score:
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
    clear_scoreboard:
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

    rarb 243
    from-mba
    to-reg 4
    xor 0
    beqz draw_0
    from-reg 4
    xor 1
    beqz draw_1
    from-reg 4
    xor 2
    beqz draw_2
    from-reg 4
    xor 3
    beqz draw_3
    from-reg 4
    xor 4
    beqz draw_4
    from-reg 4
    xor 5
    beqz draw_5
    from-reg 4
    xor 6
    beqz draw_6
    from-reg 4
    xor 7
    beqz draw_7
    from-reg 4
    xor 8
    beqz draw_8
    from-reg 4
    xor 9
    beqz draw_9
    from-reg 4
    xor 10
    beqz draw_10
    from-reg 4
    xor 11
    beqz draw_11
    from-reg 4
    xor 12
    beqz draw_12
    from-reg 4
    xor 13
    beqz draw_13
    from-reg 4
    xor 14
    beqz draw_14
    from-reg 4
    xor 15
    beqz draw_15

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