import sys
import re

class Arch242Assembler:
    def __init__(self):
        self.instrs = {
            # instruction with reg: 17 18 25 26
            # single-byte instructions
            'rot-r': (1, [0x00],),
            'rot-l': (1, [0x01],),
            'rot-rc': (1, [0x02],),
            'rot-lc': (1, [0x03],),
            'from-mba': (1, [0x04],),
            'to-mba': (1, [0x05],),
            'from-mdc': (1, [0x06],),
            'to-mdc': (1, [0x07],),
            'addc-mba': (1, [0x08],),
            'add-mba': (1, [0x09],),
            'subc-mba': (1, [0x0A],),
            'sub-mba': (1, [0x0B],),
            'inc*-mba': (1, [0x0C],),
            'dec*-mba': (1, [0x0D],),
            'inc*-mdc': (1, [0x0E],),
            'dec*-mdc': (1, [0x0F],),
            'and-ba': (1, [0x1A],),
            'xor-ba': (1, [0x1B],),
            'or-ba': (1, [0x1C],),
            'and*-mba': (1, [0x1D],),
            'xor*-mba': (1, [0x1E],),
            'or*-mba': (1, [0x1F],),
            'clr-cf': (1, [0x2A],),
            'set-cf': (1, [0x2B],),
            # 'set-ei': (1, [0x2C],),
            # 'clr-ei': (1, [0x2D],),
            'ret': (1, [0x2E],),
            # 'retc': (1, [0x2F],),
            'from-ioa': (1, [0x32],), # changed from 'from-ioa'
            'inc': (1, [0x31],),
            # 'to-ioa': (1, [0x32],),
            # 'to-iob': (1, [0x33],),
            # 'to-ioc': (1, [0x34],),
            'bcd': (1, [0x36],),
            # 'timer-start': (1, [0x38],),
            # 'timer-end': (1, [0x39],),
            # 'from-timerl': (1, [0x3A],),
            # 'from-timerh': (1, [0x3B],),
            # 'to-timerl': (1, [0x3C],),
            # 'to-timerh': (1, [0x3D],),
            'nop': (1, [0x3E],),
            'dec': (1, [0x3F],),
            
            # two-byte instruction
            'shutdown': (2, [0x37, 0x3E])
        }

        self.labels = {}
        self.curr_address = 0

    def parse_imm(self, value: str) -> int:
        # Parse immediate value to decimal if in hex
        value = value.strip()
        match value[:2].lower():
            case '0x':
                return int(value, 16)
            case _:
                return int(value)
            
    def parse_reg(self, reg_str: str) -> int:
        try:
            reg_num = int(reg_str)
            if 0 <= reg_num <= 4:
                return reg_num
            else:
                raise ValueError(f"Invalid register number: {reg_num}")
            
        except:
            raise ValueError(f"Unknown register: {reg_str}")
        

    def encode_instructions(self, parts: list[str]):
        if not parts:
            return None
        
        instruction = parts[0].lower()

        match instruction:
            case '.byte':
                if len(parts) != 2:
                    raise ValueError("Invalid .byte")
                value = self.parse_imm(parts[1])
                if value > 255:
                    raise ValueError(f"Value too large for .byte: {value}")
                return [value]
            
            case inst if inst in self.instrs:
                return list(self.instrs[inst][1])
            
            case 'inc*-reg' | 'to-reg':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                opcode = {
                    'inc*-reg': 0x10,
                    'to-reg': 0x20,
                }

                reg = self.parse_reg(parts[1])
                return [opcode[instruction]| (reg << 1)]
            
            case 'dec*-reg'| 'from-reg':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                opcode = {
                    'dec*-reg': 0x10,
                    'from-reg': 0x20,
                }

                reg = self.parse_reg(parts[1])
                return [opcode[instruction] | (reg << 1) | 0x01]

                       
            case 'add' | 'sub' | 'and' | 'xor' | 'or' | 'r4':   # remove 'timer'
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                imm = self.parse_imm(parts[1])

                if imm > 15:
                    raise ValueError(f"Immediate value too large for {instruction}: {imm}")
                
                opcode = {
                    'add': 0x40,
                    'sub': 0x41,
                    'and': 0x42,
                    'xor': 0x43,
                    'or': 0x44,
                    'r4': 0x46,
                    # 'timer': 0x47,
                }
                return [opcode[instruction], imm]
            
            case 'acc':
                if len(parts) != 2:
                    raise ValueError("Invalid acc format")
                imm = self.parse_imm(parts[1])


                if imm > 15:
                    raise ValueError(f"Immediate value too large for acc: {imm}")
                
                return [0x70 | imm]
            
            case 'rarb' | 'rcrd':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                imm = self.parse_imm(parts[1])

                if imm > 255:
                    raise ValueError(f"Immediate value too large for {instruction}: {imm}")
                
                high = (imm >> 4) & 0x0F
                low = imm & 0x0F

                opcode = {'rarb': 0x50, 'rcrd': 0x60,}

                return [opcode[instruction] | low, high]
            
            case 'b-bit':
                if len(parts) != 3:
                    raise ValueError("Invalid b-bit format")
                
                bit = self.parse_imm(parts[1])

                if bit > 3:
                    raise ValueError(f"Invalid bit value for b-bit: {bit}")
                
                target = self.parse_imm(parts[2]) if parts[2] not in self.labels else self.labels[parts[2]]

                if target > 2047:
                    raise ValueError(f"Branch target too large: {target}")
                
                high_bits = (target >> 8) & 0x07
                low_bits = target & 0xFF

                return [0x80 | (bit << 3) | high_bits, low_bits]
            
            case 'bnz-a' | 'bnz-b' | 'beqz' | 'bnez' | 'beqz-cf' | 'bnez-cf' | 'bnz-d': # remove b-timer
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                target = self.parse_imm(parts[1]) if parts[1] not in self.labels else self.labels[parts[1]]

                if target > 2047:
                    raise ValueError(f"Branch target too large: {target}")
                
                high_bits = (target >> 8) & 0x07
                low_bits = target & 0xFF  

                opcode ={
                    'bnz-a': 0xA0,
                    'bnz-b': 0xA8,
                    'beqz': 0xB0,
                    'bnez': 0xB8,
                    'beqz-cf': 0xC0,
                    'bnez-cf': 0xC8,
                    # 'b-timer': 0xD0,
                    'bnz-d': 0xD8
                }

                return [opcode[instruction] | high_bits, low_bits]
            
            case 'b' | 'call':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                target = self.parse_imm(parts[1]) if parts[1] not in self.labels else self.labels[parts[1]]

                if target > 4095:
                    raise ValueError(f"Branch target too large: {target}")

                
                high_bits = (target >> 8) & 0x0F
                low_bits = target & 0xFF 

                opcode = {'b': 0xE0, 'call': 0xF0}

                return [opcode[instruction] | high_bits, low_bits]

            case _:
                raise ValueError(f"Unknown instruction: {instruction}")


    def get_instruction_size(self, parts: list[str]):
        if not parts:
            return 0

        instruction = parts[0].lower()

        match instruction:
            case '.byte':
                return 1

            case inst if inst in self.instrs:
                return self.instrs[inst][0]
            
            case 'add' | 'sub' | 'and' | 'xor' | 'or' | 'r4'  | 'rarb' | 'rcrd':
                return 2
            
            case 'acc' | 'inc*-reg' | 'dec*-reg' | 'to-reg' | 'from-reg':
                return 1
            
            case inst if inst.startswith('b') or inst == 'call':
                return 2
            
            case _:
                return 0
            
    def process_line(self, line: str):
        # removing comments
        comment_pos = line.find('#')
        if comment_pos >= 0:
            line = line[:comment_pos]

        line = line.strip()
        if not line:
            return None
        
        # checking for labels 
        colon_pos = line.find(':')

        if colon_pos >= 0:
            label = line[:colon_pos].strip()
            self.labels[label] = self.curr_address
            line = line[colon_pos + 1:].strip()
            if not line:
                return None
            
        parts = line.split()

        if not parts:
            return None
        
        return self.encode_instructions(parts)
    
    def assemble(self, input_file: str, output_format: str):
        # first pass, collecting labels and removing comments
        self.curr_address = 0
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()

                # handling comments
                comment_pos = line.find('#')
                if comment_pos >= 0:
                    line = line[:comment_pos]

                line = line.strip()
                if not line:
                    continue


                # handling labels
                colon_pos = line.find(':')
                if colon_pos >= 0:
                    label = line[:colon_pos].strip()
                    self.labels[label] = self.curr_address
                    line = line[colon_pos + 1:].strip()

                if line:
                    parts = line.split()
                    self.curr_address += self.get_instruction_size(parts)

        # second pass, generating code
        self.curr_address = 0
        output_bytes = []
        with open(input_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    result = self.process_line(line)
                    if result:
                        output_bytes.extend(result)
                        self.curr_address += len(result)
                except Exception as e:
                    raise ValueError(f"Error at line {line_num}: {str(e)}")
            
        match output_format:
            case 'bin':
                binary_lines = []
                for byte in output_bytes:
                    binary_lines.append(f'{byte:08b}')
                return binary_lines
                # return '\n'.join(binary_lines).encode('ascii')
            
            case 'hex':
                hex_lines = []
                for byte in output_bytes:
                    hex_lines.append(f'{byte:02x}')
                return hex_lines
                # return '\n'.join(hex_lines).encode('ascii')                         

def main():
    if len(sys.argv) != 3:
        print("Type: python assembler.py <input_file> <bin | hex>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_format = sys.argv[2].lower()

    match output_format:
        case 'bin' | 'hex':
            pass

        case _:
            print("Output format must be in bin or hex")
            sys.exit(1)
        
    assembler = Arch242Assembler()

    try:
        lines = assembler.assemble(input_file, output_format)
        output = '\n'.join(lines).encode('ascii')

        base_name = input_file.rsplit('.', 1)[0]
        output_file = f"{base_name}.{output_format}"


        with open(output_file, 'w') as f:
            f.write(output.decode('ascii'))

        print(f"Assembly successful. Output written to {output_file}")

                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    except Exception as e:
        print(f"Assembly error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


        