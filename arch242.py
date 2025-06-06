import sys
from assembler import Arch242Assembler
import emulator as emu

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 arch242.py input.asm")

    asm_path = sys.argv[1]
    asm_assembler = Arch242Assembler()
    instr_hex = asm_assembler.assemble(asm_path, "hex")

    emu.Arch242Emulator(instr_hex)

if __name__ == "__main__":
    main()