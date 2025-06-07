init:
    call init_snake

game_loop:
    call handle_input
    call move_snake
    call check_collision
    call check_eat_food
    call draw_snake
    b game_loop

init_snake:
    # store address of null terminator
    acc 4
    rarb 0
    to-mba
    
    # store address of each part of snake (row, col)
    rarb 1
    rcrd 2
    acc 0
    to-mba
    to-mdc
    rcrd 4
    acc 1
    to-mdc
    rcrd 6
    acc 2
    to-mdc
    ret

handle_input:
    from-ioa
    ret

move_snake:

check_collision:

check_eat_food:

draw_snake:
    rcrd 0x00
    from-mdc # acc = 0x00
    rcrd 0x27
    to-mdc # MEM[0x27] = length ng snake

    Build_segment:
        Get_row:
            draw_snake_Compute_rowRA:
                rarb 0x26
                clr-cf
                inc*-mba
                bnez-cf draw_snake_Compute_rowRB
                b draw_snake_Done_Compute_row

            draw_snake_Compute_rowRB:
                rarb 0x25
                inc*-mba

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
                inc*-mba
                bnez-cf draw_snake_Compute_colRA
                b draw_snake_Done_Compute_col
            
            draw_snake_Compute_colRB:
                rarb 0x25
                inc*-mba

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
        
        rarb 0x28 # get the row from MEM[0x28]
        from-mba
        to-reg 2 # rc = row

        call draw_segment
        rcrd 0x27
        dec*-mdc # subtract 1 to the length hanggang maging 0
        from-mdc # acc = length-1
        beqz Build_segment # if di pa 0, continue building
    
    shutdown


draw_segment: #draws one segment
    # computing memory address given row, col
    # LED_addr = 192 + row*5 + (col//4)
    # mask = 1 << (col % 4)

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
        inc*-mba
        bnz-d draw_segment_Compute_RA

    Done_multiply:
        from-reg 4
        rot-r
        rot-r
        and 12 #acc = 
        
    draw_segment_Compute_RA2:
        rarb 0x26
        add-mba 
        to-mba
        bnez-cf draw_segment_Compute_RB2
        b Done_finally
    
    draw_segment_Compute_RB2:
        rarb 0x25
        inc*-mba

    Done_finally:
        rcrd 0x25
        from-mdc #acc = MEM[0x25] -> rb dapat
        to-reg 1 

        rcrd 0x26
        from-mdc #acc = MEM[0x26] -> ra
        to-reg 0
    ret
    # ATP DAPAT RB:RA = LED ADDRESS NA


map_to_led:
    
is_in_bounds:

