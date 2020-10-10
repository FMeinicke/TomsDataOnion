#!/usr/bin/env python3
#%%
from TomsDataOnion.decode import UserError
import base64
from typing import Union, Iterable, List

def log(*msg):
    """ Prints msg to stdout """
    print(*msg)
    return

class TomtelCorei69:
    def __init__(self, code: Union[bytes, Iterable[int]]):
        """
        Initialize the Tomtel Core i69 VM with the given bytecode.
        """

        self.registers = Registers()
        self.memory: List[bytearray] = bytearray(code)
        self.out_stream: bytes = b""

        self._MV_DEST_MASK = 0b00111000
        self._MV_SRC_MASK = 0b00000111

    def write_to_memory(self, value: int):
        """
        Write the value `value` to the memory location where the memory cursor
        (i.e. ptr+c) is currently at
        """
        self.memory[self.registers.ptr + self.registers.c] = value

    def read_from_memory(self) -> int:
        """
        Get the value that is located at the memory location where the memory cursor
        (i.e. ptr+c) is currently at
        """
        return self.memory[self.registers.ptr + self.registers.c]

    def run(self):
        """
        Run the Tomtel Core i69 VM with its code.
        Stops upon reading the 'HALT' instruction.
        """
        inst = Instruction(self.memory[0], self.memory[1:])
        while True:
            # log('Reading instruction', self.registers.pc)
            # 1. Read the next instruction
            inst = Instruction(self.memory[self.registers.pc], self.memory[self.registers.pc+1:])
            # 2. Increment pc register by the size of the current instruction
            self.registers.pc += inst.size
            # 3. Execute the instruction
            ## ADD a <- b
            if inst.op_name == 'ADD':
                self.registers.a = (self.registers.a + self.registers.b) % 256

            ## APTR imm8
            elif inst.op_name == 'APTR':
                self.registers.ptr += inst.operands[0] # overflow is undefined

            ## CMP
            elif inst.op_name == 'CMP':
                self.registers.f = int(self.registers.a != self.registers.b)

            ## HALT
            elif inst.op_name == 'HALT':
                break

            ## JEZ imm32
            elif inst.op_name == 'JEZ':
                if self.registers.f == 0:
                    self.registers.pc = inst.operands_to_int()

            ## JNZ imm32
            elif inst.op_name == 'JNZ':
                if self.registers.f != 0:
                    self.registers.pc = inst.operands_to_int()

            ## MV(32) {dest} <- {src}
            elif inst.op_name in ('MV', 'MV32'):
                dest = (inst.op_code & self._MV_DEST_MASK) >> 3
                src = inst.op_code & self._MV_SRC_MASK
                # log(f"{inst.op_name} from {src} to {dest}")
                if 7 not in (dest, src):
                    self.registers.move_by_index(dest, src, inst.op_name == 'MV32')
                else:
                    if dest == 7:
                        self.write_to_memory(self.registers.from_index(src, inst.op_name == 'MV32'))
                    elif src == 7:
                        self.registers.write_word_by_index(dest, self.read_from_memory())
                    else:
                        raise UserError("Something's wrong here...")

            ## MVI(32) {dest} <- {src}
            elif inst.op_name in ('MVI', 'MVI32'):
                dest = (inst.op_code & self._MV_DEST_MASK) >> 3
                imm_value = inst.operands_to_int()
                if dest != 7:
                    self.registers.move_imm_by_index(dest, imm_value, inst.op_name == 'MVI32')
                else:
                    self.write_to_memory(imm_value)

            ## OUT a
            elif inst.op_name == 'OUT':
                self.out_stream += bytes([self.registers.a])

            ## SUB a <- b
            elif inst.op_name == 'SUB':
                self.registers.a = (self.registers.a - self.registers.b + 256) % 256

            ## XOR a <- b
            elif inst.op_name == 'XOR':
                self.registers.a ^= self.registers.b

            else:
                raise UserError(f"Unknown instruction {inst}")

            # log(self.registers)


