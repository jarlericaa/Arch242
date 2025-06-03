import sys

class Arch242Assembler:
    def __init__(self):
        self.instrs = {
            # instruction with reg, TBA since may confusion pa: 17 18 25 26
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
            'set-ei': (1, [0x2C],),
            'clr-ei': (1, [0x2D],),
            'ret': (1, [0x2E],),
            'retc': (1, [0x2F],),
            'from-pa': (1, [0x30],),
            'inc': (1, [0x31],),
            'to-ioa': (1, [0x32],),
            'to-iob': (1, [0x33],),
            'to-ioc': (1, [0x34],),
            'bcd': (1, [0x36],),
            'timer-start': (1, [0x38],),
            'timer-end': (1, [0x39],),
            'from-timerl': (1, [0x3A],),
            'from-timerh': (1, [0x3B],),
            'to-timerl': (1, [0x3C],),
            'to-timerh': (1, [0x3D],),
            'nop': (1, [0x3E],),
            'dec': (1, [0x3F],),
            
            # two-byte instruction
            'shutdown': (2, [0x37, 0x3E])
        }

        self.regs = {
            'RA': 0, 'ra': 0,
            'RB': 1, 'rb': 1,
            'RC': 2, 'rc': 2,
            'RD': 3, 'rd': 3,
            'RE': 4, 're': 4,
            'RF': 5, 'rf': 5
        }

        # self.labels = {}
        self.curr_address = 0

    def parse_imm(self, value: str) -> int:
        # Parse immediate value to decimal if in hex
        value = value.strip()
        match value[:2].lower():
            case '0x':
                return int(value, 16)
            case _:
                return int(value)
            
    def encode_instructions(self, parts: list[str]):
        if not parts:
            return None
        
        instruction = parts[0].lower()

        match instruction:
            case '.byte':
                if len(parts) != 2:
                    raise ValueError("Invalide .byte")
                value = self.parse_imm(parts[1])
                if value > 255:
                    raise ValueError(f"Value too large for .byte: {value}")
                return [value]
            
            case inst if inst in self.instrs:
                return list(self.instrs[inst][1])
            
            case 'add' | 'sub' | 'and' | 'xor' | 'or' | 'r4' | 'timer':
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
                    'timer': 0x47,
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

                return [opcode[instruction] | high, low]
            
            case 'b-bit':
                if len(parts) != 3:
                    raise ValueError("Invalid b-bit format")
                
                bit = self.parse_imm(parts[1])

                if bit > 3:
                    raise ValueError(f"Invalid bit value for b-bit: {bit}")
                
                target = self.parse_imm(parts[2]) # if parts[2] not in self.labels else self.labels[parts[2]]

                if target > 2047:
                    raise ValueError(f"Branch target too large: {target}")
                
                high_bits = (target >> 8) & 0x07
                low_bits = target & 0xFF

                return [0x80 | (bit << 3) | high_bits, low_bits]
            
            case 'bnz-a' | 'bnz-b' | 'beqz' | 'bnez' | 'beqz-cf' | 'bnez-cf' | 'b-timer' | 'bnz-d':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                target = self.parse_imm(parts[1]) # if parts[1] not in self.labels else self.labels[parts[1]]

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
                    'b-timer': 0xD0,
                    'bnz-d': 0xD8
                }

                return [opcode[instruction] | high_bits, low_bits]
            
            case 'b' | 'call':
                if len(parts) != 2:
                    raise ValueError(f"Invalid {instruction} format")
                
                target = self.parse_imm(parts[1]) # if parts[1] not in self.labels else self.labels[parts[1]]

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
            
            case 'add' | 'sub' | 'and' | 'xor' | 'or' | 'r4' | 'timer' | 'rarb' | 'rcrd':
                return 2
            
            case 'acc':
                return 1
            
            case inst if inst.startswith('b') or inst == 'call':
                return 2
            
            case _:
                return 0
            
    def process_line(self, line: str):
        parts = line.split()

        if not parts:
            return None
        
        return self.encode_instructions(parts)
    
    def assemble(self, input_file: str, output_format: str):
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
                return '\n'.join(binary_lines).encode('ascii')
            
            case 'hex':
                hex_lines = []
                for byte in output_bytes:
                    hex_lines.append(f'{byte:02x}')
                return '\n'.join(hex_lines).encode('ascii')                         

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
        output = assembler.assemble(input_file, output_format)

        base_name = input_file.rsplit('.', 1)[0]
        output_file = f"{base_name}.{output_format}"

        with open(output_file, 'w') as f:
            f.write(output.decode('ascii'))

        print(f"Assembly successful. Output writen to {output_file}")

                
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)
    
    except Exception as e:
        print(f"Assembly error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()


        