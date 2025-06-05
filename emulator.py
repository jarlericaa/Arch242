import sys
import pyxel
from constants import *

class Arch242Emulator:
    def __init__(self, instr_hex: list[int]):
        if len(instr_hex) > 2**16:
            sys.exit("Instructions do not fit the memory")
        
        self.pc = 0

        self.instr_mem = instr_hex # 16-bit wide
        self.data_mem = bytearray(256) # 8-bit wide

        self.reg = [0] * 5 # 4-bit wide
        self.acc = 0 # 4-bit wide
        self.cf = 0 # 1-bit register
        self.temp = 0 # 16-bit register
        self.ioa = 0 # 4-bit register

        self.running = True
        self.led_display_base = 192
        pyxel.init(80, 160, title="Arch242 Emulator", fps=60)
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.running:
            self.handle_input()
            self.process_instruction(self.instr_mem[self.pc])

    def draw(self):
        pyxel.cls(0)
        for addr in range(192, 242):
            val = self.data_mem[addr] & 0x0F
            row = (addr - 192) // 2
            for bit in range(4):
                col = ((addr - 192) * 4 + bit) % 20
                if val & (1 << bit):
                    pyxel.rect(col * 5, row * 5, 5, 5, 11)

    def handle_input(self):
        if pyxel.btn(pyxel.KEY_UP):
            self.ioa = 1
        elif pyxel.btn(pyxel.KEY_DOWN):
            self.ioa = 2
        elif pyxel.btn(pyxel.KEY_LEFT):
            self.ioa = 3
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.ioa = 4
        else:
            self.ioa = 0

    def process_instruction(self, instr: int):
        pass



if __name__ == "__main__":
    pass