import sys
import pyxel

# display configurations
CELL_DIM = 8
NUM_ROWS = 10
NUM_COLS = 20


class Arch242Emulator:
    def __init__(self, instr_hex: list[str]):
        if len(instr_hex) > 2**16:
            sys.exit("Instructions do not fit the memory")
        
        self.isa = Arch242ISA(self)
        self.dispatch_table = {
            0x00: self.isa.rotr, 0x01: self.isa.rotl, 0x02: self.isa.rotrc,
            0x03: self.isa.rotlc, 0x04: self.isa.frommba, 0x05: self.isa.tomba,
            0x06: self.isa.frommdc, 0x07: self.isa.tomdc, 0x08: self.isa.addcmba,
            0x09: self.isa.addmba, 0x0A: self.isa.subcmba, 0x0B: self.isa.submba,
            0x0C: self.isa.incmba, 0x0D: self.isa.decmba, 0x0E: self.isa.incmdc,
            0x0F: self.isa.decmdc, 0x1A: self.isa.andba, 0x1B: self.isa.xorba,
            0x1C: self.isa.orba, 0x1D: self.isa.andmba, 0x1E: self.isa.xormba,
            0x1F: self.isa.ormba, 0x2A: self.isa.clrcf, 0x2B: self.isa.setcf,
            0x2E: self.isa.ret, 0x31: self.isa.inc, 0x32: self.isa.fromioa, 
            0x36: self.isa.bcd, 0x37: self.isa.shutdown, 0x3E: self.isa.nop,
            0x3F: self.isa.dec, 0x40: self.isa.addimm, 0x41: self.isa.subimm,
            0x42: self.isa.andimm, 0x43: self.isa.xorimm, 0x44: self.isa.orimm,
            0x46: self.isa.r4imm, 

            # R-type
            # inc*-reg 0001RRR0
            0x10: self.isa.increg, 0x12: self.isa.increg, 0x14: self.isa.increg,
            0x16: self.isa.increg, 0x18: self.isa.increg,

            # dec*-reg 0001RRR1
            0x11: self.isa.decreg, 0x13: self.isa.decreg, 0x15: self.isa.decreg,
            0x17: self.isa.decreg, 0x19: self.isa.decreg,

            # to-reg 0010RRR0
            0x20: self.isa.toreg, 0x22: self.isa.toreg, 0x24: self.isa.toreg,
            0x26: self.isa.toreg, 0x28: self.isa.toreg,

            # from-reg 0010RRR1
            0x21: self.isa.fromreg, 0x23: self.isa.fromreg, 0x25: self.isa.fromreg,
            0x27: self.isa.fromreg, 0x29: self.isa.fromreg,
        }
        self.pc = 0
        self.instr_mem = list(map(lambda x: int(x, 16), instr_hex)) # 16-bit wide
        self.data_mem = bytearray(256) # 8-bit wide

        self.reg = [0] * 5 # 4-bit wide
        self.acc = 0 # 4-bit wide
        self.cf = 0 # 1-bit register
        self.temp = 0 # 16-bit register
        self.ioa = 0 # 4-bit register

        self.running = True
        self.debugging = True
        if self.debugging:
            open("logs/debugging.txt", 'w').close()
        pyxel.init(CELL_DIM * NUM_COLS, CELL_DIM * NUM_ROWS, title="Arch242 Emulator", fps=1500)
        pyxel.run(self.update, self.draw)

    def update(self):
        if self.running and self.pc < len(self.instr_mem):
            self.read_input()
            if self.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"PC: {self.pc}\n")
            self.process_instruction(self.instr_mem[self.pc])
            if self.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"acc: {self.acc}\n")
                    f.write(f"cf: {self.cf}\n")
                    f.write(f"temp: {self.temp}\n")
                    f.write(f"registers: {self.reg}\n")
                    f.write(f"direction): {self.data_mem[0xf2]}\n")
                    f.write(F"ioa: {self.ioa}\n")
                    f.write(f"length: {self.data_mem[0x00]}\n")
                    f.write(f"head position: r: {self.data_mem[0x01]}, c: {self.data_mem[0x02]}\n")
                    f.write(f"NULL: r: {self.data_mem[0x07]}, c: {self.data_mem[0x08]}\n")
                    f.write(f"tail pointer r: 0x{self.data_mem[0xfe]}{self.data_mem[0xff]}\n")
                    f.write(f"tail pointer c: 0x{self.data_mem[0xfc]}{self.data_mem[0xfd]}\n")
                    f.write(f"0x35: {self.data_mem[0x35]}\n")
                    f.write(f"0x36: {self.data_mem[0x36]}\n")
                    f.write(f"0x34: {self.data_mem[0x34]}\n")
                    f.write(f"217: {self.data_mem[0xd9]}\n")
                    f.write(f"218: {self.data_mem[0xda]}\n")
                    
                    f.write(f"\n")

    def draw(self):
        pyxel.cls(0)
        for addr in range(192, 242):
            val = self.data_mem[addr] & 0x0F
            row = (addr - 192) // (NUM_COLS // 4)
            for bit in range(4):
                col = ((addr - 192) * 4 + bit) % 20
                if val & (1 << bit):
                    if bit == 0 and addr in [195, 200, 205, 210, 215, 220, 225, 230, 235, 240]:
                        pyxel.rect(col * CELL_DIM, row * CELL_DIM, CELL_DIM, CELL_DIM, 12)
                    elif row == self.data_mem[0xf4] and col == self.data_mem[0xf5]:
                        pyxel.rect(col * CELL_DIM, row * CELL_DIM, CELL_DIM, CELL_DIM, 8)
                    else:
                        pyxel.rect(col * CELL_DIM, row * CELL_DIM, CELL_DIM, CELL_DIM, 11)

    def read_input(self):
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_RIGHT):
            self.ioa = (int(pyxel.btn(pyxel.KEY_UP))     << 0 |
                        int(pyxel.btn(pyxel.KEY_DOWN))   << 1 |
                        int(pyxel.btn(pyxel.KEY_LEFT))   << 2 |
                        int(pyxel.btn(pyxel.KEY_RIGHT))  << 3)
            
        # if pyxel.btn(pyxel.KEY_UP):
        #     self.ioa = 1
        # elif pyxel.btn(pyxel.KEY_DOWN):
        #     self.ioa = 2
        # elif pyxel.btn(pyxel.KEY_LEFT):
        #     self.ioa = 4
        # elif pyxel.btn(pyxel.KEY_RIGHT):
        #     self.ioa = 8
        # else:
        #     self.ioa = 0

    def process_instruction(self, instr: int):
        try:
            if 0x50 <= instr <= 0x5F:
                self.isa.rarbimm()
                # print("rarbimm")
            elif 0x60 <= instr <= 0x6F:
                self.isa.rcrdimm()
                # print("rcrdimm")
            elif 0x70 <= instr <= 0x7F:
                self.isa.accimm()
                # print("accimm")
            elif 0x80 <= instr <= 0x9F:
                self.isa.bbitkimm()
                # print("bbitkimm")
            elif 0xA0 <= instr <= 0xA7:
                self.isa.bnzaimm()
                # print("bnzaimm")
            elif 0xA8 <= instr <= 0xAF:
                self.isa.bnzbimm()
                # print("bnzbimm")
            elif 0xB0 <= instr <= 0xB7:
                self.isa.beqzimm()
                # print("beqzimm")
            elif 0xB8 <= instr <= 0xBF:
                self.isa.bnezimm()
                # print("bnezimm")
            elif 0xC0 <= instr <= 0xC7:
                self.isa.beqzcfimm()
                # print("beqzcfimm")
            elif 0xC8 <= instr <= 0xCF:
                self.isa.bnezcfimm()
                # print("bnezcfimm")
            elif 0xD8 <= instr <= 0xDF:
                self.isa.bnzdimm()
                # print("bnzdimm")
            elif 0xE0 <= instr <= 0xEF:
                self.isa.bimm()
                # print("bimm")
            elif 0xF0 <= instr <= 0xFF:
                self.isa.callimm()
                # print("callimm")
            elif instr in self.dispatch_table:
                self.dispatch_table[instr]()
                # print(self.dispatch_table[instr].__name__)
            else:
                raise(KeyError)
        except (ValueError, KeyError) as e:
            sys.exit(f"Invalid Instruction: Found {e} while running instruction at {self.pc}")

