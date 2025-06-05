# test_assembler.py
from assembler import Arch242Assembler
import tempfile
import os

def test_assembler():
    """Test function for Arch242 assembler"""
    # Test cases with expected outputs
    test_cases = [
        # Test 1: Single-byte instructions
        {
            'name': 'Single-byte instructions',
            'code': '''
                rot-r
                rot-l
                inc
                dec
                nop
            ''',
            'expected_bin': ['00000000', '00000001', '00110001', '00111111', '00111110'],
            'expected_hex': ['00', '01', '31', '3f', '3e']
        },
        
        # Test 2: Immediate instructions
        {
            'name': 'Immediate instructions',
            'code': '''
                acc 15
                add 7
                sub 3
                and 5
                xor 9
                or 12
            ''',
            'expected_bin': ['01111111', '01000000', '00000111', '01000001', '00000011', 
                           '01000010', '00000101', '01000011', '00001001', '01000100', '00001100'],
            'expected_hex': ['7f', '40', '07', '41', '03', '42', '05', 
                           '43', '09', '44', '0c']
        },
        
        # Test 3: Memory instructions
        {
            'name': 'Memory instructions',
            'code': '''
                from-mba
                to-mba
                rarb 0x45
                rcrd 0xAB
            ''',
            'expected_bin': ['00000100', '00000101', '01010100', '00000101', '01101010', '00001011'],
            'expected_hex': ['04', '05', '54', '05', '6a', '0b']
        },
                
        # Test 4: Labels and branches
        {
            'name': 'Labels and branches',
            'code': '''
                start:
                    acc 5
                loop:
                    dec
                    bnez loop
                    b start
            ''',
            'expected_bin': ['01110101', '00111111', '10111000', '00000001', '11100000', '00000000'],
            'expected_hex': ['75', '3f', 'b8', '01', 'e0', '00']
        },

        
        # Test 5: Comments and .byte
        {
            'name': 'Comments and .byte directive',
            'code': '''
                # This is a comment
                acc 10  # Load 10
                .byte 0xFF
                .byte 0x00
                nop     # No operation
                ''',
            'expected_bin': ['01111010', '11111111', '00000000', '00111110'],
            'expected_hex': ['7a', 'ff', '00', '3e']
        },
        
        # Test 6: Two-byte shutdown
        {
            'name': 'Shutdown instruction',
            'code': '''
                    acc 1
                    shutdown
                ''',
            'expected_bin': ['01110001', '00110111', '00111110'],
            'expected_hex': ['71', '37', '3e']
        },
        
        # Test 7: Hex immediates
        {
            'name': 'Hex immediate values',
            'code': '''
                acc 0x0F
                add 0x08
                rarb 0xFF
            ''',
            'expected_bin': ['01111111', '01000000', '00001000', '01011111', '00001111'],
            'expected_hex': ['7f', '40', '08', '5f', '0f']
        },
        
        # Test 8: Complex program with calls
        {
            'name': 'Complex program with subroutines',
            'code': '''
                main:
                    acc 5
                    call subroutine
                    from-ioa
                    b end
                    
                subroutine:
                    inc
                    inc
                    ret
                    
                end:
                    nop
                    ''',
            'expected_bin': ['01110101', '11110000', '00000110', '00110000', 
                        '11100000', '00001001', '00110001', '00110001', 
                        '00101110', '00111110'],
            'expected_hex': ['75', 'f0', '06', '30', 'e0', '09', 
                        '31', '31', '2e', '3e']
        },
        
        # Test 9: Register-based instructions
        {
            'name': 'Register instructions',
            'code': '''
                inc*-reg RA
                inc*-reg RB
                inc*-reg RC
                inc*-reg RD
                inc*-reg RE
                dec*-reg RA
                dec*-reg RB
                dec*-reg RC
                dec*-reg RD
                dec*-reg RE
            ''',
            'expected_bin': ['00010000', '00010010', '00010100', '00010110', 
                           '00011000', '00010001', '00010011', '00010101', 
                           '00010111', '00011001'],
            'expected_hex': ['10', '12', '14', '16', '18', 
                           '11', '13', '15', '17', '19']
        },
        
        # Test 10: to-reg and from-reg instructions
        {
            'name': 'to-reg and from-reg instructions',
            'code': '''
                to-reg RA
                to-reg RB
                to-reg RC
                to-reg RD
                to-reg RE
                from-reg RA
                from-reg RB
                from-reg RC
                from-reg RD
                from-reg RE
            ''',
            'expected_bin': ['00100000', '00100010', '00100100', '00100110', 
                           '00101000', '00100001', '00100011', '00100101', 
                           '00100111', '00101001'],
            'expected_hex': ['20', '22', '24', '26', '28', 
                           '21', '23', '25', '27', '29']
        },
        
        # Test 11: r4 instruction
        {
            'name': 'r4 instruction',
            'code': '''
                r4 0
                r4 5
                r4 15
            ''',
            'expected_bin': ['01000110', '00000000', '01000110', '00000101', '01000110', '00001111'],
            'expected_hex': ['46', '00', '46', '05', '46', '0f']
        },
        
        # Test 12: Branch instructions
        {
            'name': 'Branch instructions',
            'code': '''
                loop:
                    bnz-a loop
                    bnz-b loop
                    beqz loop
                    bnez loop
                    beqz-cf loop
                    bnez-cf loop
                    bnz-d loop
                    b-bit 2 loop
            ''',
            'expected_bin': ['10100000', '00000000', '10101000', '00000000', 
                           '10110000', '00000000', '10111000', '00000000',
                           '11000000', '00000000', '11001000', '00000000',
                           '11011000', '00000000', '10010000', '00000000'],
            'expected_hex': ['a0', '00', 'a8', '00', 'b0', '00', 
                           'b8', '00', 'c0', '00', 'c8', '00',
                           'd8', '00', '90', '00']
        },
        
        # Test 13: Mixed register names
        {
            'name': 'Mixed case register names',
            'code': '''
                to-reg ra
                to-reg Rb
                from-reg rC
                from-reg RD
                inc*-reg re
            ''',
            'expected_bin': ['00100000', '00100010', '00100101', '00100111', '00011000'],
            'expected_hex': ['20', '22', '25', '27', '18']
        }
    ]
    
    print(f"Total test cases defined: {len(test_cases)}")  # Debug line
    
    # Run tests
    passed = 0
    failed = 0
    
    for test_num, test  in enumerate(test_cases, 1):
        print(f"\nTesting Case {test_num}: {test['name']}")
        print("-" * 40)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asm', delete=False) as f:
            f.write(test['code'])
            temp_filename = f.name
        
        try:
            # Test binary output
            assembler = Arch242Assembler()
            bin_output = assembler.assemble(temp_filename, 'bin')
            
            if bin_output == test['expected_bin']:
                print("✓ Binary output correct")
            else:
                print("✗ Binary output incorrect")
                print(test['code'])
                print(f"  Expected: {test['expected_bin']}")
                print(f"  Got:      {bin_output}")
                failed += 1
                continue
            
            # Test hex output
            assembler = Arch242Assembler()  # Reset assembler
            hex_output = assembler.assemble(temp_filename, 'hex')
            
            if hex_output == test['expected_hex']:
                print("✓ Hex output correct")
                passed += 1
            else:
                print("✗ Hex output incorrect")
                print(test['code'])
                print(f"  Expected: {test['expected_hex']}")
                print(f"  Got:      {hex_output}")
                failed += 1
                
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            failed += 1
        finally:
            # Clean up
            os.unlink(temp_filename)
    
    # Summary
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    print(f"Total tests: {len(test_cases)}")
    
    return passed == len(test_cases)

if __name__ == "__main__":
    test_assembler()