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

class Arch242ISA:
    def init(self, emulator: Arch242Emulator):
        self.emu = emulator

    def rotr(self):
        self.emu.acc = ((self.emu.acc >> 1) | ((self.emu.acc & 0x01) << 3)) & 0xF
        self.emu.pc += 1

    def rotl(self):
        self.emu.acc = ((self.emu.acc << 1) | ((self.emu.acc >> 3) & 0x1)) & 0xF
        self.emu.pc += 1

    def rotrc(self):
        temp = self.emu.cf
        self.emu.cf = self.emu.acc & 0x01
        self.emu.acc = (self.emu.acc >> 1) | (temp << 3) & 0xF
        self.emu.pc += 1

    def rotlc(self):
        temp = self.emu.cf
        self.emu.cf = self.emu.acc >> 3 & 0x01
        self.emu.acc = ((self.emu.acc << 1) | temp) & 0xF
        self.emu.pc += 1

    def frommba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = self.emu.data_mem[addr] & 0x0F
        self.emu.pc += 1

    def tomba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] = self.emu.acc
        self.emu.pc += 1

    def frommdc(self):
        addr = self.emu.reg[3] << 4 | self.emu.reg[2]
        self.emu.acc = self.emu.data_mem[addr] & 0x0F
        self.emu.pc += 1

    def tomdc(self):
        addr = self.emu.reg[3] << 4 | self.emu.reg[2]
        self.emu.data_mem[addr] = self.emu.acc
        self.emu.pc += 1

    def addcmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc += self.emu.data_mem[addr] + self.emu.cf
        self.emu.cf = 1 if self.emu.acc & 0x0F else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1

    def addmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc += self.emu.data_mem[addr]
        self.emu.cf = 1 if self.emu.acc & 0x0F else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1

    def subcmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = self.emu.acc - self.emu.data_mem[addr] + self.emu.cf
        self.emu.cf = 1 if self.emu.acc < 0 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1

    def submba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = self.emu.acc - self.emu.data_mem[addr]
        self.emu.cf = 1 if self.emu.acc < 0 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1

    def incmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] += 1
        self.emu.pc += 1

    def decmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] -= 1
        self.emu.pc += 1

    def incmdc(self):
        addr = self.emu.reg[3] << 4 | self.emu.reg[2]
        self.emu.data_mem[addr] += 1
        self.emu.pc += 1

    def decmdc(self):
        addr = self.emu.reg[3] << 4 | self.emu.reg[2]
        self.emu.data_mem[addr] -= 1
        self.emu.pc += 1

    def increg(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        curr_reg = curr_instr & 0xE >> 1
        self.emu.reg[curr_reg] += 1
        self.emu.pc += 1

    def decreg(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        curr_reg = curr_instr & 0x0E >> 1
        self.emu.reg[curr_reg] -= 1
        self.emu.pc += 1

    def andba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = (self.emu.acc & self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1

    def xorba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = (self.emu.acc ^ self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1

    def orba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.acc = (self.emu.acc | self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1

    def andmba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.acc | self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1

    def xormba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] = self.emu.acc ^ self.emu.data_mem[addr]
        self.emu.pc += 1

    def ormba(self):
        addr = self.emu.reg[1] << 4 | self.emu.reg[0]
        self.emu.data_mem[addr] = self.emu.acc | self.emu.data_mem[addr]
        self.emu.pc += 1

    def toreg(self):
        curr_reg = (self.emu.instr_mem[self.emu.pc] & 0xe) >> 1
        self.emu.reg[curr_reg] = self.emu.acc
        self.emu.pc += 1

    def fromreg(self):
        curr_reg = (self.emu.instr_mem[self.emu.pc] & 0xe) >> 1
        self.emu.acc = self.emu.reg[curr_reg]
        self.emu.pc += 1

    def clrcf(self):
        self.emu.cf = 0
        self.emu.pc += 1

    def setcf(self):
        self.emu.cf = 1
        self.emu.pc += 1

    def ret(self):
        self.emu.pc = (self.emu.pc & 0xF000) | (self.emu.temp & 0x0FFF)
        self.temp = 0

    def fromioa(self):
        self.emu.acc = self.emu.ioa
        self.emu.pc += 1

    def inc(self):
        self.emu.acc += 1
        self.emu.pc += 1

    def bcd(self):
        if self.emu.acc >= 10 or self.emu.cf == 1:
            self.emu.acc += 6
            self.emu.acc &= 0xF
            self.emu.cf = 1
        self.emu.pc += 1

    def shutdown(self):
        pyxel.quit()

    def nop(self):
        pass

    def dec(self):
        self.emu.acc -= 1
        self.emu.pc += 1

    def addimm(self):
        self.emu.acc = self.emu.acc + (self.emu.instr_mem[self.emu.pc+1] & 0x0F)
        self.emu.pc += 2

    def subimm(self):
        self.emu.acc = self.emu.acc - (self.emu.instr_mem[self.emu.pc+1] & 0x0F)
        self.emu.pc += 2
    
    def andimm(self):
        self.emu.acc = self.emu.acc & (self.emu.instr_mem[self.emu.pc+1] & 0x0F)
        self.emu.pc += 2

    def xorimm(self):
        self.emu.acc = self.emu.acc ^ (self.emu.instr_mem[self.emu.pc+1] & 0x0F)
        self.emu.pc += 2

    def orimm(self):
        self.emu.acc = self.emu.acc | (self.emu.instr_mem[self.emu.pc+1] & 0x0F)
        self.emu.pc += 2

    def r4imm(self):
        self.emu.reg[4] = self.emu.instr_mem[self.emu.pc+1] & 0x0F
        self.emu.pc += 2

    def rarbimm(self):
        self.emu.reg[0] = self.emu.instr_mem[self.emu.pc] & 0x0F
        self.emu.reg[1] = self.emu.instr_mem[self.emu.pc+1] & 0x0F
        self.emu.pc += 2

    def rcrdimm(self):
        self.emu.reg[2] = self.emu.instr_mem[self.emu.pc] & 0x0F
        self.emu.reg[3] = self.emu.instr_mem[self.emu.pc+1] & 0x0F
        self.emu.pc += 2

    def accimm(self):
        self.emu.acc = self.emu.instr_mem[self.emu.pc] & 0x0F
        self.emu.pc += 1

    def branch(self):
        imm = ((self.emu.instr_mem[self.emu.pc] & 0x07) << 8) | self.emu.instr_mem[self.emu.pc+1]
        self.emu.pc = (self.emu.pc & 0xF800) | imm

    def bbitkimm(self):
        kk = (self.emu.instr_mem[self.emu.pc] & 0x18) >> 3
        accbitkk = (self.emu.acc >> kk) & 0x1
        if accbitkk == 1:
            self.branch()

    def bnzaimm(self):
        if self.emu.reg[0] != 0: # RA is nonzero
            self.branch()

    def bnzbimm(self):
        if self.emu.reg[1] != 0: # RB is nonzero
            self.branch()

    def beqzimm(self):
        if self.emu.acc == 0:
            self.branch()

    def bnezimm(self):
        if self.emu.acc != 0:
            self.branch()

    def beqzcfimm(self):
        if self.emu.cf == 0:
            self.branch()

    def bnezcfimm(self):
        if self.emu.cf != 0:
            self.branch()

    def bnzdimm(self):
        if self.emu.reg[3] != 0:
            self.branch()

    def bimm(self):
        imm = ((self.emu.instr_mem[self.emu.pc] & 0x0F) << 8) | self.emu.instr_mem[self.emu.pc+1]
        self.emu.pc = (self.emu.pc & 0xF000) | imm

    def callimm(self):
        self.emu.temp = self.emu.pc + 2
        self.bimm()

if __name__ == "__main__":
    pass