class Arch242ISA:
    def __init__(self, emulator: Arch242Emulator):
        self.emu = emulator

    def rotr(self):
        self.emu.acc = ((self.emu.acc >> 1) | ((self.emu.acc & 0x01) << 3)) & 0xF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("rotr\n")

    def rotl(self):
        self.emu.acc = ((self.emu.acc << 1) | ((self.emu.acc >> 3) & 0x1)) & 0xF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("rotl\n")

    def rotrc(self):
        temp = self.emu.cf
        self.emu.cf = self.emu.acc & 0x01
        self.emu.acc = (self.emu.acc >> 1) | (temp << 3) & 0xF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("rotrc\n")

    def rotlc(self):
        temp = self.emu.cf
        self.emu.cf = self.emu.acc >> 3 & 0x01
        self.emu.acc = ((self.emu.acc << 1) | temp) & 0xF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("rotlc\n")

    def frommba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = self.emu.data_mem[addr] & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("frommba\n")

    def tomba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = self.emu.acc
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("tomba\n")

    def frommdc(self):
        addr = (self.emu.reg[3] << 4) | self.emu.reg[2]
        self.emu.acc = self.emu.data_mem[addr] & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("frommdc\n")

    def tomdc(self):
        addr = (self.emu.reg[3] << 4) | self.emu.reg[2]
        self.emu.data_mem[addr] = self.emu.acc
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("tomdc\n")

    def addcmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc += self.emu.data_mem[addr] + self.emu.cf
        self.emu.cf = 1 if self.emu.acc > 15 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("addcmba\n")

    def addmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc += self.emu.data_mem[addr]
        self.emu.cf = 1 if self.emu.acc > 15 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("addmba\n")

    def subcmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = self.emu.acc - self.emu.data_mem[addr] + self.emu.cf
        self.emu.cf = 1 if self.emu.acc < 0 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("subcmba\n")

    def submba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = self.emu.acc - self.emu.data_mem[addr]
        self.emu.cf = 1 if self.emu.acc < 0 else 0
        self.emu.acc &= 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("submba\n")

    def incmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.data_mem[addr] + 1) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("incmba\n")

    def decmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.data_mem[addr] - 1) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("decmba\n")

    def incmdc(self):
        addr = (self.emu.reg[3] << 4) | self.emu.reg[2]
        self.emu.data_mem[addr] = (self.emu.data_mem[addr] + 1) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("incmdc\n")

    def decmdc(self):
        addr = (self.emu.reg[3] << 4) | self.emu.reg[2]
        self.emu.data_mem[addr] = (self.emu.data_mem[addr] - 1) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("decmdc\n")

    def increg(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        curr_reg = (curr_instr & 0xE) >> 1
        self.emu.reg[curr_reg] = (self.emu.reg[curr_reg] + 1) & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"increg {curr_reg}\n")

    def decreg(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        curr_reg = (curr_instr & 0x0E) >> 1
        self.emu.reg[curr_reg] = (self.emu.reg[curr_reg] - 1) & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"decreg {curr_reg}\n")

    def andba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = (self.emu.acc & self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("andba\n")

    def xorba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = (self.emu.acc ^ self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("xorba\n")

    def orba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.acc = (self.emu.acc | self.emu.data_mem[addr]) & 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("orba\n")

    def andmba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.acc & self.emu.data_mem[addr]) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("andmba\n")

    def xormba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.acc ^ self.emu.data_mem[addr]) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("xormba\n")

    def ormba(self):
        addr = (self.emu.reg[1] << 4) | self.emu.reg[0]
        self.emu.data_mem[addr] = (self.emu.acc | self.emu.data_mem[addr]) & 0xFF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("ormba\n")

    def toreg(self):
        curr_reg = (self.emu.instr_mem[self.emu.pc] & 0x0E) >> 1
        self.emu.reg[curr_reg] = self.emu.acc
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"toreg {curr_reg}\n")

    def fromreg(self):
        curr_reg = (self.emu.instr_mem[self.emu.pc] & 0x0E) >> 1
        self.emu.acc = self.emu.reg[curr_reg]
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"fromreg {curr_reg}\n")

    def clrcf(self):
        self.emu.cf = 0
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("clrcf\n")

    def setcf(self):
        self.emu.cf = 1
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("setcf\n")

    def ret(self):
        self.emu.pc = (self.emu.pc & 0xF000) | (self.emu.temp & 0x0FFF)
        self.temp = 0
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("ret\n")

    def fromioa(self):
        self.emu.acc = self.emu.ioa
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("fromioa\n")

    def inc(self):
        self.emu.acc += 1
        self.emu.acc &= 0xF
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("inc\n")

    def bcd(self):
        if self.emu.acc >= 10 or self.emu.cf == 1:
            self.emu.acc += 6
            self.emu.acc &= 0x0F
            self.emu.cf = 1
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("bcd\n")

    def shutdown(self):
        if self.emu.instr_mem[self.emu.pc+1] == 0x3E:
            self.emu.running = False
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write("shutdown\n")
            pyxel.quit()
        else:
            raise KeyError

    def nop(self):
        pass

    def dec(self):
        self.emu.acc -= 1
        self.emu.acc &= 0x0F
        self.emu.pc += 1
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write("dec\n")

    def addimm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.acc = self.emu.acc + (next_instr & 0x0F)
            self.emu.acc &= 0xF
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"addimm {next_instr & 0x0F}\n")
        else:
            raise ValueError

    def subimm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.acc = self.emu.acc - (next_instr & 0x0F)
            self.emu.acc &= 0xF
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"subimm {next_instr & 0x0F}\n")
        else:
            raise ValueError
    
    def andimm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.acc = self.emu.acc & (next_instr & 0x0F)
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"andimm {next_instr & 0x0F}\n")
        else:
            raise ValueError

    def xorimm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.acc = self.emu.acc ^ (next_instr & 0x0F)
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"xorimm {next_instr & 0x0F}\n")
        else:
            raise ValueError

    def orimm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.acc = self.emu.acc | (next_instr & 0x0F)
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"orimm {next_instr & 0x0F}\n")
        else:
            raise ValueError

    def r4imm(self):
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.reg[4] = next_instr & 0x0F
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"r4imm {next_instr & 0x0F}\n")
        else:
            raise ValueError

    def rarbimm(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.reg[0] = curr_instr & 0x0F
            self.emu.reg[1] = next_instr & 0x0F
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"rarbimm {((next_instr & 0x0F) << 4) | (curr_instr & 0x0F)}\n")
        else:
            raise ValueError

    def rcrdimm(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        if not (next_instr >> 4):
            self.emu.reg[2] = curr_instr & 0x0F
            self.emu.reg[3] = next_instr & 0x0F
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"rcrdimm {((next_instr & 0x0F) << 4) | (curr_instr & 0x0F)}\n")
        else:
            raise ValueError

    def accimm(self):
        self.emu.acc = self.emu.instr_mem[self.emu.pc] & 0x0F
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"accimm {self.emu.instr_mem[self.emu.pc] & 0x0F}\n")
        self.emu.pc += 1

    def branch(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        imm = ((curr_instr & 0x07) << 8) | next_instr
        self.emu.pc = (self.emu.pc & 0xF800) | imm
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"branched to {self.emu.pc}\n")

    def bbitkimm(self):
        kk = (self.emu.instr_mem[self.emu.pc] & 0x18) >> 3
        accbitkk = (self.emu.acc >> kk) & 0x1

        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"bbitkimm kk={kk}\n")

        if accbitkk == 1:
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")

    def bnzaimm(self):
        if self.emu.reg[0] != 0: # RA is nonzero
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"bnzaimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")


    def bnzbimm(self):
        if self.emu.reg[1] != 0: # RB is nonzero
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"bnzbimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")

    def beqzimm(self):
        if self.emu.acc == 0:
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"beqzimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")

    def bnezimm(self):
        if self.emu.acc != 0:
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"bnezimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")

    def beqzcfimm(self):
        if self.emu.cf == 0:
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"beqzcfimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")


    def bnezcfimm(self):
        if self.emu.cf != 0:
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"bnezcfimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")


    def bnzdimm(self):
        if self.emu.reg[3] != 0:
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"bnzdimm\n")
            self.branch()
        else:
            self.emu.pc += 2
            if self.emu.debugging:
                with open("logs/debugging.txt", 'a') as f:
                    f.write(f"did not branch\n")


    def bimm(self):
        curr_instr = self.emu.instr_mem[self.emu.pc]
        next_instr = self.emu.instr_mem[self.emu.pc+1]
        imm = ((curr_instr & 0x0F) << 8) | next_instr
        self.emu.pc = (self.emu.pc & 0xF000) | imm

        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"bimm - jumped to {imm}\n")

    def callimm(self):
        self.emu.temp = self.emu.pc + 2
        if self.emu.debugging:
            with open("logs/debugging.txt", 'a') as f:
                f.write(f"call - saved temp to {self.emu.temp}\n")
        self.bimm()

if __name__ == "__main__":
    pass