class Instruction:
    def __init__(self, op_code: int, code: Union[bytes, Iterable[int]]):
        """
        Construct a new Instruction with the op code `op_code` and the potential
        operands given in `code`. Takes only as many operands from `code` as the
        Instruction expects.
        """
        self.possible_op_codes = {
            0x01: 'HALT',
            0x02: 'OUT',

            0x21: 'JEZ',
            0x22: 'JNZ',

            0xC1: 'CMP',
            0xC2: 'ADD',
            0xC3: 'SUB',
            0xC4: 'XOR',

            0xE1: 'APTR'
        }
        self.possible_op_codes.update(dict(
            [(n, 'MV') for n in range(0x49, 0x7F)] +
            [(n, 'MVI') for n in range(0x48, 0x7F, 8)] +
            [(n, 'MV32') for n in range(0x89, 0xBF) if (n & 0b00000111) != 7]+
            [(n, 'MVI32') for n in range(0x88, 0xBF, 8)]
        ))

        self.op_code: int = op_code
        self.op_name: str = self.possible_op_codes[op_code]
        self.size: int # size = size(op_code) + size(operands); to be filled later
        self.operands: List[int] # to be filled later

        # log(['0x'+format(i, '02x')+':'+n for (i,n) in self.possible_op_codes.items()])

        if self.op_name in ('JEZ', 'JNZ', 'MVI32'):
            self.size = 5
        elif self.op_name in ('APTR', 'MVI'):
            self.size = 2
        else:
            self.size = 1

        # log(f"Instruction with code 0x{op_code:02x} expects {self.size-1} operands")

        self.operands = code[:self.size-1]

        # log(self)

    def __repr__(self):
        return f"Instruction(op_name: {self.op_name}, op_code: 0x{self.op_code:02x}, operands: {['0x'+format(o, '02x') for o in self.operands]})"

    def __str__(self):
        return repr(self)

    def operands_to_int(self) -> int:
        """
        Convert the list of operands that this Instruction has to an integer value.
        This comes in handy when the operands represent a 32 bit immediate value.
        In this case the operands are 4 8-bit integers in little-endian byte-order.
        """
        res: int = 0
        for op in self.operands[::-1]: # o through in reverse because of little-endianess
            res <<= 8 # shift by 2 bytes (8 bit)
            res += op

        return res

class Registers:
    def __init__(self):
        # 8-bit registers
        self.a: int = 0   # accumulation reg
        self.b: int = 0   # operand reg
        self.c: int = 0   # count/offset reg
        self.d: int = 0   # general purpose reg
        self.e: int = 0   # general purpose reg
        self.f: int = 0   # flags reg
        # 32-bit registers
        self.la:  int = 0 # general purpose reg
        self.lb:  int = 0 # general purpose reg
        self.lc:  int = 0 # general purpose reg
        self.ld:  int = 0 # general purpose reg
        self.ptr: int = 0 # pointer to memory
        self.pc:  int = 0 # program counter

        self.word_index_attr_map = {
            1:  'a',
            2:  'b',
            3:  'c',
            4:  'd',
            5:  'e',
            6:  'f',
            7:  'la',
            8:  'lb',
            9:  'lc',
            10: 'ld',
            11: 'ptr',
            12: 'pc'
        }

    def __repr__(self):
        return f"""Registers(a: {self.a}, b: {self.b}, c: {self.c}, d: {self.d}, e: {self.e}, f: {self.f},
              la: {self.la}, lb: {self.lb}, lc: {self.lc}, ld: {self.ld}, ptr: {self.ptr}, pc: {self.pc})"""

    def __str__(self):
        return repr(self)

    def from_index(self, index: int, is_32_bit: bool):
        """
        Get the value of the register identified by the index `index`.
        If `is_32_bit` is `True` this function operates on the 32-bit registers
        instead of the 8_bit ones
        """
        offset = 6 if is_32_bit else 0
        return getattr(self, self.word_index_attr_map[index+offset])

    def move_by_index(self, dest_index: int, src_index: int, is_32_bit: bool):
        """
        Set the value of the register identified by the index `dest_index` to
        the value of the register identified by index `src_index`.
        If `is_32_bit` is `True` this function operates on the 32-bit registers
        instead of the 8_bit ones
        """
        offset = 6 if is_32_bit else 0
        src = getattr(self, self.word_index_attr_map[src_index+offset])
        setattr(self, self.word_index_attr_map[dest_index+offset], src)

    def move_imm_by_index(self, dest_index: int, imm_value: int, is_32_bit: bool):
        """
        Set the value of the register identified by the index `dest_index` to
        the value given by `imm_value`.
        If `is_32_bit` is `True` this function operates on the 32-bit registers
        instead of the 8_bit ones
        """
        offset = 6 if is_32_bit else 0
        setattr(self, self.word_index_attr_map[dest_index+offset], imm_value)

    def write_word_by_index(self, dest_index: int, word: int):
        """
        Set the value of the register identified by the index `dest_index` to
        the value given in `word`
        """
        setattr(self, self.word_index_attr_map[dest_index], word)

def test():
    code = []
    with open("layer6_test", 'r') as file:
        for line in file.readlines():
            # get rid of leading/trailing whitespace and comments
            bytes_str = line.split('#')[0].strip().split()
            code += [int(b, base=16) for b in bytes_str]
    # log(['0x'+format(i, '02x') for i in code])
    VM = TomtelCorei69(code)
    VM.run()
    exit(0)

def decode(payload: Union[bytes, str]) -> bytes:
    print("Decoding Layer 6...")
    # test()

    result: bytes = b''
    decoded = base64.a85decode(payload, adobe=True)
    VM = TomtelCorei69(decoded)
    VM.run()
    result = VM.out_stream

    with open("layer7", "wb+") as layer_file:
        layer_file.write(result)

    return result

#%%
if __name__ == "__main__":
    with open('layer6', 'r') as payload_file:
        decode(payload_file.read())
