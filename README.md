# CS 21 24.2 Project: Arch242
# Project Details
This project consists of an Pyxel-based assembler and emulator, snake game using the Arch242 ISA, and a Logisim-based  hardware implementation based on a given custom architeture, Arch 242.

- Contributions:
    - `Lim, Eliana Mari P.`: emulator (part a2), snake game (part a3)
    - `Ricaforte, Jarelle Gail E.`: snake game (part a3), hardware implementation (part b)
    - `Sacramento, Gabrielle Denise S.`: hardware implementation (part b)
    - `Sim, Charlize S.`: assembler (part a1), snake game(part a3)

# Setup
- Make sure to have at least Python 3.10, Pyxel, and Logisim Evolution installed.

To access the files in this repository:
1. Clone this repository or download the ZIP file.
2. Extract files to desired location

# Part A1: Arch-242 assembler
## How to Run
From the root directory, run the following:

```sh
python parta1/assembler.py <input_file.asm> <bin | hex>
```
or 

```sh
python3 parta1/assembler.py <input_file.asm> <bin | hex>
```

## Additional Features
### Exception Handling
The assembler provides comprehensive error reporting with line-specific feedback:

- Line-specific errors: Shows exact line number where errors occur
- Range validation: Validates immediate values and register numbers
- Clear error messages: Descriptive messages help identify issues quickly

Example error output:
```
Error at line 15: Invalid register number: 7

Error at line 23: Immediate value too large for add: 20

Error at line 31: Unknown instruction: invalidop
```

### Label Support
Labels can be defined and referenced throughout your assembly code:
- Label definition: Use `label_name:` to define a label at the current address
- Label referencing: Use the label name in branch and call instructions
- Automatic address resolution: Labels are automatically resolved to their memory addresses during assembly
- Forward references: Labels can be referenced before they are defined

Example usage:
```
main_loop:
    from-ioa
    beqz no_input
    b process_input

no_input:
    nop
    b main_loop

process_input:
    call handle_direction
    b main_loop
```

### Comment Support
The assembler supports single-line comments for code documentation:

- Comment syntax: Use `#` to start a comment that continues to the end of the line
- Inline comments: Comments can be placed after instructions on the same line
- Full-line comments: Entire lines can be comments for documentation
- Automatic stripping: Comments are automatically removed during assembly and don't affect the generated code

Example usage:
```
# Main program entry point
main_loop:
    from-ioa          # Read input from IOA
    beqz no_input     # Branch if no input received
    b process_input   # Jump to input processing

# Handle case when no input is available
no_input:
    nop              # Do nothing
    b main_loop      # Return to main loop
```
### Hexadecimal Immediate Values
The assembler supports both decimal and hexadecimal immediate values:

- Hex format: Use `0x` prefix for hexadecimal values (e.g., `0xFF`, `0x20`)
- Case insensitive: Both uppercase and lowercase hex digits are supported (`0xFF` or `0xff`)
- Mixed usage: You can mix decimal and hex values in the same program
- Range validation: Hex values are validated against instruction-specific limits

Example usage:
```
acc 0xF          # Load 15 into accumulator
rarb 0x20        # Set RA/RB to address 32
add 0xA          # Add 10 to accumulator
```
## Some Notes/Assumptions
- Since the project specifications did not specify which memory to place the `.byte` directive, the contributors assumed that it is stored in the instruction memory and is treated as instructions. This means `.byte` values are placed alongside other instructions in the program memory and will increment the program counter accordingly.


# Part A2: Pyxel-based Arch-242 emulator
## How to Run
From the root directory, run the following:

```sh
python parta2/arch242.py <input_file.asm>
```
or
```sh
python3 parta2/arch242.py <input_file.asm> 
```

## Additional Features
- Custom LED colors for snake game
- Debugging Features
    - How to use
        - By default, this feature is off.
        - set `self.debugging = True` in `emulator.py`
            ```python
            class Arch242Emulator:
                def __init__(self, instr_hex: list[str]):
                    ...
                    self.debugging = True
                    ...
            ````
    - When a program is ran into the emulator, it does the following:
        - If a folder `parta2/logs`, does not exist yet. It initializes the folder.
        - It creates a file `parta2/logs/debugging.txt` with the following contents for every instruction ran by the program by default:
            - Current program counter
            - Instruction ran
            - Values at different registers
        - To see specific values at different parts of the emulator, it can be added into the following portion of the code:
            ```python
            class Arch242Emulator:
                def update(self):
                    ...
                    if self.debugging:
                        with open("logs/debugging.txt", 'a') as f:
                            ...
                            f.write(f"<value you would like to track>")
                            f.write(f"\n")
                            ...
                    ...
            ```
## Some Notes/Assumptions
- Since addressability was not specified, the instruction memory and data memory were assumed to be byte-addressable memory.
- The LED matrix is a 10-row by 20-column matrix. It follows the mapping table in the project specifications.
- `beqz <imm>` branches when ACC is zero, and `bnez <imm>` branches when ACC is nonzero.
# Part A3: Snake Game assembly code
## How to Run
To assemble the code into machine code,
- From the root directory, run the following:
    ```sh
    python parta1/assembler.py <input_file.asm> <bin / hex>
    ```
    or 

    ```sh
    python3 parta1/assembler.py <input_file.asm> <bin / hex>
    ```

To run the code using the emulator (play the snake game),
- From the root directory, run the following:
    ```sh
    python parta2/arch242.py parta3/snake.asm
    ```
    or
    ```sh
    python3 parta2/arch242.py parta3/snake.asm
    ```

Note: The emulator uses the assembler to assemble into a list of hex strings.

## Some Notes/Assumptions
- When restarting the game, the snake respawns and follows the most recent direction.
- Using a direction that goes toward the snake will result into a self collision, e.g. when the snake is moving to the right, pressing the left key will cause your snake to die and the game will restart.

# Part B: Logisim-based Arch-242 implementation
## How to Run

1. Open `Arch242.circ` in Logisim Evolution.
2. Click the **InstrMem** Circuit 
    1. Right Click the ROM 
    2. **Load Image → Hex**
    3. Select your `.hex` file
    4. Start the simulation.

A `.hex` file can be made from your `.asm` file containing your Arch242 Assembly Code using the assembler. Run the following in the terminal:
```sh
python parta1/assembler.py <input_file.asm> hex
```
After running, a `.hex` file will be created on the same location as your `.asm` file, which you can load into the Logisim-based hardware.

## Some Notes/Assumptions
- Since addressability was not specified, the instruction memory was assumed to be byte-addressable and data memory was assumed to be nibble-addressable memory.
- `beqz <imm>` branches when ACC is zero, and `bnez <imm>` branches when ACC is nonzero.
