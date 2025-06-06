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
    # while not yet equal to tail, process snake part
    rarb 2
    from-mba

    rcrd 3
    from-mdc
    may address ka na nung head sa acc
    so kailangan ilagay sa registers yung address na yun para maaccess yung data sa memory na yun
    Set ACC to MEM[RB:RA]
    map ACC to LED
    increment RBRA
        kapag 
    if xor is zero, after_draw_snake

after_draw_snake:
    ret

map_to_led:
    
